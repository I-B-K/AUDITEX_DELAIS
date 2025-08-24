# Utiliser une image Python officielle comme image de base
FROM python:3.10-slim

# Empêcher Python d'écrire des fichiers .pyc
ENV PYTHONDONTWRITEBYTECODE 1
# Assurer que la sortie de Python est affichée immédiatement
ENV PYTHONUNBUFFERED 1

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Installer les dépendances système si nécessaire (ici, aucune pour l'instant)
# RUN apt-get update && apt-get install -y ...

# Copier le fichier des dépendances et les installer
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le script d'entrée et le rendre exécutable
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Copier le reste du code de l'application
COPY . .

# Collecter les fichiers statiques
RUN python manage.py collectstatic --noinput

# Exposer le port sur lequel Gunicorn va tourner
EXPOSE 8000

# Définir le point d'entrée du conteneur
ENTRYPOINT ["/entrypoint.sh"]
