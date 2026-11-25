#!/bin/sh
set -eu
umask 077

if [ -z "${DJANGO_SECRET_KEY:-}" ]; then
    case "${DJANGO_PUBLIC_DEPLOYMENT:-}" in
        [Tt][Rr][Uu][Ee])
            echo "Configure uma DJANGO_SECRET_KEY forte e estável para o modo público." >&2
            exit 1
            ;;
    esac
    if [ ! -s /data/django-secret-key ]; then
        python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())' > /data/django-secret-key.tmp
        mv /data/django-secret-key.tmp /data/django-secret-key
    fi
    DJANGO_SECRET_KEY="$(cat /data/django-secret-key)"
    export DJANGO_SECRET_KEY
fi

if [ -n "${DJANGO_LEGACY_RESPONSE_ENCRYPTION_KEYS:-}" ]; then
    echo "Execute a migração legada em um processo separado da API." >&2
    exit 1
fi


python manage.py migrate --noinput
python manage.py createcachetable
python manage.py seed_catalog
exec "$@"
