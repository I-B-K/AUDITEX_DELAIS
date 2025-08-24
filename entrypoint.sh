#!/bin/sh

# Attendre que la base de données soit prête
# (Cette partie est simple, pour des cas plus robustes, utiliser un script comme wait-for-it.sh)
echo "Waiting for MySQL..."
while ! nc -z db 3306; do
  sleep 1
done
echo "MySQL started"

# Appliquer les migrations de la base de données
echo "Applying database migrations..."
python manage.py migrate --noinput

# Collecter les fichiers statiques
# (Déjà fait dans le Dockerfile, mais peut être utile ici si les volumes sont modifiés)
# echo "Collecting static files..."
# python manage.py collectstatic --noinput

# Démarrer le serveur Gunicorn
echo "Starting Gunicorn..."
exec "$@"
