#!/bin/sh

# Attendre que la base de données soit prête
# (Cette partie est simple, pour des cas plus robustes, utiliser un script comme wait-for-it.sh)
DB_WAIT_HOST=${DB_HOST:-db}
DB_WAIT_PORT=${DB_PORT:-3306}
echo "Waiting for database ${DB_WAIT_HOST}:${DB_WAIT_PORT}..."
while ! nc -z "$DB_WAIT_HOST" "$DB_WAIT_PORT"; do
  sleep 1
done
echo "Database reachable"

# Appliquer les migrations de la base de données
echo "Applying database migrations..."
python manage.py migrate --noinput

# Collecter les fichiers statiques
# (Déjà fait dans le Dockerfile, mais peut être utile ici si les volumes sont modifiés)
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Démarrer le serveur Gunicorn
echo "Starting Gunicorn..."
exec "$@"
