package.path = "test/lib/?.lua;" .. package.path -- kong & co (prioritize our mocks)

local filter = require("kong.plugins.oidc.filter")
local lu = require("luaunit")

TestFilter = require("test.unit.base_case"):extend()

function TestFilter:setUp()
  TestFilter.super:setUp()
  _G.ngx = {
    var = {
      uri = ""
    }
  }
end

function TestFilter:tearDown()
  TestFilter.super:tearDown()
end

local config =  {
  filters = {  "^/pattern1$","^/pattern2$"}
}

function TestFilter:testIgnoreRequestWhenMatchingPattern1()
  ngx.var.uri = "/pattern1"
  lu.assertFalse(filter.shouldProcessRequest(config))
end

function TestFilter:testIgnoreRequestWhenMatchingPattern2()
  ngx.var.uri = "/pattern2"
  lu.assertFalse(filter.shouldProcessRequest(config))
end

function TestFilter:testProcesseRequestWhenNoMatch()
  ngx.var.uri = "/not_matching"
  lu.assertTrue(filter.shouldProcessRequest(config))
end

function TestFilter:testProcessRequestWhenTheyAreNoFiltersNil()
  ngx.var.uri = "/pattern1"
  local testConfig = { filters = nil }
  lu.assertTrue(filter.shouldProcessRequest(testConfig))
end

function TestFilter:testProcessRequestWhenTheyAreNoFiltersEmpty()
  ngx.var.uri = "/pattern1"
  local testConfig = { filters = {} }
  lu.assertTrue(filter.shouldProcessRequest(testConfig))
end


lu.run()
