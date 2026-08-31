# LiteratureAdvisor · FastAPI 容器镜像
# Phase 1 MVP 部署基线 · 2026-09-01
FROM python:3.12-slim

# 时区 + 不缓冲 stdout(便于 docker logs 实时观察)
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    TZ=Asia/Shanghai

WORKDIR /app

# 先装依赖,利用 Docker 缓存;requirements.txt 变更才重装
COPY requirements.txt .
RUN pip install -r requirements.txt

# 再拷代码(代码变动频率高于依赖)
COPY app/ ./app/
COPY data/ ./data/
COPY scripts/ ./scripts/

EXPOSE 8000

# 启动:uvicorn 单 worker 适合开发/小流量;生产建议 -w 2~4
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
