FROM python:3.9-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    LANG=fr_FR.UTF-8 \
    LANGUAGE=fr_FR:fr \
    LC_ALL=fr_FR.UTF-8

WORKDIR /app

# Dépendances système (client MariaDB/MySQL + locale + netcat pour le wait + Cairo pour pycairo/xhtml2pdf)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       default-libmysqlclient-dev \
       default-mysql-client \
       locales \
       netcat-openbsd \
       pkg-config \
       libssl-dev \
       libcairo2-dev \
       libpango1.0-dev \
       libffi-dev \
       shared-mime-info \
    && echo "fr_FR.UTF-8 UTF-8" >> /etc/locale.gen \
    && locale-gen \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x entrypoint.sh wait-for-db.sh || true

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]
CMD ["gunicorn", "delais_paiements.wsgi:application", "--bind", "0.0.0.0:8000"]


