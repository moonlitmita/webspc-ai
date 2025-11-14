# Redis 安装目录
$RedisHome = "D:\Redis"

# 脚本所在目录 = 项目根目录\dev-redis
$ConfDir = $PSScriptRoot 

Start-Process "$RedisHome\redis-server.exe" "`"$ConfDir\redis-session.conf`"" -WindowStyle Normal
Start-Process "$RedisHome\redis-server.exe" "`"$ConfDir\redis-model.conf`""   -WindowStyle Normal
Start-Process "$RedisHome\redis-server.exe" "`"$ConfDir\redis-mcp.conf`""     -WindowStyle Normal

Write-Host "Three instances have been started:6379(session) 6380(model) 6381(MCP)"
