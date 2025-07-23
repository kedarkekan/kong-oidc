#!/bin/bash
set -e

export LUA_VERSION=${LUA_VERSION:-5.1}
export KONG_VERSION=${KONG_VERSION:-3.9.1-0}
export LUA_RESTY_OPENIDC_VERSION=${LUA_RESTY_OPENIDC_VERSION:-1.7.6-3}

pip install hererocks
hererocks lua_install -r^ --lua=${LUA_VERSION}
export PATH=${PATH}:${PWD}/lua_install/bin

# Clear luarocks cache to avoid manifest issues
rm -rf ~/.cache/luarocks
# Configure luarocks for Kong 3.x compatibility
luarocks config lua_version 5.1

luarocks install kong ${KONG_VERSION}
luarocks install lua-resty-openidc ${LUA_RESTY_OPENIDC_VERSION}
luarocks install lua-cjson
luarocks install luaunit
luarocks install luacov
