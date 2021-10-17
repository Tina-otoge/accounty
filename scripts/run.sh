#!/bin/bash

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
FLASK_DEBUG=1 flask run
