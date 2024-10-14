-- logger.lua
local logger = {}

-- 日志级别
local levels = {
    DEBUG = 1,
    INFO  = 2,
    WARN  = 3,
    ERROR = 4
}

-- 设置初始日志级别
local current_level = levels.INFO

-- 设置日志级别
function logger.set_level(level)
    local lvl = levels[level:upper()]
    if lvl then
        current_level = lvl
    else
        error("Invalid log level: " .. level)
    end
end

-- 获取当前时间戳
local function get_timestamp()
    return os.date("%Y-%m-%d %H:%M:%S")
end

-- 打印日志
local function log(level_name, level_value, message)
    if level_value >= current_level then
        io.write(string.format("[%s] [%s] %s", get_timestamp(), level_name, message), '\n')
    end
end

-- 定义日志级别的输出函数
function logger.debug(message)
    log("DEBUG", levels.DEBUG, message)
end

function logger.info(message)
    log("INFO", levels.INFO, message)
end

function logger.warn(message)
    log("WARN", levels.WARN, message)
end

function logger.error(message)
    log("ERROR", levels.ERROR, message)
end

return logger
