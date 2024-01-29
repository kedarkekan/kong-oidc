package.path = "test/lib/?.lua;" .. package.path -- kong & co (prioritize our mocks)

local Object = require "classic"
local BaseCase = Object:extend()


function BaseCase:setUp()
end

function BaseCase:tearDown()
end


return BaseCase
