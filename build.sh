#!/bin/bash
echo "DATABASE_URL=${DATABASE_URL}" > .env
pip install -r requirements.txt
python -m flask db upgrade
