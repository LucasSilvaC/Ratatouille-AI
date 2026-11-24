#!/bin/sh
set -eu
umask 077

if [ ! -e /data/db.sqlite ]; then
    cp /seed/db.sqlite /data/db.sqlite.tmp
    mv /data/db.sqlite.tmp /data/db.sqlite
fi

if [ -z "${DJANGO_SECRET_KEY:-}" ]; then
    if [ ! -s /data/django-secret-key ]; then
        python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())' > /data/django-secret-key.tmp
        mv /data/django-secret-key.tmp /data/django-secret-key
    fi
    DJANGO_SECRET_KEY="$(cat /data/django-secret-key)"
    export DJANGO_SECRET_KEY
fi

python manage.py migrate --noinput
exec "$@"
