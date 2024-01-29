-- Luacheck configuration for kong-oidc plugin
-- Suppress warnings that are expected for Kong plugins

-- Global variables provided by Kong
globals = {
    -- Kong globals
    "kong",
    "ngx",

    -- Test globals
    "TestHandler",
    "TestFilter",
    "TestUtils",
    "TestToken",
    "TestIntrospect",
    "lu",
    "luacov",

    -- Classic module
    "Object",
    "BaseCase",
    "MockableCase"
}

-- Suppress specific warning types for Kong plugins
-- These are expected in Kong plugin development
no_unused = false  -- Allow unused variables in tests
no_redefined = false  -- Allow redefined variables in tests
no_get = false  -- Allow accessing undefined variables (ngx, kong)
no_set = false  -- Allow setting global variables (for mocks)

-- Max line length (disabled as requested)
max_line_length = false

-- Per-file configurations
files = {
    -- Kong plugin files - suppress expected warnings
    ["kong/plugins/oidc/*.lua"] = {
        no_unused = false,
        no_redefined = false,
        no_get = false,
        no_set = false
    },

    -- Test files - suppress test-specific warnings
    ["test/unit/*.lua"] = {
        no_unused = false,
        no_redefined = false,
        no_get = false,
        no_set = false
    },

    -- Mock files - suppress mock-specific warnings
    ["test/lib/*.lua"] = {
        no_unused = false,
        no_redefined = false,
        no_get = false,
        no_set = false
    }
}
