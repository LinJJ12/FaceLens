"""认证与用户接口测试。"""
import json


def test_health(client):
    resp = client.get('/api/health')
    assert resp.status_code == 200
    body = resp.get_json()
    assert body['status'] == 'ok'
    assert 'available_models' in body


def test_register_login_me(client):
    resp = client.post('/api/auth/register', json={
        'username': 'alice_test',
        'email': 'alice_test@example.com',
        'password': 'secret123',
    })
    assert resp.status_code == 201
    body = resp.get_json()
    assert body['token']
    assert body['refreshToken']
    assert body['user']['username'] == 'alice_test'

    headers = {'Authorization': f"Bearer {body['token']}"}
    me = client.get('/api/auth/me', headers=headers)
    assert me.status_code == 200
    assert me.get_json()['user']['username'] == 'alice_test'


def test_register_validation(client):
    # 缺字段
    assert client.post('/api/auth/register', json={'username': 'x'}).status_code == 400
    # 用户名过短
    assert client.post('/api/auth/register', json={
        'username': 'ab', 'email': 'a@b.co', 'password': '123456'
    }).status_code == 400
    # 邮箱非法
    assert client.post('/api/auth/register', json={
        'username': 'bob_test', 'email': 'not-an-email', 'password': '123456'
    }).status_code == 400
    # 密码过短
    assert client.post('/api/auth/register', json={
        'username': 'bob_test', 'email': 'bob@example.com', 'password': '123'
    }).status_code == 400


def test_register_duplicate(client, user_token):
    _, username = user_token
    resp = client.post('/api/auth/register', json={
        'username': username,
        'email': f'{username}@example.com',
        'password': 'password123',
    })
    assert resp.status_code == 409


def test_login_wrong_password(client, user_token):
    _, username = user_token
    resp = client.post('/api/auth/login', json={'username': username, 'password': 'wrong-pass'})
    assert resp.status_code == 401


def test_login_with_email(client, user_token):
    _, username = user_token
    resp = client.post('/api/auth/login', json={
        'username': f'{username}@example.com', 'password': 'password123'
    })
    assert resp.status_code == 200


def test_refresh_token_single_use(client, user_token):
    """后端刷新令牌是一次性的：第二次刷新必须失败。"""
    _, username = user_token
    login = client.post('/api/auth/login', json={'username': username, 'password': 'password123'})
    refresh_token = login.get_json()['refreshToken']

    first = client.post('/api/auth/refresh', json={'refreshToken': refresh_token})
    assert first.status_code == 200
    assert first.get_json()['token']

    second = client.post('/api/auth/refresh', json={'refreshToken': refresh_token})
    assert second.status_code == 401


def test_change_password_and_login(client, user_token):
    token, username = user_token
    headers = {'Authorization': f'Bearer {token}'}

    resp = client.post('/api/auth/change-password', headers=headers, json={
        'oldPassword': 'password123',
        'newPassword': 'newpass456',
    })
    assert resp.status_code == 200

    # 旧密码失效
    assert client.post('/api/auth/login', json={
        'username': username, 'password': 'password123'
    }).status_code == 401
    # 新密码可登录
    assert client.post('/api/auth/login', json={
        'username': username, 'password': 'newpass456'
    }).status_code == 200


def test_password_hash_upgraded_from_legacy(app, client):
    """历史遗留的无盐 SHA-256 哈希在登录成功后应自动升级为加盐哈希。"""
    import hashlib
    from src.storage.database import db, User

    with app.app_context():
        u = User(username='legacy_user', email='legacy@example.com',
                 password_hash=hashlib.sha256(b'oldpass123').hexdigest(), role='user')
        db.session.add(u)
        db.session.commit()
        uid = u.id

    resp = client.post('/api/auth/login', json={'username': 'legacy_user', 'password': 'oldpass123'})
    assert resp.status_code == 200

    with app.app_context():
        stored = db.session.get(User, uid).password_hash
        assert stored != hashlib.sha256(b'oldpass123').hexdigest()
        assert len(stored) > 64  # pbkdf2 哈希带盐与方法前缀

    with app.app_context():
        user = db.session.get(User, uid)
        db.session.delete(user)
        db.session.commit()


def test_profile_update(client, auth_headers):
    resp = client.put('/api/auth/profile', headers=auth_headers, json={'email': 'new@example.com'})
    assert resp.status_code == 200
    assert resp.get_json()['user']['email'] == 'new@example.com'


def test_user_stats(client, auth_headers):
    resp = client.get('/api/auth/stats', headers=auth_headers)
    assert resp.status_code == 200
    stats = resp.get_json()['stats']
    assert stats['total_predictions'] == 0
    assert stats['active_days'] == 0
