FROM python:3.10-slim

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /app

COPY app/ ./app

RUN python -m grpc_tools.protoc \
    -I./app/proto \
    --python_out=./app/proto \
    --grpc_python_out=./app/proto \
    ./app/proto/products.proto

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002"]
