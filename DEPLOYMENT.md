# Token 计算器 - Docker 部署指南

## 概述

本文档提供了使用 Docker 部署 Token 计算器应用的详细说明。

## 文件结构

确保以下文件在项目根目录中：

```
token-count/
├── token_counter.py      # 主应用文件
├── tokenizer.json        # DeepSeek 分词器配置文件
├── tokenizer_config.json # 分词器配置文件
├── Dockerfile           # Docker 配置文件
├── requirements.txt     # Python 依赖文件
└── DEPLOYMENT.md       # 本部署指南
```

## Docker 部署步骤

### 1. 构建 Docker 镜像

```bash
docker build -t token-counter .
```

### 2. 运行 Docker 容器

```bash
# 基本运行命令
docker run -p 7860:7860 token-counter

# 后台运行命令
docker run -d -p 7860:7860 --name token-counter-app token-counter
```

### 3. 访问应用

应用启动后，可以通过以下 URL 访问：

- 本地访问: `http://localhost:7860`
- 如果部署在服务器上: `http://[服务器IP]:7860`

## 高级部署选项

### 使用 Docker Compose

创建 `docker-compose.yml` 文件：

```yaml
version: '3.8'
services:
  token-counter:
    build: .
    ports:
      - "7860:7860"
    restart: unless-stopped
    volumes:
      # 可选：挂载配置文件目录
      # - ./config:/app/config
```

运行命令：

```bash
docker-compose up -d
```

### 环境变量配置

如需自定义端口，可在运行时使用环境变量：

```bash
docker run -d -p 8080:8080 -e GRADIO_SERVER_PORT=8080 --name token-counter-app token-counter
```

## 部署注意事项

1. **端口映射**: 
   - 应用默认在容器内 7860 端口运行
   - 请确保宿主机端口未被占用

2. **资源限制**:
   ```bash
   docker run -d -p 7860:7860 --memory=1g --cpus=1 --name token-counter-app token-counter
   ```

3. **数据持久化**:
   - 如需保存用户数据，可挂载卷到 `/app/data`

4. **健康检查**:
   - 应用启动后，可以通过访问 `http://localhost:7860/` 检查是否正常运行

## 故障排除

### 构建错误

- 确保所有依赖文件存在
- 检查 `requirements.txt` 中的包名是否正确

### 运行时错误

- 检查 `tokenizer.json` 是否存在
- 确认端口映射是否正确

### 性能问题

- 检查系统资源是否足够
- 考虑增加容器的内存限制

## 更新应用

1. 更新代码后，重新构建镜像：
   ```bash
   docker build -t token-counter .
   ```

2. 停止并删除旧容器：
   ```bash
   docker stop token-counter-app
   docker rm token-counter-app
   ```

3. 运行新容器：
   ```bash
   docker run -d -p 7860:7860 --name token-counter-app token-counter
   ```

## 安全建议

- 不要在生产环境中使用默认端口，考虑使用非标准端口
- 限制容器资源使用
- 定期更新基础镜像
- 考虑添加反向代理（如 Nginx）用于生产环境