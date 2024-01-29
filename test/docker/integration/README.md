# Integration Tests

This directory contains integration tests for the kong-oidc plugin using Docker Compose.

## Prerequisites

- Docker and Docker Compose
- Python 3.6+
- `requests` Python package (`pip install requests`)

## Setup

### **Environment Configuration**

This integration test environment uses two different `.env` files:

1. **Root `.env` file** (for main build script):
   - Used by `bin/build-env.sh`
   - Contains Kong, database, and Keycloak configuration
   - See main README.md for setup instructions

2. **Integration test `.env` file** (for Docker Compose):
   ```bash
   cp env.example .env
   ```

### **Configure Integration Test Environment Variables** in `test/docker/integration/.env`:
   - `IP`: Your local IP address (used for Kong to Keycloak communication)
   - `KONG_HTTP_PROXY_PORT`: Kong proxy port (default: 8000)
   - `KONG_HTTP_ADMIN_PORT`: Kong admin port (default: 8001)
   - `KEYCLOAK_PORT`: Keycloak port (default: 8080)
   - Database credentials and other settings

## Running Tests

### Quick Start
```bash
./run.sh
```

### Manual Steps
1. **Start services**:
   ```bash
   docker-compose up -d
   ```

2. **Wait for services** to be ready (check logs)

3. **Run setup**:
   ```bash
   python3 setup.py
   ```

4. **Run integration tests**:
   ```bash
   python3 test_integration.py
   ```

5. **Cleanup**:
   ```bash
   docker-compose down
   ```

## Test Coverage

The integration tests cover:

- ✅ **Kong Admin API** accessibility
- ✅ **Keycloak Health** checks
- ✅ **OIDC Discovery** endpoint functionality
- ✅ **Plugin Configuration** validation
- ✅ **Protected Endpoint** redirect behavior
- ✅ **Public Endpoint** accessibility

## Services

- **Kong**: API Gateway with kong-oidc plugin
- **PostgreSQL**: Kong's database
- **Redis**: Session storage for kong-oidc
- **Keycloak**: OpenID Connect provider

## Test Flow

1. Keycloak is configured with a test client
2. Kong is configured with the kong-oidc plugin
3. A service and route are created pointing to httpbin.org
4. Tests can be run against the configured endpoints

## Troubleshooting

- **IP Address**: Make sure the `IP` variable in `.env` is set to your local IP
- **Port Conflicts**: Ensure ports 8000, 8001, 8080, 5432, 6379 are available
- **Keycloak**: Check Keycloak logs if authentication fails
- **Kong**: Check Kong logs for plugin errors

## Adding Tests

1. Add test commands to `run.sh`
2. Use the Kong admin API for configuration
3. Test against the proxy endpoints
4. Clean up resources after tests
