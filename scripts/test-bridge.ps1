# Test webapp bridge to backend (MCP HTTP server).
# Run from repo root. Backend must be running on 10793 (e.g. web_sota/start.ps1).

$Base = "http://127.0.0.1:10793"
$ErrorCount = 0

function Test-Endpoint {
    param([string]$Path, [string]$Description)
    try {
        $r = Invoke-WebRequest -Uri "$Base$Path" -UseBasicParsing -TimeoutSec 5
        if ($r.StatusCode -eq 200) {
            Write-Host "OK $Path - $Description" -ForegroundColor Green
            return $true
        }
    } catch {
        Write-Host "FAIL $Path - $Description - $($_.Exception.Message)" -ForegroundColor Red
        $script:ErrorCount++
        return $false
    }
    Write-Host "FAIL $Path - Status $($r.StatusCode)" -ForegroundColor Red
    $script:ErrorCount++
    return $false
}

Write-Host "Testing Avatar-MCP backend bridge (base $Base)..." -ForegroundColor Cyan
Test-Endpoint -Path "/api/v1/health" -Description "health"
Test-Endpoint -Path "/api/v1/status" -Description "status"
Test-Endpoint -Path "/api/v1/tools" -Description "tools list"
Test-Endpoint -Path "/api/v1/avatars" -Description "avatars list"

if ($ErrorCount -eq 0) {
    Write-Host "All bridge endpoints OK." -ForegroundColor Green
    exit 0
} else {
    Write-Host "$ErrorCount endpoint(s) failed. Ensure backend is running: uv run uvicorn avatarmcp.http_server:app --host 127.0.0.1 --port 10793" -ForegroundColor Yellow
    exit 1
}
