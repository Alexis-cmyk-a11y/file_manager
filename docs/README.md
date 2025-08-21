# 文件管理系统 - 重构版本

## 项目概述

本项目是一个基于Flask的文件管理系统，经过重构后采用了模块化架构，提高了代码的可维护性和可扩展性。

## 架构设计

### 模块结构

```
file_manager/
├── core/                   # 核心模块
│   ├── __init__.py        # 核心模块初始化
│   ├── app.py            # 应用工厂
│   └── config.py         # 配置管理
├── api/                   # API接口模块
│   ├── __init__.py       # API模块初始化
│   └── routes/           # 路由定义
│       ├── __init__.py
│       ├── file_ops.py   # 文件操作API
│       ├── upload.py     # 上传API
│       ├── download.py   # 下载API
│       └── system.py     # 系统信息API
├── services/              # 业务逻辑服务层
│   ├── __init__.py       # 服务层初始化
│   ├── file_service.py   # 文件操作服务
│   ├── upload_service.py # 上传服务
│   ├── download_service.py # 下载服务
│   ├── security_service.py # 安全服务
│   └── system_service.py # 系统信息服务
├── utils/                 # 工具函数模块
│   ├── __init__.py       # 工具模块初始化
│   └── file_utils.py     # 文件工具类
├── models/                # 数据模型
├── middleware/            # 中间件
├── tests/                 # 测试文件
├── docs/                  # 文档
├── static/                # 静态资源
├── templates/             # 模板文件
├── main.py               # 主入口文件
└── requirements.txt       # 依赖包
```

### 架构特点

1. **分层架构**: 采用经典的三层架构（表现层、业务逻辑层、数据访问层）
2. **模块化设计**: 每个功能模块独立，便于维护和扩展
3. **服务层模式**: 业务逻辑集中在服务层，提高代码复用性
4. **工厂模式**: 使用应用工厂模式创建Flask应用实例
5. **蓝图模式**: 使用Flask蓝图组织API路由

## 核心模块说明

### Core模块
- **app.py**: 应用工厂，负责创建和配置Flask应用
- **config.py**: 配置管理，支持环境变量和环境特定配置

### API模块
- **file_ops.py**: 文件操作相关API（列表、复制、移动、删除、重命名、创建文件夹）
- **upload.py**: 文件上传API
- **download.py**: 文件下载API
- **system.py**: 系统信息API

### Services模块
- **file_service.py**: 文件操作的核心业务逻辑
- **upload_service.py**: 文件上传业务逻辑
- **download_service.py**: 文件下载业务逻辑
- **security_service.py**: 安全验证业务逻辑
- **system_service.py**: 系统信息业务逻辑

### Utils模块
- **file_utils.py**: 文件操作相关的工具函数

## 使用方法

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 运行应用
```bash
python main.py
```

### 3. 运行测试
```bash
python -m unittest tests/test_services.py
```

## 配置说明

### 环境变量
- `ROOT_DIR`: 文件管理根目录
- `SERVER_PORT`: 服务器端口
- `DEBUG_MODE`: 调试模式开关
- `ENV`: 运行环境（development/production）

### 配置文件
主要配置在 `core/config.py` 中，支持环境变量覆盖。

## 安全特性

1. **路径遍历防护**: 防止访问根目录外的文件
2. **文件类型验证**: 支持白名单和黑名单文件类型控制
3. **文件大小限制**: 可配置的单文件和总上传大小限制
4. **速率限制**: API访问频率限制
5. **输入验证**: 文件名和路径的安全验证

## 扩展指南

### 添加新的API端点
1. 在 `api/routes/` 下创建新的路由文件
2. 在 `core/app.py` 中注册新的蓝图
3. 在相应的服务层添加业务逻辑

### 添加新的服务
1. 在 `services/` 下创建新的服务类
2. 实现相应的业务逻辑
3. 在API路由中调用服务

### 添加新的工具函数
1. 在 `utils/` 下创建新的工具模块
2. 实现相应的工具函数
3. 在服务层或其他地方调用

## 测试策略

- **单元测试**: 测试各个服务类的功能
- **集成测试**: 测试API端点的功能
- **安全测试**: 测试安全防护功能

## 部署说明

### 开发环境
```bash
export ENV=development
export DEBUG_MODE=true
python main.py
```

### 生产环境
```bash
export ENV=production
export DEBUG_MODE=false
python main.py
```

## 版本历史

- **v2.0.0**: 重构版本，采用模块化架构
- **v1.x.x**: 原始单体架构版本

## 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 许可证

本项目采用MIT许可证。
