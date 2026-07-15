$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
Push-Location $Root
try {
    docker compose down
}
finally {
    Pop-Location
}
