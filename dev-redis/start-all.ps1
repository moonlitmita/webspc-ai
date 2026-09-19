# 脚本所在目录 = 项目根目录\dev-redis
$ConfDir = $PSScriptRoot

# 自动探测 redis-server.exe 路径
$RedisExe = $null

# 1. 常见安装根目录（含子目录）中查找
$CandidateRoots = @("D:\Redis")
foreach ($root in $CandidateRoots) {
    if (Test-Path -LiteralPath $root) {
        $found = Get-ChildItem -LiteralPath $root -Recurse -Filter "redis-server.exe" -ErrorAction SilentlyContinue |
                 Select-Object -First 1
        if ($found) { $RedisExe = $found.FullName; break }
    }
}

# 2. 从 PATH 环境中查找
if (-not $RedisExe) {
    $cmd = Get-Command redis-server -ErrorAction SilentlyContinue
    if ($cmd) { $RedisExe = $cmd.Source }
}

if (-not $RedisExe) {
    Write-Error "未找到 redis-server.exe，请检查 Redis 安装目录或将其加入 PATH。"
    exit 1
}

Write-Host "使用 Redis: $RedisExe"

# 确保数据目录存在（model/mcp 实例落盘到此目录）
$DataDir = Join-Path $ConfDir "data"
if (-not (Test-Path -LiteralPath $DataDir)) {
    New-Item -ItemType Directory -Path $DataDir | Out-Null
}

Start-Process "$RedisExe" "`"$ConfDir\redis-session.conf`"" -WindowStyle Normal
Start-Process "$RedisExe" "`"$ConfDir\redis-model.conf`""   -WindowStyle Normal
Start-Process "$RedisExe" "`"$ConfDir\redis-mcp.conf`""     -WindowStyle Normal
Start-Process "$RedisExe" "`"$ConfDir\redis-alarm.conf`"" -WindowStyle Normal

Write-Host "Four instances have been started:6380(session) 6381(model) 6382(MCP) 6383(alarm)"
