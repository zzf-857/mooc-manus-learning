[CmdletBinding()]
param(
    [switch]$SkipDependencies
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$Root = Split-Path -Parent $PSScriptRoot

function Require-Command([string]$Name, [string]$InstallHint) {
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "缺少 $Name。$InstallHint"
    }
}

Push-Location $Root
try {
    Require-Command 'docker' '请安装并启动 Docker Desktop。'

    if (-not (Test-Path -LiteralPath '.env')) {
        Copy-Item -LiteralPath '.env.example' -Destination '.env'
        Write-Host '[setup] 已从 .env.example 创建本地 .env'
    }
    if (-not (Test-Path -LiteralPath 'api/config.yaml')) {
        Copy-Item -LiteralPath 'api/config.example.yaml' -Destination 'api/config.yaml'
        Write-Host '[setup] 已创建安全的 api/config.yaml；可在 UI 设置页填写模型密钥'
    }

    docker compose config --quiet

    if (-not $SkipDependencies) {
        Require-Command 'uv' '请运行 winget install --id=astral-sh.uv -e。'
        Require-Command 'npm' '请安装 Node.js 22 LTS 或更新版本。'
        uv sync --project api --frozen
        npm ci --prefix ui
    }

    Write-Host '[setup] 环境准备完成。运行 .\scripts\start.ps1 启动完整栈。'
}
finally {
    Pop-Location
}
