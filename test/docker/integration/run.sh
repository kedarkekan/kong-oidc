#!/bin/bash
set -e

# Source network functions
source ./_network_functions

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Error: .env file not found. Please copy env.example to .env and configure it."
    echo "cp env.example .env"
    exit 1
fi

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

# Set IP if not already set
if [ -z "$IP" ]; then
    export IP=$(curl -s ifconfig.me)
    echo "Using IP: $IP"
fi

echo "Starting integration tests..."

# Start services
echo "Starting Docker Compose services..."
docker-compose up -d

# Wait for services to be ready
echo "Waiting for services to be ready..."
_wait_for_endpoint "http://localhost:${KONG_HTTP_ADMIN_PORT}" 60
_wait_for_endpoint "http://localhost:${KEYCLOAK_PORT}" 60

# Run setup
echo "Setting up test environment..."
python3 setup.py

# Run tests
echo "Running integration tests..."
python3 test_integration.py

# Cleanup
echo "Cleaning up..."
docker-compose down

echo "Integration tests completed!"
