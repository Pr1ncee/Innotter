#!/bin/bash

echo "Applying migrations..."
python manage.py migrate

echo "Creating a superuser..."
python manage.py initadmin

echo "Starting development server..."
python manage.py runserver 0.0.0.0:8000
