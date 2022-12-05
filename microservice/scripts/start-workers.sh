#!/bin/bash

echo "Starting the workers..."
python3 /app/microservice/core/rabbitmq/start_workers.py
