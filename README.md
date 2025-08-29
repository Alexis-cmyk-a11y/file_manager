# 文件管理系统

一个轻量、实用的文件管理系统。以目录隔离与硬链接共享为核心，提供上传/下载、在线编辑与简洁的共享能力。

## 主要特性

- **目录隔离**: 每个用户拥有独立的 `home/users/<username>` 工作区
- **硬链接共享**: 将文件共享到 `home/shared/<username>_shared`，只读、零拷贝
- **在线编辑**: 内置编辑器，常用文本/代码直接在线编辑
- **基础操作**: 浏览、上传、下载、重命名、删除
- **安全防护**: 路径校验、类型检查、操作日志

## 快速开始

1) 安装依赖
```bash
pip install -r requirements.txt
```

2) 初始化与启动（开发环境）
```bash
python scripts\init_database.py
python main.py
```

3) 访问
- 主页: `http://localhost:8888`
- 编辑器: `http://localhost:8888/editor`
- 共享: `http://localhost:8888/shared`

## 配置

- 配置文件位于 `config/`，按环境分层管理
- 详见: `docs/CONFIGURATION.md`

## 目录结构（核心）

```
file_manager/
├── api/           # 后端API路由
├── core/          # 应用入口与配置装载
├── services/      # 业务服务（文件/上传/共享等）
├── templates/     # 页面模板
├── static/        # 前端静态资源
├── config/        # 配置文件（development/production）
└── home/          # 用户与共享目录（运行期数据）
```

## 常见脚本

```bash
python scripts\init_database.py     # 初始化数据库
python scripts\init_simple_system.py # 初始化示例目录结构
python scripts\maintain_logs.py     # 日志清理
```

## API 速览

- 文件: `GET /api/list`, `POST /api/upload`, `GET /api/download`
- 编辑: `GET /editor`, `POST /api/editor/save`
- 共享: `POST /api/sharing/share`, `POST /api/sharing/unshare`, `GET /api/sharing/shared`

## 许可证

MIT License

——
提示: 若首次部署，请核对 `config/environment.txt` 与对应环境配置，并确保 `home/` 目录在目标系统可用（硬链接需要同一分区）。
