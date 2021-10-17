#!/bin/bash

source .venv/bin/activate
python -m app.import "$@"
