local shell = require('shell')
local repo = "https://github.com/z5882852/RemotOC/blob/main/"
local scripts = {
    'run.lua',
    'env.lua',
    'lib/logger.lua',
    'lib/json.lua',
    'src/executor.lua',
    'plugins/echo.lua',
}

print("installing...")
for i = 1, #scripts do
    local script_path = string.format('%s', scripts[i])
    shell.execute(string.format('rm -f %s', script_path))

    local script_dir = script_path:match("(.*/)")

    if script_dir then
        shell.execute(string.format('mkdir -p %s', script_dir))
    end

    shell.execute(string.format('wget -f %s%s %s', repo, scripts[i], script_path))
end
print("done.")