FROM python:3.11-slim
RUN pip install uv
WORKDIR /app
COPY pyproject.toml uv.lock* ./
RUN uv pip install --system 
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8080"]

