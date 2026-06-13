param(
    [switch]$Headless,
    [switch]$BackendOnly,
    [switch]$NoBrowser
)

$WebPort = 10792
$BackendPort = 10793
$MetricsPort = 10790
$ProjectRoot = Split-Path -Parent $PSScriptRoot

$FleetStartPath = Join-Path $ProjectRoot "scripts\FleetStartMode.ps1"
if (-not (Test-Path -LiteralPath $FleetStartPath)) {
    Write-Host "ERROR: Missing vendored launcher helper: $FleetStartPath" -ForegroundColor Red
    exit 1
}
. $FleetStartPath
$FleetStart = Initialize-FleetStartMode @PSBoundParameters
Enter-FleetHeadlessConsole -Headless:$Headless -BackendOnly:$BackendOnly

# Docker compose publishes 10793 (avatarmcp) and 10790 (prometheus) — stop before local uvicorn
$composeFile = Join-Path $ProjectRoot "docker-compose.yml"
if ((Get-Command docker -ErrorAction SilentlyContinue) -and (Test-Path $composeFile)) {
    $dockerNames = @(
        (& docker ps --filter "publish=$BackendPort" --format "{{.Names}}" 2>$null)
        (& docker ps --filter "publish=$MetricsPort" --format "{{.Names}}" 2>$null)
    ) | Where-Object { $_ }
    if ($dockerNames.Count -gt 0) {
        Write-Host "[avatar-mcp] Stopping Docker services on fleet ports ($($dockerNames -join ', '))..." -ForegroundColor Yellow
        & docker compose -f $composeFile stop avatarmcp prometheus 2>$null
        Start-Sleep -Seconds 2
    }
}

Stop-FleetPortSquatters -Ports @($WebPort, $BackendPort, $MetricsPort) -Label "avatar-mcp"

if (-not (Assert-FleetPortsAvailable -Ports @($WebPort, $BackendPort, $MetricsPort) -Label "avatar-mcp")) { exit 1 }

Set-Location $PSScriptRoot
if (-not (Test-Path "node_modules")) { npm install }

Write-Host "Starting Python backend on port $BackendPort ..." -ForegroundColor Cyan
$backendCmd = "Set-Location '$PSScriptRoot'; uv run --project '$ProjectRoot' uvicorn avatarmcp.http_server:app --host 127.0.0.1 --port $BackendPort --log-level info"
Start-Process powershell -ArgumentList "-NoProfile", "-WindowStyle", "Normal", "-Command", $backendCmd

$healthUrl = "http://127.0.0.1:$BackendPort/api/v1/health"
$maxWait = 45
$waited = 0
$backendUp = $false
while ($waited -lt $maxWait) {
    try {
        $null = Invoke-WebRequest -Uri $healthUrl -UseBasicParsing -TimeoutSec 3 -ErrorAction Stop
        Write-Host "Backend ready at $healthUrl" -ForegroundColor Green
        $backendUp = $true
        break
    } catch {
        Start-Sleep -Seconds 2
        $waited += 2
    }
}
if (-not $backendUp) {
    Write-Host "WARNING: Backend did not answer /api/v1/health within ${maxWait}s." -ForegroundColor Yellow
}

if (-not $FleetStart.RunFrontend) {
    while ($true) { Start-Sleep -Seconds 60 }
}

if (-not $NoBrowser) {
    $frontendUrl = "http://127.0.0.1:$WebPort/"
    $pollAndOpen = "for (`$i = 0; `$i -lt 60; `$i++) { try { `$null = Invoke-WebRequest -Uri '$frontendUrl' -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop; Start-Process '$frontendUrl'; exit } catch { Start-Sleep -Seconds 1 } }"
    Start-Process powershell -ArgumentList "-NoProfile", "-WindowStyle", "Hidden", "-Command", $pollAndOpen
}

Write-Host "Starting Vite frontend on port $WebPort ..." -ForegroundColor Green
npm run dev -- --port $WebPort --host 127.0.0.1 --strictPort


