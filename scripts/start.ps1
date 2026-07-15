[CmdletBinding()]
param(
    [switch]$NoBuild
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$Root = Split-Path -Parent $PSScriptRoot

Push-Location $Root
try {
    & "$PSScriptRoot\setup.ps1" -SkipDependencies

    if ($NoBuild) {
        docker compose up -d
    }
    else {
        docker compose up -d --build
    }

    $PortLine = Get-Content -LiteralPath '.env' | Where-Object { $_ -match '^NGINX_PORT=' } | Select-Object -First 1
    $Port = if ($PortLine) { ($PortLine -split '=', 2)[1].Trim() } else { '8088' }
    $Url = "http://127.0.0.1:$Port"
    Write-Host "[start] 服务已提交启动，入口：$Url"
    docker compose ps
}
finally {
    Pop-Location
}
