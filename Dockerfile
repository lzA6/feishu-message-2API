# --- STAGE 1: The Builder ---
# 此阶段仅用于生成 feishu_im_pb2.py 文件
FROM python:3.11-slim AS builder

WORKDIR /builder

# 从 app 目录复制 proto 文件定义
COPY app/feishu_im.proto .

RUN pip install --no-cache-dir grpcio-tools
# [修正] 将生成的 pb2 文件输出到 /builder 目录
RUN python -m grpc_tools.protoc -I. --python_out=. feishu_im.proto


# --- STAGE 2: The Final Image ---
# 此阶段构建最终的运行镜像
FROM python:3.11-slim

WORKDIR /app

# [核心修正] 将所有源文件和静态文件从本地的 app/ 目录，直接复制到容器的 /app 工作目录
# 这会创建一个扁平化的、清晰的结构，例如 /app/main.py, /app/public/index.html
COPY ./app/ .

# 将第一阶段生成的 pb2 文件，同样复制到 /app 工作目录的根部
COPY --from=builder /builder/feishu_im_pb2.py .

# 复制并安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

# [核心修正] 使用最简单的启动命令，因为 main.py 现在就在工作目录的根部
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
