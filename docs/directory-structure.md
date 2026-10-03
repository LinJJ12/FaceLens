# 目录结构说明

本仓库采用「运行时代码 / 运维脚本 / 文档 / 文档资源」分离的组织方式，便于维护与二次开发。

启动与使用说明见根目录 [README.md](../README.md) 与 [backend/README.md](../backend/README.md)。

## 仓库布局

```text
FaceLens/
├── README.md / LICENSE / .gitignore / .gitattributes
├── .github/
│   ├── workflows/ci.yml               # CI：后端测试矩阵 + 前端构建 + Docker 构建验证
│   ├── workflows/docker-publish.yml   # CD：镜像发布到 GitHub Container Registry
│   └── dependabot.yml                 # 依赖周更检查（pip / npm / docker / actions）
├── docker-compose.yml                 # Docker Compose 编排
├── .env.example                       # Docker 环境变量模板
├── docs/                              # 文档资源（非运行时）
│   ├── directory-structure.md
│   ├── banner.svg                     # README 顶部横幅
│   └── screenshots/                   # README 截图（dark/ 为深色主题样张）
├── training/                          # 模型训练（Notebook + 说明）
│   ├── README.md
│   ├── requirements.txt
│   └── notebooks/                     # RAF_CNN / RAF_VGG / RAF_SE
├── models/                            # 推理权重（通常 gitignore）
├── backend/
│   ├── Dockerfile                     # 推理后端镜像（非 root 运行）
│   ├── docker-entrypoint.sh           # Gunicorn 启动（on_starting 钩子内预热模型）
│   ├── gunicorn.conf.py               # Gunicorn 配置
│   ├── main.py                        # 本地启动入口
│   ├── requirements.txt / requirements-dev.txt
│   ├── pytest.ini / ruff.toml         # 测试与静态检查配置
│   ├── README.md
│   ├── src/
│   │   ├── api/                       # Flask HTTP（app、health、健康评级辅助）
│   │   ├── auth/                      # JWT 认证（pbkdf2 密码哈希）
│   │   ├── config/settings.py         # 路径 / 模型 / 密钥 / 情绪口径（单一来源）
│   │   ├── storage/                   # SQLAlchemy 模型与轻量 schema 升级
│   │   └── ml/                        # 预处理、人脸质量、视频抽帧
│   ├── scripts/                       # 迁移与运维一次性脚本（破坏性操作需显式确认）
│   ├── tests/                         # pytest 套件（无 TensorFlow 环境可运行）
│   └── data/                          # 运行时 uploads / logs / db（内容忽略）
└── frontend/
    ├── Dockerfile                     # 前端构建 + Nginx
    ├── nginx.conf                     # 静态资源与 /api 反代（视频分析长超时）
    ├── public/                        # favicon.svg；演示视频（忽略）
    ├── index.html / package.json / vite.config.js
    └── src/
        ├── pages/                     # Landing（公开落地页）+ 路由页面
        ├── api/                       # HTTP 客户端（client 含 401 单飞刷新）
        ├── utils/                     # IndexedDB、chartTheme（ECharts 双主题）等
        ├── components/ / stores/ / router/ / data/
        └── assets/
            ├── landing-preview.jpg    # 落地页界面预览
            └── styles/theme.css       # 中性灰设计令牌（浅色 / html.dark 双主题）
```

## 文档资源

| 路径 | 用途 |
|------|------|
| `docs/banner.svg` | README 顶部横幅 |
| `docs/screenshots/` | README 展示截图（深色主题） |
| `docs/screenshots/light/` | 浅色主题样张 |
| `frontend/public/favicon.svg` | 极简镜头图形 favicon |
| `frontend/src/assets/landing-preview.jpg` | 落地页界面预览图 |

## 训练与推理分工

| 目录 | 职责 |
|------|------|
| `training/` | RAF-DB 数据集上的模型训练与导出说明 |
| `models/` | 训练产出的 `.h5` / SavedModel，供 `backend` 加载推理 |
| `backend/src/ml/` | 运行时预处理、人脸质量、视频抽帧（不含训练逻辑） |

训练流程详见 [training/README.md](../training/README.md)。

## 约定

- 后端在 `backend/` 下运行：`python main.py`；业务导入形如 `from src.api.app import app`
- 配置只读 `src.config.settings`（含 `MODEL_PATHS`、`UPLOAD_FOLDER`、`DATABASE_URI`、`JWT_SECRET_KEY`、情绪分类口径）
- 上传文件相对 `backend/data/uploads/` 存库，经 `/api/uploads/<path>` 访问（JWT 可经 `?token=` 传递）
- 运维脚本：`import _bootstrap` 后再 `from src....`
- 前端 HTTP 客户端位于 `src/api/`；路由页面位于 `src/pages/`
- 前端颜色一律使用 `theme.css` 令牌（`var(--color-*)`）；ECharts 通过 `utils/chartTheme.js` 注册的主题跟随 `html.dark`
- 情绪分类口径（积极/消极/中性）与占比量纲（0-100 百分数）以后端 `settings.py` 为准，前端展示逻辑与其保持一致

## 请勿错放

- 迁移 / 修复脚本应放在 `backend/scripts/`，不要放回 `backend/` 根目录
- 页面组件使用 `pages/`，不要恢复已废弃的 `views/` 目录命名
- Axios 封装放在 `api/`，不要放回 `utils/`
- 新增硬编码颜色前先确认 `theme.css` 是否已有令牌；确需新增令牌请同时补 `html.dark` 取值
