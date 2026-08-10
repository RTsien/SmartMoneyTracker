# Docker 部署指南

## 🐳 快速开始

### 方法 1: 使用 Docker Compose（推荐）

```bash
# 构建并启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

访问: http://localhost:8001

### 方法 2: 使用 Docker 命令

```bash
# 构建镜像
docker build -t smartmoneytracker .

# 运行容器
docker run -d \
  --name smartmoneytracker \
  -p 8001:8001 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/reports:/app/reports \
  smartmoneytracker

# 查看日志
docker logs -f smartmoneytracker

# 停止容器
docker stop smartmoneytracker

# 删除容器
docker rm smartmoneytracker
```

## 📋 环境变量配置

创建 `.env` 文件（可选）：

```bash
# Tushare Token（如果有）
TUSHARE_TOKEN=your_token_here

# 其他配置
AKSHARE_ENABLED=true
```

## 🔧 高级配置

### 自定义端口

修改 `docker-compose.yml`:

```yaml
ports:
  - "8080:8001"  # 主机端口:容器端口
```

### 持久化数据

数据会自动保存到以下目录：
- `./data` - 缓存数据
- `./reports` - 分析报告

### 资源限制

在 `docker-compose.yml` 中添加：

```yaml
services:
  smartmoneytracker:
    # ... 其他配置
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

## 🛠️ 常用命令

```bash
# 重新构建镜像
docker-compose build --no-cache

# 查看运行状态
docker-compose ps

# 进入容器
docker-compose exec smartmoneytracker bash

# 查看实时日志
docker-compose logs -f --tail=100

# 重启服务
docker-compose restart

# 更新并重启
docker-compose pull
docker-compose up -d
```

## 🔍 故障排查

### 容器无法启动

```bash
# 查看详细日志
docker-compose logs smartmoneytracker

# 检查容器状态
docker-compose ps
```

### 端口被占用

```bash
# 查看端口占用
lsof -i :8001

# 修改端口
# 编辑 docker-compose.yml，修改 ports 配置
```

### 依赖安装失败

```bash
# 清理并重新构建
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## 📦 镜像管理

```bash
# 查看镜像
docker images | grep smartmoneytracker

# 删除旧镜像
docker rmi smartmoneytracker

# 清理未使用的镜像
docker image prune -a
```

## 🚀 生产环境部署

### 使用生产级 WSGI 服务器

修改 `Dockerfile` 的 CMD：

```dockerfile
# 安装 gunicorn
RUN pip install gunicorn

# 使用 gunicorn 启动
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8001", "app:app"]
```

### 反向代理（Nginx）

`nginx.conf` 示例：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### HTTPS 配置

使用 Let's Encrypt:

```bash
# 安装 certbot
sudo apt-get install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com
```

## 🔐 安全建议

1. **不要在镜像中包含敏感信息**
   - 使用环境变量或 secrets
   - 不要提交 `.env` 文件到 Git

2. **定期更新基础镜像**
   ```bash
   docker pull python:3.12-slim
   docker-compose build --no-cache
   ```

3. **使用非 root 用户运行**（可选）
   在 Dockerfile 中添加：
   ```dockerfile
   RUN useradd -m -u 1000 appuser
   USER appuser
   ```

## 📊 监控和日志

### 查看资源使用

```bash
# 实时监控
docker stats smartmoneytracker

# 查看详细信息
docker inspect smartmoneytracker
```

### 日志管理

```bash
# 限制日志大小（在 docker-compose.yml 中）
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

## 🆘 获取帮助

- 查看 [README.md](README.md) 了解项目详情
- 查看 [tests/TESTING.md](tests/TESTING.md) 了解测试
- 提交 Issue: https://github.com/rtsien/SmartMoneyTracker/issues

---

**注意**: 首次启动可能需要几分钟来下载和安装依赖。
