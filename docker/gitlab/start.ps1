# *********************************************************************************
# * SOTA Fleet Orchestration - Standardized Start System (v1.19.0)                *
# * Generated/Repaired by Antigravity on 2026-03-03                  *
# *********************************************************************************

# SOTA Infrastructure Orchestration: GitLab
# Target: local GitLab in Docker (Port 8929)

$ErrorActionPreference = "Stop"

$InfrastructurePath = "D:\Dev\infrastructure\gitlab"
$ConfigPath = Join-Path $InfrastructurePath "config"
$LogsPath = Join-Path $InfrastructurePath "logs"
$DataPath = Join-Path $InfrastructurePath "data"

Write-Host "--- Initializing Secure Substrate ---" -ForegroundColor Cyan

# Ensure directories exist
foreach ($path in @($ConfigPath, $LogsPath, $DataPath)) {
    if (!(Test-Path $path)) {
        New-Item -ItemType Directory -Path $path -Force | Out-Null
        Write-Host "Created persistence node: $path" -ForegroundColor Gray
    }
}

# Verify Docker
try {
    docker version | Out-Null
}
catch {
    Write-Error "Docker engine is not detected. Please ensure Docker Desktop is running."
}

# Start Stack
Write-Host "Deploying GitLab container (Port 8929)..." -ForegroundColor Yellow
docker-compose up -d

Write-Host "Orchestration Complete. GitLab is warming up." -ForegroundColor Green
Write-Host "Access URL: http://localhost:8929" -ForegroundColor Green
Write-Host "Note: Internal boot may take 2-5 minutes on first run." -ForegroundColor Cyan

