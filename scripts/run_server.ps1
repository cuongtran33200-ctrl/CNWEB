$ErrorActionPreference = "Stop"

$port = 8025
while (Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue) {
    $port++
}

$backend = Join-Path $PSScriptRoot "..\backend"
$python = Join-Path $PSScriptRoot "..\.venv\Scripts\python.exe"

Write-Host "Starting Django on http://127.0.0.1:$port"
Push-Location $backend
try {
    & $python manage.py runserver "127.0.0.1:$port"
}
finally {
    Pop-Location
}