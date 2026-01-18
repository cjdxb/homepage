# Homepage 生产环境部署文档

本文档介绍如何在 Linux 服务器上部署 Homepage 项目。

## 目录

- [环境要求](#环境要求)
- [服务器准备](#服务器准备)
- [后端部署](#后端部署)
- [前端部署](#前端部署)
- [Nginx 配置](#nginx-配置)
- [Systemd 服务配置](#systemd-服务配置)
- [SSL 证书配置](#ssl-证书配置)
- [常用运维命令](#常用运维命令)
- [故障排查](#故障排查)

---

## 环境要求

| 组件 | 版本要求 |
|------|---------|
| 操作系统 | CentOS 7+ / Ubuntu 18.04+ / Debian 10+ |
| Python | 3.9+ |
| Node.js | 18.x+ |
| Nginx | 1.18+ |

## 服务器准备

### 1. 更新系统

**CentOS / RHEL:**
```bash
sudo yum update -y
sudo yum install -y epel-release
```

**Ubuntu / Debian:**
```bash
sudo apt update && sudo apt upgrade -y
```

### 2. 安装基础依赖

**CentOS / RHEL:**
```bash
sudo yum install -y git curl wget vim gcc make openssl-devel bzip2-devel libffi-devel
```

**Ubuntu / Debian:**
```bash
sudo apt install -y git curl wget vim build-essential libssl-dev zlib1g-dev \
    libbz2-dev libreadline-dev libsqlite3-dev libffi-dev
```

### 3. 安装 Python 3.9+

**CentOS / RHEL:**
```bash
sudo yum install -y python39 python39-pip python39-devel
```

**Ubuntu / Debian:**
```bash
sudo apt install -y python3 python3-pip python3-venv python3-dev
```

### 4. 安装 Node.js 18.x

```bash
# 使用 NodeSource 仓库安装
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# 或者使用 nvm（推荐）
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
source ~/.bashrc
nvm install 18
nvm use 18
```

### 5. 安装 Nginx

**CentOS / RHEL:**
```bash
sudo yum install -y nginx
```

**Ubuntu / Debian:**
```bash
sudo apt install -y nginx
```

### 6. 创建部署用户（推荐）

```bash
# 创建专用用户
sudo useradd -m -s /bin/bash homepage
sudo passwd homepage

# 创建应用目录
sudo mkdir -p /opt/homepage
sudo chown homepage:homepage /opt/homepage
```

---

## 后端部署

### 1. 上传代码

```bash
# 切换到部署用户
sudo su - homepage

# 进入应用目录
cd /opt/homepage

# 方式一：从 Git 仓库克隆（推荐）
git clone <your-repo-url> .

# 方式二：手动上传
# 使用 scp 或 sftp 将代码上传到 /opt/homepage 目录
```

### 2. 创建 Python 虚拟环境

```bash
cd /opt/homepage/backend

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 升级 pip
pip install --upgrade pip
```

### 3. 安装 Python 依赖

```bash
# 确保虚拟环境已激活
source /opt/homepage/backend/venv/bin/activate

# 安装项目依赖
pip install -r requirements.txt

# 安装 Gunicorn（生产环境 WSGI 服务器）
pip install gunicorn
```

### 4. 配置环境变量

创建环境变量文件：

```bash
vim /opt/homepage/backend/.env
```

添加以下内容：

```bash
# Flask 配置
SECRET_KEY=your-super-secret-key-change-this-in-production
FLASK_ENV=production

# Gunicorn 配置
GUNICORN_BIND=127.0.0.1:9320
GUNICORN_WORKERS=4
GUNICORN_ACCESS_LOG=/var/log/homepage/access.log
GUNICORN_ERROR_LOG=/var/log/homepage/error.log
GUNICORN_LOG_LEVEL=warning
```

> ⚠️ **重要**：请务必修改 `SECRET_KEY` 为一个随机的强密码字符串！

生成随机密钥：
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### 5. 创建日志目录

```bash
sudo mkdir -p /var/log/homepage
sudo chown homepage:homepage /var/log/homepage
```

### 6. 初始化数据库

```bash
cd /opt/homepage/backend
source venv/bin/activate

# 初始化数据库（如果是首次部署）
python3 -c "from app import db, app; app.app_context().push(); db.create_all()"
```

### 7. 测试后端服务

```bash
cd /opt/homepage/backend
source venv/bin/activate

# 测试启动
gunicorn -c gunicorn.conf.py app:app

# 测试 API（新开一个终端）
curl http://127.0.0.1:9320/api/shortcuts
```

---

## 前端部署

### 1. 安装前端依赖

```bash
cd /opt/homepage/frontend

# 安装依赖
npm install
```

### 2. 配置生产环境 API 地址

创建生产环境配置文件：

```bash
vim /opt/homepage/frontend/.env.production
```

添加以下内容（根据实际域名修改）：

```bash
# API 地址配置
# 如果前后端部署在同一域名下，使用相对路径
VITE_API_BASE_URL=

# 如果后端使用独立域名/端口，使用完整地址
# VITE_API_BASE_URL=https://api.yourdomain.com
```

### 3. 构建前端

```bash
cd /opt/homepage/frontend

# 构建生产版本
npm run build
```

构建完成后，静态文件将生成在 `dist` 目录中。

### 4. 部署静态文件

```bash
# 创建 Nginx 静态文件目录
sudo mkdir -p /var/www/homepage

# 复制构建文件
sudo cp -r /opt/homepage/frontend/dist/* /var/www/homepage/

# 设置权限
sudo chown -R nginx:nginx /var/www/homepage  # CentOS
# 或
sudo chown -R www-data:www-data /var/www/homepage  # Ubuntu/Debian
```

---

## Nginx 配置

### 1. 创建 Nginx 配置文件

```bash
sudo vim /etc/nginx/conf.d/homepage.conf
```

添加以下配置：

```nginx
# Homepage Nginx 配置

upstream backend {
    server 127.0.0.1:9320;
    keepalive 32;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;  # 修改为你的域名

    # 前端静态文件
    root /var/www/homepage;
    index index.html;

    # Gzip 压缩
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/json application/xml;

    # 静态资源缓存
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # API 代理
    location /api {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Connection "";
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }

    # Vue Router 历史模式支持
    location / {
        try_files $uri $uri/ /index.html;
    }

    # 安全头
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # 访问日志
    access_log /var/log/nginx/homepage_access.log;
    error_log /var/log/nginx/homepage_error.log;
}
```

### 2. 测试并重载 Nginx

```bash
# 测试配置
sudo nginx -t

# 重载配置
sudo systemctl reload nginx
```

---

## Systemd 服务配置

### 1. 创建后端服务文件

```bash
sudo vim /etc/systemd/system/homepage.service
```

添加以下内容：

```ini
[Unit]
Description=Homepage Backend Service
After=network.target

[Service]
Type=notify
User=homepage
Group=homepage
WorkingDirectory=/opt/homepage/backend
Environment="PATH=/opt/homepage/backend/venv/bin"
EnvironmentFile=/opt/homepage/backend/.env
ExecStart=/opt/homepage/backend/venv/bin/gunicorn -c gunicorn.conf.py app:app
ExecReload=/bin/kill -s HUP $MAINPID
ExecStop=/bin/kill -s TERM $MAINPID
Restart=always
RestartSec=5
KillMode=mixed
TimeoutStopSec=30

# 安全设置
PrivateTmp=true
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/homepage/backend /var/log/homepage

[Install]
WantedBy=multi-user.target
```

### 2. 启用并启动服务

```bash
# 重载 systemd 配置
sudo systemctl daemon-reload

# 启用开机自启
sudo systemctl enable homepage

# 启动服务
sudo systemctl start homepage

# 查看服务状态
sudo systemctl status homepage
```

---

## SSL 证书配置

### 使用 Let's Encrypt 免费证书（推荐）

#### 1. 安装 Certbot

**CentOS / RHEL:**
```bash
sudo yum install -y certbot python3-certbot-nginx
```

**Ubuntu / Debian:**
```bash
sudo apt install -y certbot python3-certbot-nginx
```

#### 2. 获取证书

```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

#### 3. 配置自动续期

```bash
# 测试续期
sudo certbot renew --dry-run

# 添加定时任务（certbot 通常会自动配置）
sudo crontab -e
# 添加：0 3 * * * /usr/bin/certbot renew --quiet
```

### 启用 SSL 后的 Nginx 配置

Certbot 会自动修改配置，但你也可以手动优化：

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 1d;

    # ... 其余配置同上 ...
}
```

---

## 常用运维命令

### 服务管理

```bash
# 启动服务
sudo systemctl start homepage

# 停止服务
sudo systemctl stop homepage

# 重启服务
sudo systemctl restart homepage

# 查看状态
sudo systemctl status homepage

# 查看日志
sudo journalctl -u homepage -f

# 重载配置（平滑重启）
sudo systemctl reload homepage
```

### Nginx 管理

```bash
# 测试配置
sudo nginx -t

# 重载配置
sudo systemctl reload nginx

# 重启 Nginx
sudo systemctl restart nginx

# 查看 Nginx 日志
tail -f /var/log/nginx/homepage_access.log
tail -f /var/log/nginx/homepage_error.log
```

### 应用日志

```bash
# 查看后端访问日志
tail -f /var/log/homepage/access.log

# 查看后端错误日志
tail -f /var/log/homepage/error.log
```

### 代码更新

```bash
# 切换到部署用户
sudo su - homepage
cd /opt/homepage

# 拉取最新代码
git pull origin main

# 更新后端依赖
cd backend
source venv/bin/activate
pip install -r requirements.txt

# 重新构建前端
cd ../frontend
npm install
npm run build
sudo cp -r dist/* /var/www/homepage/

# 重启后端服务
sudo systemctl restart homepage
```

### 数据库备份

```bash
# 备份 SQLite 数据库
cp /opt/homepage/backend/homepage.db /opt/homepage/backend/backup/homepage_$(date +%Y%m%d_%H%M%S).db

# 设置定时备份（每天凌晨3点）
crontab -e
# 添加：0 3 * * * cp /opt/homepage/backend/homepage.db /opt/homepage/backend/backup/homepage_$(date +\%Y\%m\%d).db
```

---

## 故障排查

### 1. 后端服务无法启动

```bash
# 查看详细错误日志
sudo journalctl -u homepage -n 50 --no-pager

# 手动测试启动
cd /opt/homepage/backend
source venv/bin/activate
gunicorn -c gunicorn.conf.py app:app

# 检查端口占用
sudo ss -tlnp | grep 9320
```

### 2. 502 Bad Gateway

```bash
# 检查后端服务是否运行
sudo systemctl status homepage

# 检查 Nginx 到后端的连接
curl -I http://127.0.0.1:9320/api/shortcuts

# 检查 Nginx 错误日志
tail -f /var/log/nginx/homepage_error.log
```

### 3. 前端页面空白

```bash
# 检查静态文件是否存在
ls -la /var/www/homepage/

# 检查 Nginx 配置中的 root 路径
nginx -T | grep root

# 检查浏览器控制台错误（F12）
```

### 4. API 请求失败

```bash
# 检查 CORS 配置
curl -I -X OPTIONS http://yourdomain.com/api/shortcuts

# 检查 API 响应
curl http://yourdomain.com/api/shortcuts

# 检查前端 API 地址配置
cat /var/www/homepage/assets/*.js | grep -o 'http[^"]*api[^"]*'
```

### 5. 权限问题

```bash
# 检查目录权限
ls -la /opt/homepage/
ls -la /var/www/homepage/
ls -la /var/log/homepage/

# 修复权限
sudo chown -R homepage:homepage /opt/homepage/
sudo chown -R www-data:www-data /var/www/homepage/  # Ubuntu
sudo chown -R nginx:nginx /var/www/homepage/        # CentOS
```

---

## 目录结构说明

部署完成后的目录结构：

```
/opt/homepage/                  # 应用根目录
├── backend/
│   ├── venv/                   # Python 虚拟环境
│   ├── app.py                  # Flask 应用
│   ├── gunicorn.conf.py        # Gunicorn 配置
│   ├── requirements.txt        # Python 依赖
│   ├── homepage.db             # SQLite 数据库
│   ├── .env                    # 环境变量配置
│   └── backup/                 # 数据库备份目录
├── frontend/
│   ├── src/                    # 前端源码
│   ├── dist/                   # 构建输出（构建后）
│   └── .env.production         # 前端生产环境配置

/var/www/homepage/              # Nginx 静态文件目录
├── index.html
├── assets/
└── ...

/var/log/homepage/              # 应用日志目录
├── access.log
└── error.log

/etc/nginx/conf.d/homepage.conf # Nginx 配置
/etc/systemd/system/homepage.service  # Systemd 服务配置
```

---

## 安全建议

1. **修改默认密钥**：确保 `SECRET_KEY` 使用强随机字符串
2. **防火墙配置**：只开放 80/443 端口，关闭 9320 端口的外部访问
3. **定期更新**：保持系统和依赖包的更新
4. **日志监控**：定期检查日志，配置日志轮转
5. **备份策略**：定期备份数据库和配置文件
6. **SSL/TLS**：强制使用 HTTPS

```bash
# 防火墙配置示例（Ubuntu）
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp
sudo ufw enable

# 防火墙配置示例（CentOS）
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

---

## 部署检查清单

- [ ] 服务器环境准备完成（Python、Node.js、Nginx）
- [ ] 代码已上传到服务器
- [ ] Python 虚拟环境已创建，依赖已安装
- [ ] 后端环境变量已配置（.env 文件）
- [ ] 数据库已初始化
- [ ] 前端已构建并部署到 /var/www/homepage
- [ ] Nginx 配置已完成
- [ ] Systemd 服务已配置并启用
- [ ] SSL 证书已配置（可选但推荐）
- [ ] 防火墙规则已配置
- [ ] 服务正常运行，可以正常访问
