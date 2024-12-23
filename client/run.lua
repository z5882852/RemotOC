local event = require("event")

local executor = require("src.executor")
local env = require("env")
local logger = require("lib.logger")

local timerId  -- 存储计时器的 ID
local shouldExit = false  -- 退出标志

local args = {...}
if #args >= 1 then
    if args[1] == "--debug" then
        logger.set_level("DEBUG")
        logger.debug("Debug mode has been enabled.")
    end
end

local function pollServer()
    local success, info = xpcall(function()
        -- 检查是否需要退出
        if shouldExit then
            logger.info("Exiting polling...")
            event.cancel(timerId)  -- 取消定时器
            return
        end

        logger.debug("Polling... Free Memory: ".. require("computer").freeMemory())

        -- 获取命令和 taskId
        local taskId, command_table, isChunked = executor.fetchCommands()

        if isChunked then
            logger.debug("Using chunked upload")
        end

        if taskId and command_table then
            -- 处理命令并获取结果
            local command_result_table = executor.processCommands(command_table, isChunked)

            logger.debug("Reporting results for Task ID: " .. tostring(taskId))
            -- 将执行结果和 taskId 一起报告回服务器
            if isChunked then
                executor.reportChunkedResults(taskId, command_result_table[1])
            else
                executor.reportResults(taskId, command_result_table)
            end
        else
            logger.debug("No commands received or invalid response.")
        end
    end, debug.traceback)

    -- 处理发生的任何错误
    if not success then
        logger.error(info)
    end
end


-- 启动定时器
timerId = event.timer(env.pollingInterval, pollServer, math.huge)


logger.info("Program started at " .. os.date("%Y-%m-%d %H:%M:%S"))
while true do
    local eventType = event.pull()
    if eventType == "interrupted" then
        shouldExit = true
        if event.cancel(timerId) then
            logger.info("Interrupt received, shutting down...")
        else
            logger.error("error")
        end
        break
    end
end
