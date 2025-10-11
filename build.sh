#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate
python fix_social_users.py  # <-- ADICIONE ESTA LINHA
python createsu.py