#!/usr/bin/env bash
set -o errexit

python -m pip install -r requirements.txt
python backend/manage.py collectstatic --no-input --settings=config.settings.prod
python backend/manage.py migrate --settings=config.settings.prod
python backend/manage.py create_admin_from_env --settings=config.settings.prod
