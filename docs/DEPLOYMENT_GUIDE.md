# 🚀 部署指南

<div align="center">
  <h3>文件管理系统生产环境部署完整指南</h3>
  <p>从开发到生产的完整部署方案</p>
</div>

## 📋 部署概览

### 支持的部署方式

| 方式 | 适用场景 | 复杂度 | 推荐度 |
|------|----------|--------|--------|
| **Docker 容器** | 快速部署、云原生 | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| **传统服务器** | 传统环境、自建机房 | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **云平台部署** | 弹性扩展、高可用 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **K8s 集群** | 大规模、微服务 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

### 系统要求

#### 最低配置
- **CPU**: 1 核心
- **内存**: 512 MB
- **磁盘**: 1 GB (系统) + 存储空间
- **网络**: 1 Mbps

#### 推荐配置
- **CPU**: 2+ 核心
- **内存**: 2+ GB
- **磁盘**: SSD 存储
- **网络**: 10+ Mbps

#### 软件要求
- **操作系统**: Linux (Ubuntu 20.04+/CentOS 8+), Windows Server, macOS
- **Python**: 3.7+
- **数据库**: 可选 (SQLite/PostgreSQL/MySQL)
- **Web服务器**: Nginx (推荐) 或 Apache

## 🐳 Docker 部署 (推荐)

### 单容器部署

#### 1. 准备 Dockerfile

```dockerfile
# Dockerfile
FROM python:3.9-slim

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 创建应用用户
RUN useradd --create-home --shell /bin/bash filemanager

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建必要目录
RUN mkdir -p logs data/uploads && \
    chown -R filemanager:filemanager /app

# 切换到应用用户
USER filemanager

# 暴露端口
EXPOSE 8888

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8888/api/info || exit 1

# 启动命令
CMD ["python", "main.py"]
```

#### 2. 构建和运行

```bash
# 构建镜像
docker build -t file-manager:latest .

# 运行容器
docker run -d \
  --name file-manager \
  -p 8888:8888 \
  -v /host/data:/app/data \
  -v /host/logs:/app/logs \
  -e ENV=production \
  -e SECRET_KEY=$(openssl rand -hex 32) \
  --restart unless-stopped \
  file-manager:latest
```

### Docker Compose 部署

#### 创建 docker-compose.yml

```yaml
version: '3.8'

services:
  file-manager:
    build: .
    container_name: file-manager
    restart: unless-stopped
    ports:
      - "8888:8888"
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./config:/app/config
    environment:
      - ENV=production
      - DEBUG_MODE=false
      - SECRET_KEY=${SECRET_KEY}
      - SERVER_HOST=0.0.0.0
      - SERVER_PORT=8888
      - LOG_LEVEL=INFO
      - LOG_FILE=logs/production.log
    networks:
      - file-manager-network
    depends_on:
      - redis
      - postgres

  # 可选：Redis 缓存
  redis:
    image: redis:7-alpine
    container_name: file-manager-redis
    restart: unless-stopped
    volumes:
      - redis_data:/data
    networks:
      - file-manager-network

  # 可选：PostgreSQL 数据库
  postgres:
    image: postgres:15-alpine
    container_name: file-manager-db
    restart: unless-stopped
    environment:
      - POSTGRES_DB=filemanager
      - POSTGRES_USER=filemanager
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - file-manager-network

  # Nginx 反向代理
  nginx:
    image: nginx:alpine
    container_name: file-manager-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - file-manager
    networks:
      - file-manager-network

volumes:
  redis_data:
  postgres_data:

networks:
  file-manager-network:
    driver: bridge
```

#### 环境变量文件 (.env)

```bash
# .env
SECRET_KEY=your-super-secret-key-here
DB_PASSWORD=your-database-password
COMPOSE_PROJECT_NAME=filemanager
```

#### 启动服务

```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f file-manager
```

## 🖥️ 传统服务器部署

### Ubuntu/Debian 部署

#### 1. 系统准备

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装依赖
sudo apt install -y python3 python3-pip python3-venv nginx git curl

# 创建应用用户
sudo useradd -m -s /bin/bash filemanager
sudo usermod -aG sudo filemanager
```

#### 2. 应用部署

```bash
# 切换到应用用户
sudo su - filemanager

# 克隆代码
git clone <repository-url> /home/filemanager/file-manager
cd /home/filemanager/file-manager

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp env.example .env
nano .env  # 编辑配置
```

#### 3. 系统服务配置

**创建 systemd 服务文件**:

```bash
sudo tee /etc/systemd/system/file-manager.service > /dev/null <<EOF
[Unit]
Description=File Manager Service
After=network.target

[Service]
Type=simple
User=filemanager
Group=filemanager
WorkingDirectory=/home/filemanager/file-manager
Environment=PATH=/home/filemanager/file-manager/venv/bin
ExecStart=/home/filemanager/file-manager/venv/bin/python main.py
Restart=always
RestartSec=3

# 日志配置
StandardOutput=journal
StandardError=journal
SyslogIdentifier=file-manager

# 安全配置
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/home/filemanager/file-manager/logs
ReadWritePaths=/home/filemanager/file-manager/data

[Install]
WantedBy=multi-user.target
EOF
```

**启动服务**:

```bash
# 重载 systemd 配置
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start file-manager

# 设置开机自启
sudo systemctl enable file-manager

# 查看服务状态
sudo systemctl status file-manager
```

### CentOS/RHEL 部署

#### 1. 系统准备

```bash
# 更新系统
sudo yum update -y

# 安装 EPEL 仓库
sudo yum install -y epel-release

# 安装依赖
sudo yum install -y python3 python3-pip git nginx curl

# 创建应用用户
sudo useradd -m filemanager
```

#### 2. 配置防火墙

```bash
# 开放端口
sudo firewall-cmd --permanent --add-port=8888/tcp
sudo firewall-cmd --permanent --add-port=80/tcp
sudo firewall-cmd --permanent --add-port=443/tcp
sudo firewall-cmd --reload
```

### Windows Server 部署

#### 1. 环境准备

```powershell
# 安装 Python (通过 Chocolatey)
Set-ExecutionPolicy Bypass -Scope Process -Force
iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))
choco install python git -y

# 或者手动下载安装 Python 3.9+
```

#### 2. 应用部署

```powershell
# 克隆代码
git clone <repository-url> C:\FileManager
cd C:\FileManager

# 创建虚拟环境
python -m venv venv
.\venv\Scripts\Activate.ps1

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
copy env.example .env
notepad .env
```

#### 3. Windows 服务配置

**安装 NSSM (Non-Sucking Service Manager)**:

```powershell
# 下载并安装 NSSM
choco install nssm -y

# 创建服务
nssm install FileManager "C:\FileManager\venv\Scripts\python.exe"
nssm set FileManager Arguments "C:\FileManager\main.py"
nssm set FileManager AppDirectory "C:\FileManager"
nssm set FileManager Description "File Manager Web Service"

# 启动服务
nssm start FileManager
```

## ☁️ 云平台部署

### AWS 部署

#### 使用 EC2

```bash
# 启动 EC2 实例 (Amazon Linux 2)
aws ec2 run-instances \
  --image-id ami-0abcdef1234567890 \
  --instance-type t3.micro \
  --key-name your-key-pair \
  --security-groups file-manager-sg \
  --user-data file://user-data.sh
```

**user-data.sh**:
```bash
#!/bin/bash
yum update -y
yum install -y python3 git docker
systemctl start docker
systemctl enable docker
usermod -a -G docker ec2-user

# 拉取并运行容器
docker run -d \
  --name file-manager \
  -p 80:8888 \
  -v /data:/app/data \
  your-registry/file-manager:latest
```

#### 使用 ECS (Fargate)

**task-definition.json**:
```json
{
  "family": "file-manager",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "file-manager",
      "image": "your-registry/file-manager:latest",
      "portMappings": [
        {
          "containerPort": 8888,
          "protocol": "tcp"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/file-manager",
          "awslogs-region": "us-west-2",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

### Google Cloud Platform

#### 使用 Cloud Run

```bash
# 构建并推送镜像
gcloud builds submit --tag gcr.io/PROJECT-ID/file-manager

# 部署到 Cloud Run
gcloud run deploy file-manager \
  --image gcr.io/PROJECT-ID/file-manager \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars ENV=production
```

### Azure 部署

#### 使用 Container Instances

```bash
# 创建容器实例
az container create \
  --resource-group myResourceGroup \
  --name file-manager \
  --image your-registry/file-manager:latest \
  --dns-name-label file-manager-unique \
  --ports 8888 \
  --environment-variables ENV=production
```

## 🔧 Nginx 反向代理配置

### 基础配置

```nginx
# /etc/nginx/sites-available/file-manager
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    # 重定向到 HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;

    # SSL 配置
    ssl_certificate /etc/ssl/certs/your-domain.crt;
    ssl_certificate_key /etc/ssl/private/your-domain.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    # HSTS
    add_header Strict-Transport-Security "max-age=63072000" always;

    # 安全头部
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";

    # 客户端最大上传大小
    client_max_body_size 100M;

    # 代理到应用
    location / {
        proxy_pass http://127.0.0.1:8888;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket 支持 (如果需要)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # 静态文件直接服务 (优化性能)
    location /static/ {
        alias /path/to/file-manager/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # 健康检查
    location /health {
        access_log off;
        proxy_pass http://127.0.0.1:8888/api/info;
    }

    # 日志配置
    access_log /var/log/nginx/file-manager-access.log;
    error_log /var/log/nginx/file-manager-error.log;
}
```

### 负载均衡配置

```nginx
upstream file_manager_backend {
    server 127.0.0.1:8888 weight=1 max_fails=3 fail_timeout=30s;
    server 127.0.0.1:8889 weight=1 max_fails=3 fail_timeout=30s;
    # 添加更多后端服务器
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    location / {
        proxy_pass http://file_manager_backend;
        # ... 其他配置
    }
}
```

## 🔒 安全加固

### SSL/TLS 配置

#### 使用 Let's Encrypt

```bash
# 安装 Certbot
sudo apt install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# 自动续期
sudo crontab -e
# 添加: 0 12 * * * /usr/bin/certbot renew --quiet
```

#### 自签名证书 (测试用)

```bash
# 生成私钥
openssl genrsa -out server.key 2048

# 生成证书
openssl req -new -x509 -key server.key -out server.crt -days 365
```

### 防火墙配置

#### UFW (Ubuntu)

```bash
# 启用防火墙
sudo ufw enable

# 允许必要端口
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# 限制应用端口 (仅本地访问)
sudo ufw allow from 127.0.0.1 to any port 8888
```

#### firewalld (CentOS)

```bash
# 创建自定义服务
sudo firewall-cmd --permanent --new-service=file-manager
sudo firewall-cmd --permanent --service=file-manager --set-short="File Manager"
sudo firewall-cmd --permanent --service=file-manager --add-port=8888/tcp
sudo firewall-cmd --permanent --add-service=file-manager
sudo firewall-cmd --reload
```

### 系统加固

#### 应用安全

```bash
# 创建专用用户
sudo useradd -r -s /bin/false filemanager

# 设置文件权限
sudo chown -R filemanager:filemanager /path/to/app
sudo chmod -R 750 /path/to/app
sudo chmod -R 640 /path/to/app/config

# 限制进程权限
# 在 systemd 服务文件中添加:
# NoNewPrivileges=true
# PrivateTmp=true
# ProtectSystem=strict
```

#### 操作系统加固

```bash
# 禁用不必要的服务
sudo systemctl disable telnet
sudo systemctl disable ftp

# 配置 fail2ban (防暴力破解)
sudo apt install fail2ban
sudo systemctl enable fail2ban
```

## 📊 监控和日志

### 系统监控

#### Prometheus + Grafana

**docker-compose.monitoring.yml**:
```yaml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana

volumes:
  prometheus_data:
  grafana_data:
```

### 日志管理

#### 集中日志收集

```bash
# 使用 rsyslog 转发日志
echo "*.* @@log-server:514" | sudo tee -a /etc/rsyslog.conf
sudo systemctl restart rsyslog
```

#### 日志轮转

```bash
# /etc/logrotate.d/file-manager
/home/filemanager/file-manager/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 filemanager filemanager
    postrotate
        systemctl reload file-manager
    endscript
}
```

## 🔄 更新和维护

### 应用更新

#### Docker 环境

```bash
# 拉取新镜像
docker pull your-registry/file-manager:latest

# 停止当前容器
docker stop file-manager

# 删除旧容器
docker rm file-manager

# 启动新容器
docker run -d \
  --name file-manager \
  -p 8888:8888 \
  -v /host/data:/app/data \
  your-registry/file-manager:latest
```

#### 传统部署

```bash
# 备份当前版本
cp -r /home/filemanager/file-manager /home/filemanager/file-manager.backup

# 拉取更新
cd /home/filemanager/file-manager
git pull origin main

# 更新依赖
source venv/bin/activate
pip install -r requirements.txt

# 重启服务
sudo systemctl restart file-manager
```

### 备份策略

#### 数据备份

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backup/$(date +%Y%m%d)"
mkdir -p $BACKUP_DIR

# 备份应用数据
tar -czf $BACKUP_DIR/app-data.tar.gz /home/filemanager/file-manager/data

# 备份配置文件
cp /home/filemanager/file-manager/.env $BACKUP_DIR/

# 备份数据库 (如果使用)
pg_dump filemanager > $BACKUP_DIR/database.sql

# 清理旧备份 (保留30天)
find /backup -type d -mtime +30 -exec rm -rf {} \;
```

#### 自动备份

```bash
# 添加到 crontab
0 2 * * * /home/filemanager/backup.sh
```

## 🚨 故障排除

### 常见问题

#### 服务无法启动

```bash
# 检查日志
sudo journalctl -u file-manager -f

# 检查端口占用
sudo netstat -tlnp | grep 8888

# 检查权限
ls -la /home/filemanager/file-manager
```

#### 性能问题

```bash
# 检查系统资源
htop
df -h
free -h

# 检查网络连接
ss -tuln | grep 8888
```

#### 文件上传失败

```bash
# 检查磁盘空间
df -h

# 检查文件权限
ls -la /home/filemanager/file-manager/data

# 检查 Nginx 配置
nginx -t
```

### 诊断工具

#### 健康检查脚本

```bash
#!/bin/bash
# health-check.sh

echo "=== File Manager Health Check ==="

# 检查服务状态
echo "Service Status:"
systemctl is-active file-manager

# 检查端口监听
echo "Port Status:"
netstat -tlnp | grep 8888

# 检查磁盘空间
echo "Disk Usage:"
df -h /home/filemanager/file-manager

# 检查内存使用
echo "Memory Usage:"
free -h

# 测试 API
echo "API Test:"
curl -s http://localhost:8888/api/info | jq .success
```

## 📚 相关文档

- [API 参考文档](API_REFERENCE.md)
- [安全配置指南](SECURITY_GUIDE.md)
- [监控和告警](MONITORING_GUIDE.md)
- [故障排除手册](TROUBLESHOOTING.md)

---

<div align="center">
  <p><strong>🚀 部署成功！</strong></p>
  <p>如需帮助，请参考 <a href="TROUBLESHOOTING.md">故障排除手册</a> 或提交 <a href="../../issues">Issue</a></p>
  <p><em>最后更新: 2024年</em></p>
</div>
