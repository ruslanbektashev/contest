FROM python:3.8-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Зависимости для mysqlclient
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    libxml2-dev \
    libxslt-dev \
  && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
COPY deploy/prod/settings.py contest

# Можно создать пользователя (не обязательно, но лучше для прод)
RUN useradd -m contest && chown -R contest /app
USER contest

# Gunicorn слушает на 8000
CMD ["gunicorn", "contest.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "60"]
