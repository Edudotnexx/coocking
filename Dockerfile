# کانفیگ یاب حرفه‌ای - Docker Image
FROM python:3.11-slim

# تنظیم متغیرهای محیطی
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# نصب ابزارهای سیستمی مورد نیاز
RUN apt-get update && apt-get install -y \
    curl \
    iputils-ping \
    net-tools \
    && rm -rf /var/lib/apt/lists/*

# ایجاد دایرکتوری کاری
WORKDIR /app

# کپی کردن فایل‌های dependency
COPY requirements.txt .

# نصب Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# کپی کردن کد برنامه
COPY . .

# ایجاد دایرکتوری logs
RUN mkdir -p logs

# ایجاد کاربر غیر‌privileged
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app
USER appuser

# نمایش پورت
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/api/health || exit 1

# اجرای برنامه
CMD ["python", "api_server.py"]
