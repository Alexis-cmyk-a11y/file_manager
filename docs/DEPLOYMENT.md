# 🚀 快速部署指南

## 📋 前置要求

- Python 3.7+
- MySQL 5.7+
- Redis (可选，推荐)

## ⚡ 快速开始

### 1. 克隆项目
```bash
git clone <repository-url>
cd file_manager
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 配置数据库
```bash
# 编辑 config.yaml 文件
# 修改 MySQL 连接信息
```

### 4. 初始化数据库
```bash
python scripts/init_database.py
```

### 5. 启动服务
```bash
python main.py
```

### 6. 访问系统
浏览器访问: http://localhost:8888

## 🔧 环境配置

### 开发环境
```bash
export ENV=development
export REDIS_HOST=localhost
```

### 生产环境
```bash
export ENV=production
export REDIS_HOST=your-redis-server
export MYSQL_HOST=your-mysql-server
```

## 📊 健康检查

```bash
# 系统状态
curl http://localhost:8888/api/health

# 缓存状态  
curl http://localhost:8888/api/cache/status
```

## 📚 详细文档

- [技术指南](TECHNICAL_GUIDE.md) - 完整的技术文档
- [项目主页](../README.md) - 项目介绍和功能说明

---

**版本**: 2.0.0 | **更新**: 2025年1月
