FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Cài cron và thư viện cần thiết
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    cron \
    curl \
    && pip install --upgrade pip

# Copy file pipeline và crontab
COPY run_pipeline.sh /app/run_pipeline.sh
COPY crontab /etc/cron.d/mycron

# Phân quyền và setup crontab
RUN chmod +x /app/run_pipeline.sh \
    && chmod 0644 /etc/cron.d/mycron \
    && crontab /etc/cron.d/mycron

# Copy requirements rồi install
COPY requirements.txt /app/
RUN pip install -r requirements.txt

# Copy toàn bộ project
COPY . /app/
