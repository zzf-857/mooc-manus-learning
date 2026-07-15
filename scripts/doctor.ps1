$ErrorActionPreference = 'Continue'
$Root = Split-Path -Parent $PSScriptRoot
Push-Location $Root
try {
    Write-Host '== Toolchain =='
    foreach ($Command in @('git', 'docker', 'uv', 'node', 'npm')) {
        $Resolved = Get-Command $Command -ErrorAction SilentlyContinue
        if ($Resolved) { Write-Host "[OK] $Command -> $($Resolved.Source)" }
        else { Write-Host "[MISSING] $Command" }
    }

    Write-Host "`n== Local config =="
    foreach ($Path in @('.env', 'api/config.yaml')) {
        if (Test-Path -LiteralPath $Path) { Write-Host "[OK] $Path" }
        else { Write-Host "[MISSING] $Path (运行 scripts/setup.ps1 创建)" }
    }

    Write-Host "`n== Compose =="
    docker compose config --quiet
    if ($LASTEXITCODE -eq 0) { Write-Host '[OK] Compose 配置有效' }
    docker compose ps

    Write-Host "`n== HTTP =="
    $PortLine = Get-Content -LiteralPath '.env' -ErrorAction SilentlyContinue | Where-Object { $_ -match '^NGINX_PORT=' } | Select-Object -First 1
    $Port = if ($PortLine) { ($PortLine -split '=', 2)[1].Trim() } else { '8088' }
    $BaseUrl = "http://127.0.0.1:$Port"
    foreach ($Url in @($BaseUrl, "$BaseUrl/api/status", "$BaseUrl/api/docs")) {
        try {
            $Response = Invoke-WebRequest -UseBasicParsing -Uri $Url -TimeoutSec 5
            Write-Host "[OK] $Url -> HTTP $($Response.StatusCode)"
        }
        catch {
            Write-Host "[FAIL] $Url -> $($_.Exception.Message)"
        }
    }
}
finally {
    Pop-Location
}
