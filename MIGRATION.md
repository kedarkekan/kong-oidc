# Migration Guide: Kong OIDC Plugin from Kong 2.x to Kong 3.9.x

This guide helps you migrate the kong-oidc plugin from Kong 2.x to Kong 3.9.x.

## Overview of Changes

### Version Compatibility
- **Kong 2.x**: Use kong-oidc plugin version 1.4.x
- **Kong 3.9.x**: Use kong-oidc plugin version 1.5.x

### Breaking Changes

#### 1. Credential Access API
**Before (Kong 2.x):**
```lua
-- Access credentials in other plugins
local credential = ngx.ctx.authenticated_credential
if credential then
    local user_id = credential.id
    local username = credential.username
end
```

**After (Kong 3.9.x):**
```lua
-- Access credentials in other plugins
local credential = kong.client.get_credential()
if credential then
    local user_id = credential.id
    local username = credential.username
end
```

#### 2. Authentication API
**Before (Kong 2.x):**
```lua
-- Set credentials (internal plugin usage)
ngx.ctx.authenticated_credential = credential
```

**After (Kong 3.9.x):**
```lua
-- Set credentials (internal plugin usage)
kong.client.authenticate(consumer, credential)
```

#### 3. Dependencies
**Before (Kong 2.x):**
```lua
-- kong-oidc.rockspec
dependencies = {
    "lua-resty-openidc ~> 1.7.6-3"
}
```

**After (Kong 3.9.x):**
```lua
-- kong-oidc.rockspec
dependencies = {
    "lua-resty-openidc ~> 1.7.6-3",
    "lua-resty-session ~> 4.0.5"
}
```

## Step-by-Step Migration

### Step 1: Update Kong Version
```bash
# Stop Kong 2.x
kong stop

# Install Kong 3.9.1
# Follow Kong's official upgrade guide for your installation method
```

### Step 2: Update kong-oidc Plugin
```bash
# Remove old plugin
luarocks remove kong-oidc

# Install new plugin version
luarocks install kong-oidc 1.5.0-0
```

### Step 3: Update Plugin Configuration
No changes required to your existing plugin configuration. All configuration parameters remain the same.

### Step 4: Update Custom Code
If you have custom plugins or code that accesses credentials:

**Find and Replace:**
```bash
# Search for deprecated usage
grep -r "ngx.ctx.authenticated_credential" /path/to/your/plugins/
```

**Update the code:**
```lua
-- Replace this:
local credential = ngx.ctx.authenticated_credential

-- With this:
local credential = kong.client.get_credential()
```

### Step 5: Test Your Configuration
```bash
# Test Kong configuration
kong check

# Start Kong
kong start

# Test your OIDC endpoints
curl -H "Host: your-api.com" http://localhost:8000/your-protected-endpoint
```

### Step 6: Verify CI/CD (For Developers)
If you're contributing to the project:

```bash
# The project now uses GitHub Actions instead of Travis CI
# Check the CI status at: https://github.com/kedarkekan/kong-oidc/actions
```

## Docker Migration

### Before (Kong 2.x)
```dockerfile
FROM kong:2.8.1
# ... plugin installation
```

### After (Kong 3.9.x)
```dockerfile
FROM kong:3.9.1
# ... plugin installation with updated dependencies
```

Use the provided `Dockerfile.kong-3.9.1` for a production-ready image.

## Configuration Examples

### Basic OIDC Configuration (No Changes Required)
```lua
{
    "name": "oidc",
    "config": {
        "client_id": "your-client-id",
        "client_secret": "your-client-secret",
        "discovery": "https://your-oidc-provider/.well-known/openid-configuration",
        "scope": "openid profile email",
        "ssl_verify": "no"
    }
}
```

### Advanced Configuration (No Changes Required)
```lua
{
    "name": "oidc",
    "config": {
        "client_id": "your-client-id",
        "client_secret": "your-client-secret",
        "discovery": "https://your-oidc-provider/.well-known/openid-configuration",
        "scope": "openid profile email",
        "ssl_verify": "no",
        "bearer_jwt_auth_enable": "yes",
        "groups_claim": "groups",
        "userinfo_header_name": "X-Userinfo",
        "access_token_header_name": "X-Access-Token",
        "id_token_header_name": "X-ID-Token"
    }
}
```

## Troubleshooting

### Common Issues

#### 1. Plugin Not Loading
**Error:** `plugin 'oidc' not found`

**Solution:**
```bash
# Ensure plugin is installed
luarocks list | grep kong-oidc

# Reinstall if needed
luarocks remove kong-oidc
luarocks install kong-oidc 1.5.0-0
```

#### 2. Dependency Conflicts
**Error:** `Missing dependencies for kong 3.9.1-0`

**Solution:**
```bash
# Clear luarocks cache
rm -rf ~/.cache/luarocks

# Reinstall with explicit dependencies
luarocks install kong-oidc 1.5.0-0
```

#### 3. Credential Access Issues
**Error:** `attempt to index field 'authenticated_credential' (a nil value)`

**Solution:** Update your custom code to use `kong.client.get_credential()` instead of `ngx.ctx.authenticated_credential`.

### Verification Commands

```bash
# Check Kong version
kong version

# Check installed plugins
kong config db_export | grep oidc

# Test plugin functionality
curl -H "Host: your-api.com" http://localhost:8000/your-protected-endpoint
```

## Rollback Plan

If you need to rollback:

1. **Stop Kong 3.9.x:**
   ```bash
   kong stop
   ```

2. **Revert to Kong 2.x:**
   ```bash
   # Follow Kong's downgrade guide
   ```

3. **Revert kong-oidc plugin:**
   ```bash
   luarocks remove kong-oidc
   luarocks install kong-oidc 1.4.0-2
   ```

4. **Restart Kong:**
   ```bash
   kong start
   ```

## Support

If you encounter issues during migration:

1. Check the [Kong upgrade guide](https://docs.konghq.com/gateway/latest/install-and-run/upgrade/)
2. Review the [kong-oidc plugin documentation](README.md)
3. Open an issue on the [kong-oidc GitHub repository](https://github.com/kedarkekan/kong-oidc)

## Changelog

### Version 1.5.0-0
- **Added:** Kong 3.9.x compatibility
- **Changed:** Updated credential access API to use `kong.client.get_credential()`
- **Changed:** Updated authentication API to use `kong.client.authenticate()`
- **Added:** Explicit `lua-resty-session` dependency
- **Updated:** Dependencies to latest compatible versions
- **Improved:** Error handling and logging
- **Added:** Comprehensive test coverage for Kong 3.9.x

## Badge Status ✅

The badges in the README are **correctly configured**:

1. **CI Badge**: `https://github.com/kedarkekan/kong-oidc/workflows/CI/badge.svg`
2. **Coverage Badge**: `https://coveralls.io/repos/github/kedarkekan/kong-oidc/badge.svg?branch=master`
3. **Release Badge**: `https://github.com/kedarkekan/kong-oidc/workflows/Release/badge.svg`

###  **Why Badges Might Not Show:**

1. **No workflow runs yet** - Badges only appear after the first workflow execution
2. **Branch name** - Make sure you're on `master` or `main` branch
3. **GitHub caching** - Sometimes takes a few minutes to update

###  **To Fix This:**

1. **Push to trigger workflows**: The badges will appear after you push to the repository
2. **Check branch name**: Ensure you're on `master` or `main` branch
3. **Wait for first run**: GitHub Actions badges need at least one successful run

### 📝 **Alternative Badge URLs:**

If you want to use different badge styles, you can also use:

```markdown
<code_block_to_apply_changes_from>
```

The current badges are correctly configured and will work once the workflows are triggered! 🎯
