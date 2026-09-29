FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV ETL_RAW_DATA_DIR=/app/data/raw
CMD ["python", "pipeline.py"]
