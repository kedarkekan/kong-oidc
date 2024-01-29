# Kong OIDC Plugin

[![CI](https://github.com/kedarkekan/kong-oidc/workflows/CI/badge.svg)](https://github.com/kedarkekan/kong-oidc/actions?query=workflow%3ACI)
[![Release](https://github.com/kedarkekan/kong-oidc/workflows/Release/badge.svg)](https://github.com/kedarkekan/kong-oidc/actions?query=workflow%3ARelease)
[![Kong Version](https://img.shields.io/badge/Kong-3.9.1-fe7d37?logo=kong&logoColor=white)](https://konghq.com/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

**kong-oidc** is a plugin for [Kong](https://github.com/Mashape/kong) implementing the
[OpenID Connect](http://openid.net/specs/openid-connect-core-1_0.html) Relying Party (RP) functionality.

It authenticates users against an OpenID Connect Provider using
[OpenID Connect Discovery](http://openid.net/specs/openid-connect-discovery-1_0.html)
and the Basic Client Profile (i.e. the Authorization Code flow).

It maintains sessions for authenticated users by leveraging `lua-resty-openidc` thus offering
a configurable choice between storing the session state in a client-side browser cookie or use
in of the server-side storage mechanisms `shared-memory|memcache|redis`.

> **Note:** at the moment, there is an issue using memcached/redis, probably due to session locking: the sessions freeze. Help to debug this is appreciated. I am currently using shared memory to store sessions.

It supports server-wide caching of resolved Discovery documents and validated Access Tokens.

It can be used as a reverse proxy terminating OAuth/OpenID Connect in front of an origin server so that
the origin server/services can be protected with the relevant standards without implementing those on
the server itself.

The introspection functionality adds capability for already authenticated users and/or applications that
already possess access token to go through kong. The actual token verification is then done by Resource Server.

## Compatibility

This plugin is compatible with Kong 3.9.x and later versions. For Kong 2.x compatibility, please use version 1.4.x.

## How does it work

The diagram below shows the message exchange between the involved parties.

![alt Kong OIDC flow](docs/kong_oidc_flow.png)

The `X-Userinfo` header contains the payload from the Userinfo Endpoint

```json
X-Userinfo: {"preferred_username":"alice","id":"60f65308-3510-40ca-83f0-e9c0151cc680","sub":"60f65308-3510-40ca-83f0-e9c0151cc680"}
```

The plugin sets the authenticated credential using Kong's client API, which can be accessed by other Kong plugins:

```lua
-- Kong 3.x compatible way to access authenticated credentials
local credential = kong.client.get_credential()
if credential then
    -- credential.id contains the 'sub' field from Userinfo
    -- credential.username contains the 'preferred_username' from Userinfo
end
```

For successfully authenticated request, possible (anonymous) consumer identity set by higher priority plugin is cleared as part of setting the credentials.

The plugin will try to retrieve the user's groups from a field in the token (default `groups`) and set `kong.ctx.shared.authenticated_groups` so that Kong authorization plugins can make decisions based on the user's group membership.

## Dependencies

**kong-oidc** depends on the following packages:

- [`lua-resty-openidc`](https://github.com/zmartzone/lua-resty-openidc/) ~> 1.7.6-3
- [`lua-resty-session`](https://github.com/bungle/lua-resty-session) ~> 4.0.5
- [`lua-cjson`](https://github.com/mpx/lua-cjson) - JSON encoding/decoding
- [`lua-resty-jwt`](https://github.com/SkyLothar/lua-resty-jwt) - JWT token handling
- [`lua-resty-string`](https://github.com/openresty/lua-resty-string) - String utilities

## Installation

### Option 1: Using LuaRocks

If you're using `luarocks` execute the following:

     luarocks install kong-oidc

[Kong >= 0.14] Since `KONG_CUSTOM_PLUGINS` has been removed, you also need to set the `KONG_PLUGINS` environment variable to include besides the bundled ones, oidc

     export KONG_PLUGINS=bundled,oidc

### Option 2: Using Docker

Pre-built Docker images are available on GitHub Container Registry with support for both **Linux AMD64** and **Linux ARM64** architectures:

```bash
# Pull the latest image (auto-detects your architecture)
docker pull ghcr.io/kedarkekan/kong-oidc:latest

# Or pull a specific version
docker pull ghcr.io/kedarkekan/kong-oidc:v1.5.0

# Explicitly pull for specific architecture (recommended for consistency)
docker pull --platform linux/amd64 ghcr.io/kedarkekan/kong-oidc:latest
docker pull --platform linux/arm64 ghcr.io/kedarkekan/kong-oidc:latest

# Check your system architecture first
uname -m  # x86_64 = AMD64, arm64 = ARM64

# Run Kong with the OIDC plugin
docker run -d \
  --name kong-oidc \
  --platform linux/amd64 \  # or linux/arm64 for Apple Silicon
  -e "KONG_DATABASE=off" \
  -e "KONG_PROXY_ACCESS_LOG=/dev/stdout" \
  -e "KONG_ADMIN_ACCESS_LOG=/dev/stdout" \
  -e "KONG_PROXY_ERROR_LOG=/dev/stderr" \
  -e "KONG_ADMIN_ERROR_LOG=/dev/stderr" \
  -e "KONG_ADMIN_LISTEN=0.0.0.0:8001" \
  -e "KONG_ADMIN_GUI_URL=http://localhost:8002" \
  -p 8000:8000 \
  -p 8443:8443 \
  -p 8001:8001 \
  -p 8444:8444 \
  ghcr.io/kedarkekan/kong-oidc:latest
```

**Supported Architectures:**
- ✅ **Linux AMD64** (x86_64) - Intel/AMD processors
- ✅ **Linux ARM64** (aarch64) - Apple Silicon, ARM servers

### **Troubleshooting**

#### **"exec format error"**
If you encounter this error, it means you're trying to run an image built for a different architecture:

```bash
# Check your system architecture
uname -m

# Pull the correct architecture
docker pull --platform linux/amd64 ghcr.io/kedarkekan/kong-oidc:latest    # For Intel/AMD
docker pull --platform linux/arm64 ghcr.io/kedarkekan/kong-oidc:latest    # For Apple Silicon

# Run with explicit platform
docker run --rm --platform linux/amd64 ghcr.io/kedarkekan/kong-oidc:latest kong version
```



### Option 3: Building from Source

To build your own Docker image:

```bash
# Clone the repository
git clone https://github.com/kedarkekan/kong-oidc.git
cd kong-oidc

# Build for your local architecture
docker build -f docker/Dockerfile -t kong-oidc:local .

# Build multi-architecture image (requires docker buildx)
docker buildx build --platform linux/amd64,linux/arm64 -f docker/Dockerfile -t kong-oidc:multiarch .

# Run the image
docker run --rm kong-oidc:local kong version
```

## Usage

### Parameters

| Parameter                                   | Default                                    | Required | description                                                                                                                                                                             |
| ------------------------------------------- | ------------------------------------------ | -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `name`                                      |                                            | true     | plugin name, has to be `oidc`                                                                                                                                                           |
| `config.client_id`                          |                                            | true     | OIDC Client ID                                                                                                                                                                          |
| `config.client_secret`                      |                                            | true     | OIDC Client secret                                                                                                                                                                      |
| `config.discovery`                          | <https://.well-known/openid-configuration> | false    | OIDC Discovery Endpoint (`/.well-known/openid-configuration`)                                                                                                                           |
| `config.scope`                              | openid                                     | false    | OAuth2 Token scope. To use OIDC it has to contains the `openid` scope                                                                                                                   |
| `config.ssl_verify`                         | false                                      | false    | Enable SSL verification to OIDC Provider                                                                                                                                                |
| `config.session_secret`                     |                                            | false    | Additional parameter, which is used to encrypt the session cookie. Needs to be random                                                                                                   |
| `config.introspection_endpoint`             |                                            | false    | Token introspection endpoint                                                                                                                                                            |
| `config.timeout`                            |                                            | false    | OIDC endpoint calls timeout                                                                                                                                                             |
| `config.introspection_endpoint_auth_method` | client_secret_basic                        | false    | Token introspection authentication method. `resty-openidc` supports `client_secret_(basic\|post)`                                                                                       |
| `config.bearer_only`                        | no                                         | false    | Only introspect tokens without redirecting                                                                                                                                              |
| `config.realm`                              | kong                                       | false    | Realm used in WWW-Authenticate response header                                                                                                                                          |
| `config.logout_path`                        | /logout                                    | false    | Absolute path used to logout from the OIDC RP                                                                                                                                           |
| `config.unauth_action`                      | auth                                       | false    | What action to take when unauthenticated <br> - `auth` to redirect to the login page and attempt (re)authenticatation,<br> - `deny` to stop with 401                                    |
| `config.recovery_page_path`                 |                                            | false    | Path of a recovery page to redirect the user when error occurs (except 401). To not show any error, you can use '/' to redirect immediately home. The error will be logged server side. |
| `config.ignore_auth_filters`                |                                            | false    | A comma-separated list of endpoints to bypass authentication for                                                                                                                        |
| `config.redirect_uri`                       |                                            | false    | A relative or absolute URI the OP will redirect to after successful authentication                                                                                                      |
| `config.userinfo_header_name`               | `X-Userinfo`                               | false    | The name of the HTTP header to use when passing the UserInfo to the upstream server                                                                                                     |
| `config.id_token_header_name`               | `X-ID-Token`                               | false    | The name of the HTTP header to use when passing the ID Token to the upstream server                                                                                                     |
| `config.access_token_header_name`           | `X-Access-Token`                           | false    | The name of the HTTP header to use when passing the Access Token to the upstream server                                                                                                 |
| `config.access_token_as_bearer`             | no                                         | false    | Whether or not the access token should be passed as a Bearer token                                                                                                                      |
| `config.disable_userinfo_header`            | no                                         | false    | Disable passing the Userinfo to the upstream server                                                                                                                                     |
| `config.disable_id_token_header`            | no                                         | false    | Disable passing the ID Token to the upstream server                                                                                                                                     |
| `config.disable_access_token_header`        | no                                         | false    | Disable passing the Access Token to the upstream server                                                                                                                                 |
| `config.groups_claim`                       | groups                                     | false    | Name of the claim in the token to get groups from                                                                                                                                       |
| `config.skip_already_auth_requests`         | no                                         | false    | Ignore requests where credentials have already been set by a higher priority plugin such as basic-auth                                                                                  |
| `config.bearer_jwt_auth_enable`             | no                                         | false    | Authenticate based on JWT (ID) token provided in Authorization (Bearer) header. Checks iss, sub, aud, exp, iat (as in ID token). `config.discovery` must be defined to discover JWKS    |
| `config.bearer_jwt_auth_allowed_auds`       |                                            | false    | List of JWT token `aud` values allowed when validating JWT token in Authorization header. If not provided, uses value from `config.client_id`                                           |
| `config.bearer_jwt_auth_signing_algs`       | [ 'RS256' ]                                | false    | List of allowed signing algorithms for Authorization header JWT token validation. Must match to OIDC provider and `resty-openidc` supported algorithms                                  |
| `config.header_names`                       |                                            | false    | List of custom upstream HTTP headers to be added based on claims. Must have same number of elements as `config.header_claims`. Example: `[ 'x-oidc-email', 'x-oidc-email-verified' ]`   |
| `config.header_claims`                      |                                            | false    | List of claims to be used as source for custom upstream headers. Claims are sourced from Userinfo, ID Token, Bearer JWT, Introspection, depending on auth method.  Use only claims containing simple string values. Example: `[ 'email', 'email_verified'` |
| `config.http_proxy` || false | http proxy url |
| `config.https_proxy` || false | https proxy url (only supports url format __http__://proxy and not __https__://proxy) |

### Enabling kong-oidc

To enable the plugin only for one API:

```http
POST /apis/<api_id>/plugins/ HTTP/1.1
Host: localhost:8001
Content-Type: application/x-www-form-urlencoded
Cache-Control: no-cache

name=oidc&config.client_id=kong-oidc&config.client_secret=29d98bf7-168c-4874-b8e9-9ba5e7382fa0&config.discovery=https%3A%2F%2F<oidc_provider>%2F.well-known%2Fopenid-configuration
```

To enable the plugin globally:

```http
POST /plugins HTTP/1.1
Host: localhost:8001
Content-Type: application/x-www-form-urlencoded
Cache-Control: no-cache

name=oidc&config.client_id=kong-oidc&config.client_secret=29d98bf7-168c-4874-b8e9-9ba5e7382fa0&config.discovery=https%3A%2F%2F<oidc_provider>%2F.well-known%2Fopenid-configuration
```

A successful response:

```http
HTTP/1.1 201 Created
Date: Tue, 24 Oct 2017 19:37:38 GMT
Content-Type: application/json; charset=utf-8
Transfer-Encoding: chunked
Connection: keep-alive
Access-Control-Allow-Origin: *
Server: kong/3.9.1

{
    "created_at": 1508871239797,
    "config": {
        "response_type": "code",
        "client_id": "kong-oidc",
        "discovery": "https://<oidc_provider>/.well-known/openid-configuration",
        "scope": "openid",
        "ssl_verify": "no",
        "client_secret": "29d98bf7-168c-4874-b8e9-9ba5e7382fa0",
        "token_endpoint_auth_method": "client_secret_post"
    },
    "id": "58cc119b-e5d0-4908-8929-7d6ed73cb7de",
    "enabled": true,
    "name": "oidc",
    "api_id": "32625081-c712-4c46-b16a-5d6ed73cb8f0"
}
```

### Upstream API request

For successfully authenticated request, the plugin will set upstream header `X-Credential-Identifier` to contain `sub` claim from user info, ID token or introspection result. Header `X-Anonymous-Consumer` is cleared.

The plugin adds a additional `X-Userinfo`, `X-Access-Token` and `X-Id-Token` headers to the upstream request, which can be consumer by upstream server. All of them are base64 encoded:

```http
GET / HTTP/1.1
Host: netcat:9000
Connection: keep-alive
X-Forwarded-For: 172.19.0.1
X-Forwarded-Proto: http
X-Forwarded-Host: localhost
X-Forwarded-Port: 8000
X-Real-IP: 172.19.0.1
Cache-Control: max-age=0
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36
Upgrade-Insecure-Requests: 1
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8
Accept-Encoding: gzip, deflate
Accept-Language: pl-PL,pl;q=0.8,en-US;q=0.6,en;q=0.4
Cookie: session=KOn1am4mhQLKazlCA.....
X-Userinfo: eyJnaXZlbl9uYW1lIjoixITEmMWaw5PFgcW7xbnEhiIsInN1YiI6ImM4NThiYzAxLTBiM2ItNDQzNy1hMGVlLWE1ZTY0ODkwMDE5ZCIsInByZWZlcnJlZF91c2VybmFtZSI6ImFkbWluIiwibmFtZSI6IsSExJjFmsOTxYHFu8W5xIYiLCJ1c2VybmFtZSI6ImFkbWluIiwiaWQiOiJjODU4YmMwMS0wYjNiLTQ0MzctYTBlZS1hNWU2NDg5MDAxOWQifQ==
X-Access-Token: eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJGenFSY0N1Ry13dzlrQUJBVng1ZG9sT2ZwTFhBNWZiRGFlVDRiemtnSzZRIn0.eyJqdGkiOiIxYjhmYzlkMC1jMjlmLTQwY2ItYWM4OC1kNzMyY2FkODcxY2IiLCJleHAiOjE1NDg1MTA4MjksIm5iZiI6MCwiaWF0IjoxNTQ4NTEwNzY5LCJpc3MiOiJodHRwOi8vMTkyLjE2OC4wLjk6ODA4MC9hdXRoL3JlYWxtcy9tYXN0ZXIiLCJhdWQiOlsibWFzdGVyLXJlYWxtIiwiYWNjb3VudCJdLCJzdWIiOiJhNmE3OGQ5MS01NDk0LTRjZTMtOTU1NS04NzhhMTg1Y2E0YjkiLCJ0eXAiOiJCZWFyZXIiLCJhenAiOiJrb25nIiwibm9uY2UiOiJmNGRkNDU2YzBjZTY4ZmFmYWJmNGY4ZDA3YjQ0YWE4NiIsImF1dGhfdGltZSI6…IiwibWFuYWdlLWFjY291bnQtbGlua3MiLCJ2aWV3LXByb2ZpbGUiXX19LCJzY29wZSI6Im9wZW5pZCBwcm9maWxlIGVtYWlsIiwiZW1haWxfdmVyaWZpZWQiOmZhbHNlLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJhZG1pbiJ9.GWuguFjSEDGxw_vbD04UMKxtai15BE2lwBO0YkSzp-NKZ2SxAzl0nyhZxpP0VTzk712nQ8f_If5-mQBf_rqEVnOraDmX5NOXP0B8AoaS1jsdq4EomrhZGqlWmuaV71Cnqrw66iaouBR_6Q0s8bgc1FpCPyACM4VWs57CBdTrAZ2iv8dau5ODkbEvSgIgoLgBbUvjRKz1H0KyeBcXlVSgHJ_2zB9q2HvidBsQEIwTP8sWc6er-5AltLbV8ceBg5OaZ4xHoramMoz2xW-ttjIujS382QQn3iekNByb62O2cssTP3UYC747ehXReCrNZmDA6ecdnv8vOfIem3xNEnEmQw
X-Id-Token: eyJuYmYiOjAsImF6cCI6ImtvbmciLCJpYXQiOjE1NDg1MTA3NjksImlzcyI6Imh0dHA6XC9cLzE5Mi4xNjguMC45OjgwODBcL2F1dGhcL3JlYWxtc1wvbWFzdGVyIiwiYXVkIjoia29uZyIsIm5vbmNlIjoiZjRkZDQ1NmMwY2U2OGZhZmFiZjRmOGQwN2I0NGFhODYiLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJhZG1pbiIsImF1dGhfdGltZSI6MTU0ODUxMDY5NywiYWNyIjoiMSIsInNlc3Npb25fc3RhdGUiOiJiNDZmODU2Ny0zODA3LTQ0YmMtYmU1Mi1iMTNiNWQzODI5MTQiLCJleHAiOjE1NDg1MTA4MjksImVtYWlsX3ZlcmlmaWVkIjpmYWxzZSwianRpIjoiMjI1ZDRhNDItM2Y3ZC00Y2I2LTkxMmMtOGNkYzM0Y2JiNTk2Iiwic3ViIjoiYTZhNzhkOTEtNTQ5NC00Y2UzLTk1NTUtODc4YTE4NWNhNGI5IiwidHlwIjoiSUQifQ==
```

### Standard OpenID Connect Scopes and Claims

The OpenID Connect Core 1.0 profile specifies the following standard scopes and claims:

| Scope     | Claim(s)                                                                                                                               |
| --------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| `openid`  | `sub`. In an ID Token, `iss`, `aud`, `exp`, `iat` will also be provided.                                                               |
| `profile` | Typically claims like `name`, `family_name`, `given_name`, `middle_name`, `preferred_username`, `nickname`, `picture` and `updated_at` |
| `email`   | `email` and `email_verified` (_boolean_) indicating if the email address has been verified by the user                                 |

_Note that the `openid` scope is a mandatory designator scope._

#### Description of the standard claims

| Claim                | Type           | Description                                                                                                                                                 |
| -------------------- | -------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `iss`                | URI            | The Uniform Resource Identifier uniquely identifying the OpenID Connect Provider (_OP_)                                                                     |
| `aud`                | string / array | The intended audiences. For ID tokens, the identity token is one or more clients. For Access tokens, the audience is typically one or more Resource Servers |
| `nbf`                | integer        | _Not before_ timestamp in Unix Epoch time\*. May be omitted or set to 0 to indicate that the audience can disregard the claim                               |
| `exp`                | integer        | _Expires_ timestamp in Unix Epoch time\*                                                                                                                    |
| `name`               | string         | Preferred display name. Ex. `John Doe`                                                                                                                      |
| `family_name`        | string         | Last name. Ex. `Doe`                                                                                                                                        |
| `given_name`         | string         | First name. Ex. `John`                                                                                                                                      |
| `middle_name`        | string         | Middle name. Ex. `Donald`                                                                                                                                   |
| `nickname`           | string         | Nick name. Ex. `Johnny`                                                                                                                                     |
| `preferred_username` | string         | Preferred user name. Ex. `johdoe`                                                                                                                           |
| `picture`            | base64         | A Base-64 encoded picture (typically PNG or JPEG) of the subject                                                                                            |
| `updated_at`         | integer        | A timestamp in Unix Epoch time\*                                                                                                                            |

`*` (Seconds since January 1st 1970).

### Passing the Access token as a normal Bearer token

To pass the access token to the upstream server as a normal Bearer token, configure the plugin as follows:

| Key                                    | Value           |
| -------------------------------------- | --------------- |
| `config.access_token_header_name`      | `Authorization` |
| `config.access_token_as_bearer`        | `yes`           |

## Development

### Code Quality and Linting

This project uses `luacheck` for code quality analysis. The linting is configured to be informative but not blocking:

```shell
# Run linting locally
./bin/lint.sh

# Or run directly
luacheck kong/ test/ --no-max-line-length --no-fail-on-warnings
```

**Linting Philosophy:**
- ✅ **Kong plugin files**: Must be clean (0 critical warnings)
- ⚠️ **Test files**: Expected warnings are acceptable
- 📊 **Current status**: ~80 warnings total (mostly expected test patterns)

**Expected Warning Categories:**
- `unused argument self` - Standard in Lua object methods
- `unused argument opts` - Expected in test mocks
- `unused variable length argument` - Expected in mock functions

These warnings don't affect functionality and are standard patterns in Lua testing environments.

### Running Unit Tests

#### **Local Testing**
To run tests locally, use the provided script:
```bash
./bin/test-local.sh
```

This script will:
- ✅ Check for required dependencies (Lua, LuaRocks)
- ✅ Install missing test dependencies automatically
- ✅ Run all unit tests with coverage

#### **Manual Testing**
If you prefer to run tests manually:
```bash
# Install test dependencies
luarocks install lua-cjson luaunit luacov lua-resty-jwt lua-resty-string lua-resty-session classic

# Run tests
lua -lluacov test/unit/test_utils.lua -o TAP --failure
```

**Note:** All `lua-resty-*` modules and Kong plugin modules require the OpenResty/Nginx environment to run properly. They may not load in standalone Lua but will work correctly within Kong. Only `lua-cjson` works in standalone Lua environments.

#### **Docker Testing**
To run tests in a Docker environment:
```bash
./bin/run-unit-tests.sh
```

This may take a while for the first run, as the docker image will need to be built, but subsequent runs will be quick.

### Continuous Integration

This project uses GitHub Actions for continuous integration:

- **Tests**: Runs on Kong 3.9.1
- **Linting**: Uses luacheck for code quality (non-blocking)
- **Docker**: Builds and tests Docker images

View the latest CI status: [![CI](https://github.com/kedarkekan/kong-oidc/workflows/CI/badge.svg)](https://github.com/kedarkekan/kong-oidc/actions?query=workflow%3ACI)

### Building the Integration Test Environment

To build the integration environment (Kong with the oidc plugin enabled, and Keycloak as the OIDC Provider), you will need to set up environment variables and run the build script.

#### **Option 1: Using Environment Variables**
```shell
export IP=192.168.0.1
export KONG_BASE_TAG=:3.9.1
export KONG_DB_TAG=:10.1
./bin/build-env.sh
```

#### **Option 2: Using .env File (Recommended)**
The project includes a pre-configured `.env` file with Kong 3.9.1 settings. You may need to update the `IP` variable to match your local network:

1. **Update IP address** (if needed):
   ```bash
   # Edit .env file and set your local IP
   sed -i 's/IP=.*/IP=192.168.0.1/' .env  # Replace with your IP
   ```

2. **Run the build script**:
   ```shell
   ./bin/build-env.sh
   ```

#### **Tear Down Environment**
```shell
./bin/teardown-env.sh
```

## Release Process

### Versioning Strategy

This project follows [Semantic Versioning](https://semver.org/) (SemVer) with manual version control:

- **Patch releases** (`1.5.0` → `1.5.1`): Bug fixes and minor improvements
- **Minor releases** (`1.5.0` → `1.6.0`): New features, backward compatible
- **Major releases** (`1.5.0` → `2.0.0`): Breaking changes
- **Build releases** (`1.5.0-0` → `1.5.0-1`): Build-specific releases

### Automated Release Workflow

The release process is fully automated through GitHub Actions:

1. **Manual Trigger**: Go to Actions → Release → Run workflow
2. **Version Input**: Enter the exact version number (e.g., `1.5.1`, `1.6.0`, `2.0.0`)
3. **Automatic Steps**:
   - Validates version format
   - Checks if version already exists
   - Updates version in `kong-oidc.rockspec`
   - Updates Git tag in rockspec
   - Commits and pushes version changes
   - Creates Git tag
   - Generates changelog from conventional commits
   - Creates GitHub Release with changelog
   - Builds and pushes Docker images to GHCR

### Conventional Commits

For automatic changelog generation, use conventional commit messages:

```bash
# Bug fixes
git commit -m "fix: resolve authentication issue"

# New features
git commit -m "feat: add support for custom claims"

# Breaking changes
git commit -m "feat!: change API endpoint structure"

# Documentation
git commit -m "docs: update installation guide"

# Build/CI changes
git commit -m "ci: update GitHub Actions workflow"
```

### Release Tags

Docker images are tagged as:
- `v1.5.0` - Full version tag (e.g., `v1.5.0`, `v1.6.0`)
- `latest` - Latest stable release (main branch only)

## Migration from Kong 2.x

If you're migrating from Kong 2.x to Kong 3.9.x, please note the following changes:

1. **Credential Access**: The plugin now uses `kong.client.get_credential()` instead of `ngx.ctx.authenticated_credential`
2. **Authentication API**: Uses `kong.client.authenticate()` for setting credentials
3. **Dependencies**: Updated to use `lua-resty-openidc ~> 1.7.6-3` and `lua-resty-session ~> 4.0.5`

For Kong 2.x compatibility, please use version 1.4.x of this plugin.

## 🚀 **CI/CD Pipeline**

### **Workflows**

#### **CI Workflow** (`.github/workflows/ci.yml`)
- **Triggers:** Push to main, Pull requests, Manual trigger
- **Jobs:** Unit tests, Linting, Docker builds
- **Output:** Multi-architecture Docker images on GHCR

#### **Release Workflow** (`.github/workflows/release.yml`)
- **Triggers:** Manual trigger only
- **Jobs:** Version bumping, Git tagging, GitHub Release creation, Docker image building and publishing
- **Output:** Versioned Docker images on GHCR, GitHub Release with changelog



### **Manual Triggers**

#### **Manual CI Run:**
1. Go to **Actions** tab
2. Select **CI** workflow
3. Click **Run workflow**

#### **Manual Release:**
1. Go to **Actions** tab
2. Select **Release** workflow
3. Click **Run workflow**
4. Enter version number (e.g., `1.5.1`, `1.6.0`, `2.0.0`)
5. Optionally add release notes






