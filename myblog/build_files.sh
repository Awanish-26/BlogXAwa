#!/bin/bash
set -o errexit

uv python install 3.12
uv venv --python 3.12
source .venv/bin/activate

uv pip install -r requirements.txt
uv run python manage.py collectstatic --no-input
uv run python manage.py migrate