"""接口安全测试：认证、越权、路径穿越防护。"""


def test_protected_route_requires_token(client):
    assert client.get('/api/histories').status_code == 401
    assert client.get('/api/histories', headers={'Authorization': 'Bearer not-a-jwt'}).status_code == 401


def test_token_format_must_be_bearer(client, user_token):
    token, _ = user_token
    # 缺少 Bearer 前缀应被拒绝
    resp = client.get('/api/histories', headers={'Authorization': f'Token {token}'})
    assert resp.status_code == 401


def test_query_token_accepted_for_uploads(client, app_module, user_token, tmp_path, monkeypatch):
    """<img> 场景允许 ?token= 传递 JWT（限上传资源，且仅限本人目录）。"""
    token, username = user_token
    root = tmp_path / 'uploads'
    (root / 'predictions' / username).mkdir(parents=True)
    (root / 'predictions' / username / 'face.jpg').write_bytes(b'fake-jpeg')
    monkeypatch.setattr(app_module, 'UPLOAD_ROOT', root.resolve())

    resp = client.get(f'/api/uploads/predictions/{username}/face.jpg?token={token}')
    assert resp.status_code == 200


def test_upload_path_traversal_blocked(client, auth_headers):
    for payload in (
        '../settings.py',
        'predictions/../../settings.py',
        '..%2fsettings.py',
        '/etc/passwd',
    ):
        resp = client.get(f'/api/uploads/{payload}', headers=auth_headers)
        # 308: Werkzeug 对 "//" 的 merge_slashes 重定向，跟随后的目标同样是 404
        assert resp.status_code in (308, 400, 403, 404), payload


def test_upload_owner_only(client, app_module, tmp_path, monkeypatch):
    """普通用户只能读取自己的上传文件。"""
    root = tmp_path / 'uploads'
    (root / 'predictions' / 'owner').mkdir(parents=True)
    (root / 'predictions' / 'owner' / 'face.jpg').write_bytes(b'fake-jpeg')
    monkeypatch.setattr(app_module, 'UPLOAD_ROOT', root.resolve())

    def register(name):
        resp = client.post('/api/auth/register', json={
            'username': name, 'email': f'{name}@example.com', 'password': 'password123'
        })
        assert resp.status_code == 201
        return {'Authorization': f"Bearer {resp.get_json()['token']}"}

    owner = register('owner')
    other = register('other')

    ok = client.get('/api/uploads/predictions/owner/face.jpg', headers=owner)
    assert ok.status_code == 200

    forbidden = client.get('/api/uploads/predictions/owner/face.jpg', headers=other)
    assert forbidden.status_code == 403

    admin = client.post('/api/auth/login', json={'username': 'admin', 'password': 'admin123'})
    admin_headers = {'Authorization': f"Bearer {admin.get_json()['token']}"}
    assert client.get('/api/uploads/predictions/owner/face.jpg', headers=admin_headers).status_code == 200


def test_admin_endpoints_reject_normal_user(client, auth_headers):
    for method, path in (
        ('get', '/api/admin/users'),
        ('get', '/api/admin/histories'),
        ('post', '/api/admin/histories/clear'),
        ('get', '/api/admin/system-info'),
        ('get', '/api/admin/system-logs'),
    ):
        resp = getattr(client, method)(path, headers=auth_headers)
        assert resp.status_code == 403, path


def test_admin_can_list_users(client, admin_headers, auth_headers):
    resp = client.get('/api/admin/users', headers=admin_headers)
    assert resp.status_code == 200
    body = resp.get_json()
    assert body['total'] >= 1


def test_histories_scoped_to_owner(client, app, app_module, auth_headers):
    """普通用户历史列表只包含自己的记录。"""
    from src.storage.database import db, PredictionHistory
    import datetime

    with app.app_context():
        db.session.add(PredictionHistory(
            emotion='happy', emotion_cn='高兴', confidence=0.9,
            model_used='CNN', username='someone_else',
            created_at=datetime.datetime.now(), input_type='image',
        ))
        db.session.commit()

    resp = client.get('/api/histories', headers=auth_headers)
    assert resp.status_code == 200
    usernames = {h.get('username') for h in resp.get_json()['histories']}
    assert 'someone_else' not in usernames


def test_user_cannot_delete_others_history(client, app, app_module, auth_headers):
    from src.storage.database import db, PredictionHistory
    import datetime

    with app.app_context():
        h = PredictionHistory(
            emotion='sad', emotion_cn='悲伤', confidence=0.8,
            model_used='CNN', username='victim_user',
            created_at=datetime.datetime.now(), input_type='image',
        )
        db.session.add(h)
        db.session.commit()
        hid = h.id

    resp = client.delete(f'/api/histories/{hid}', headers=auth_headers)
    assert resp.status_code == 403

    with app.app_context():
        assert db.session.get(PredictionHistory, hid) is not None  # 未被删除
        db.session.get(PredictionHistory, hid)
        db.session.query(PredictionHistory).filter_by(username='victim_user').delete()
        db.session.commit()
