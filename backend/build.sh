#!/usr/bin/env bash
# Build script for Render deployment
# This script runs during the build phase

set -o errexit

cd backend

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate
