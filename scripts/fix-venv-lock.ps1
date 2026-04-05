# Unblock uv sync when avatarmcp.exe or a process using .venv is locking.
# Run from repo root. Use -Kill to terminate found processes; use -Recreate to delete .venv and uv sync.

param([switch]$Kill, [switch]$Recreate)

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$VenvPath = Join-Path $ProjectRoot ".venv"
$VenvScripts = Join-Path $VenvPath "Scripts"

if ($Recreate) {
    Write-Host "Recreating .venv (removing and running uv sync)..." -ForegroundColor Cyan
    if (Test-Path $VenvPath) {
        Write-Host "Removing existing .venv..." -ForegroundColor Yellow
        try {
            Remove-Item -Recurse -Force $VenvPath -ErrorAction Stop
            Write-Host "Removed." -ForegroundColor Green
        } catch {
            Write-Host "Could not remove .venv: $_" -ForegroundColor Red
            Write-Host "Close Cursor, all PowerShell windows, and any process using this repo. Then run: Remove-Item -Recurse -Force .venv; uv sync" -ForegroundColor Yellow
            exit 1
        }
    }
    Set-Location $ProjectRoot
    uv sync
    if ($LASTEXITCODE -eq 0) { Write-Host "Done. No avatarmcp.exe is installed (run via: uv run python -m avatarmcp)." -ForegroundColor Green }
    exit $LASTEXITCODE
}

if (-not (Test-Path $VenvPath)) {
    Write-Host "No .venv at $VenvPath" -ForegroundColor Yellow
    exit 0
}

$found = @()
$venvNorm = $VenvPath -replace "\\", "\\"
Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | Where-Object {
    $_.ExecutablePath -and ($_.ExecutablePath -like "*avatar-mcp*" -or $_.ExecutablePath -like "*avatarmcp*")
} | ForEach-Object {
    $found += [PSCustomObject]@{ PID = $_.ProcessId; Path = $_.ExecutablePath; CommandLine = $_.CommandLine }
}
Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | Where-Object {
    $cmd = $_.CommandLine
    $cmd -and ($cmd -like "*avatarmcp*" -or $cmd -like "*avatar-mcp*" -or $cmd -like "*http_server*" -or $cmd -like "*uvicorn*avatarmcp*" -or $cmd -like "*$VenvPath*")
} | ForEach-Object {
    if ($found.PID -notcontains $_.ProcessId) {
        $found += [PSCustomObject]@{ PID = $_.ProcessId; Path = $_.ExecutablePath; CommandLine = $_.CommandLine }
    }
}

if ($found.Count -eq 0) {
    Write-Host "No process found that clearly uses this venv. The lock is often from Cursor (MCP) or a terminal." -ForegroundColor Cyan
    Write-Host "Option 1: Close Cursor and all terminals, then run: uv sync" -ForegroundColor White
    Write-Host "Option 2: Recreate venv (removes .venv and runs uv sync): .\scripts\fix-venv-lock.ps1 -Recreate" -ForegroundColor White
    exit 0
}

foreach ($p in $found) {
    Write-Host "PID $($p.PID): $($p.Path)" -ForegroundColor Yellow
    if ($Kill) {
        try {
            Stop-Process -Id $p.PID -Force -ErrorAction Stop
            Write-Host "  Stopped." -ForegroundColor Green
        } catch {
            Write-Host "  Failed: $_" -ForegroundColor Red
        }
    }
}

if (-not $Kill -and $found.Count -gt 0) {
    Write-Host "To stop these run: .\scripts\fix-venv-lock.ps1 -Kill" -ForegroundColor Cyan
    Write-Host "Or recreate venv: .\scripts\fix-venv-lock.ps1 -Recreate" -ForegroundColor Cyan
}
