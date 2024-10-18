local internet = require("internet")
local computer = require("computer")
local os = require("os")
local filesystem = require("filesystem")
local shell = require("shell")

local env = require("env")
local logger = require("lib/logger")
local json = require("lib/json")


local executor = {}

local serverUrl = env.baseUrl .. env.getPath
local reportUrl = env.baseUrl .. env.reportPath
local chunkedReportUrl = env.baseUrl .. env.chunkedReportPath



-- 导入插件
local function loadPlugins()
    -- 获取当前工作目录的路径
    local pluginPath = shell.resolve("plugins/")
    for file in filesystem.list(pluginPath) do
        -- 只加载 *.lua
        if file:match("%.lua$") then
            local moduleName = file:sub(1, -5) -- 去掉 ".lua" 扩展名
            local success, err = pcall(function() require("plugins/" .. moduleName) end)

            if success then
                logger.info("Successfully loaded plugin: " .. moduleName)
            else
                logger.error("Error loading plugin: " .. moduleName .. err)
            end
        end
    end
end


local function getHeaders()
    local headers = {
        ["Content-Type"] = "application/json",
        ["X-Client-ID"] = env.clientId,
        ["X-Server-Token"] = env.serverToken,
    }
    return headers
end


local function close(req)
    local success = false
    -- 检查是否为函数直接调用
    if type(req.close) == "function" then
        req.close()
        success = true
    end

    -- 检查元表是否有 close 方法
    if not success then
        local mt = getmetatable(req)
        if mt and mt.__index and mt.__index.close then
            mt.__index.close()
            success = true
        elseif mt and mt.__call then
            mt.__call(req, "close")
            success = true
        end
    end

    -- 如果还不成功，记录错误日志
    if not success then
        logger.error("Failed to close the request.")
    end
end

-- 执行单个命令的函数
local function executeCommand(command_content)
    logger.debug("Executing command: " .. tostring(command_content)) -- Debug: 输出正在执行的命令内容
    local code, loadError = load(command_content)

    if not code then
        logger.debug("Failed to load command: " .. tostring(loadError)) -- Debug: 输出加载失败的错误
        return false, loadError
    end

    local success, result = xpcall(code, debug.traceback)

    if not success then
        logger.debug("Command execution failed: " .. tostring(result)) -- Debug: 输出执行失败的错误信息
        return false, result
    end

    logger.debug("Command executed successfully") -- Debug: 输出执行成功的结果
    return true, result
end

-- 处理从服务器接收到的命令
function executor.processCommands(command_table, isChunked)
    logger.debug("Processing commands...") -- Debug: 输出接收到的命令表
    local command_result_table = {}

    for cid, command_content in pairs(command_table) do
        logger.debug("Processing command with ID: " .. tostring(cid)) -- Debug: 输出当前处理的命令ID
        local success, command_result = executeCommand(command_content)

        if success then
            if isChunked and command_result.message == "success" then
                command_result_table[cid] = command_result.data
            else
                command_result_table[cid] = json.encode(command_result)
            end
        else
            command_result_table[cid] = json.encode({ message = command_result })
        end
    end
    return command_result_table
end

-- 从服务器获取命令的函数
function executor.fetchCommands()
    logger.debug("Fetching commands from server...") -- Debug: 输出正在获取命令

    local headers = getHeaders()
    local req = internet.request(serverUrl, nil, headers)
    local response = ""
    if not req then
        logger.error("Unable to connect to the server.")
        return nil, nil, nil
    end

    -- 等待请求完成连接，设置超时时间
    local startTime = computer.uptime()
    local timeout = 2 -- 超时时间（秒）

    while not req.finishConnect() do
        if computer.uptime() - startTime > timeout then
            logger.error("Timeout while fetching commands to the server.")
            close(req)
            return nil, nil, nil
        end
        os.sleep(0)
    end

    -- 读取响应内容
    local chunk
    repeat
        chunk = req.read()
        if chunk then
            response = response .. chunk
        end
    until not chunk

    close(req)

    if response == "" then
        return nil, nil, nil
    end

    -- 将 JSON 响应解码为 Lua 表
    local res = json.decode(response)


    -- 检查响应码
    if not res or res.code ~= 200 then
        if res.message then
            logger.warn("Unable to fetching commands: " .. res.message)
        else
            logger.warn("Unable to fetching commands: unknown error")
        end
        return nil, nil, nil
    end

    local command_table = res.data

    -- 检查是否包含 taskId 和 commands 字段
    if not command_table or not command_table.taskId or not command_table.commands then
        return nil, nil, nil
    end


    logger.debug("Task ID: " .. tostring(command_table.taskId))

    -- 返回 taskId 和 commands
    return command_table.taskId, command_table.commands, command_table.is_chunked
end

-- 向服务器报告命令执行结果的函数
function executor.reportResults(taskId, command_result_table)
    logger.debug("Reporting command results to server for Task ID: " .. tostring(taskId))

    local report_data = {
        task_id = taskId,
        results = command_result_table
    }

    local headers = getHeaders()
    -- 向服务器发送报告
    local req = internet.request(
        reportUrl,
        json.encode(report_data),
        headers
    )

    if not req then
        logger.error("Unable to connect to the server to report results.")
        return
    end

    local startTime = computer.uptime()
    local timeout = 4 -- 超时时间（秒）

    while not req.finishConnect() do
        if computer.uptime() - startTime > timeout then
            logger.error("Timeout while reporting results to the server.")
            close(req)
            return
        end
        os.sleep(0)
    end

    -- 读取并忽略响应内容（如果有）
    repeat
        local chunk = req.read()
    until not chunk

    logger.debug("Results for Task ID " .. tostring(taskId) .. " successfully reported.")
    close(req)
end

-- 向服务器报告命令执行结果的函数（分块上传）
function executor.reportChunkedResults(taskId, command_result_table)
    logger.debug("Reporting command results to server for Task ID: " .. tostring(taskId) .. " using chunked upload.")

    -- 设置默认的分块大小，如果没有传入则默认分块大小为 128
    local chunk_size = env.chunkSize or 128
    local total_commands = #command_result_table
    local chunked = 1 -- 初始块编号为1，表示开始分块上传

    -- 分块上传时，遍历所有结果，并分块发送
    for i = 1, total_commands, chunk_size do
        local chunked_result = {}

        -- 获取当前块的结果
        for j = i, math.min(i + chunk_size - 1, total_commands) do
            chunked_result[#chunked_result + 1] = command_result_table[j]
        end
        chunked = i
        -- 判断是否是最后一块
        if i + chunk_size - 1 >= total_commands then
            chunked = 0 -- 最后一块时，chunked 为 0
        end

        -- 准备报告数据
        local report_data = {
            task_id = taskId,
            results = chunked_result
        }

        local headers = getHeaders()

        -- 向服务器发送分块报告
        local req = internet.request(
            chunkedReportUrl .. "?chunked=" .. tostring(chunked),
            json.encode(report_data),
            headers
        )

        if not req then
            logger.error("Unable to connect to the server to report chunked results.")
            return
        end

        local startTime = computer.uptime()
        local timeout = 4 -- 超时时间（秒）

        while not req.finishConnect() do
            if computer.uptime() - startTime > timeout then
                logger.error("Timeout while reporting chunked results to the server.")
                close(req)
                return
            end
            os.sleep(0)
        end

        -- 读取并忽略响应内容（如果有）
        repeat
            local chunk = req.read()
        until not chunk

        logger.debug("Chunked results for Task ID " .. tostring(taskId) .. " successfully reported.")
        close(req)

        -- 如果最后一块已完成，结束循环
        if chunked == 0 then
            break
        end
        os.sleep(0.2)
    end
end

loadPlugins()

return executor
