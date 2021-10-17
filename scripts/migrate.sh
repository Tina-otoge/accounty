#!/bin/bash

source .venv/bin/activate
alembic revision --autogenerate -m "$*"
