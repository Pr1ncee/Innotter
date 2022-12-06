#!/bin/bash

echo "Starting microservice's server..."
uvicorn core.main:app --reload --host 0.0.0.0 --port 8080
