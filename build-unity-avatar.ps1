# Unity Desktop Avatar Build Script
# This script builds the Unity desktop avatar project

param(
    [string]$UnityPath = "",
    [string]$ProjectPath = "$PSScriptRoot\unity-desktop-avatar",
    [string]$OutputPath = "$PSScriptRoot\Builds",
    [switch]$Clean,
    [switch]$Development
)

# Auto-detect Unity if not provided
if (-not $UnityPath) {
    $possiblePaths = @(
        "C:\Program Files\Unity\Hub\Editor\2022.3.11f1\Editor\Unity.exe",
        "C:\Program Files\Unity\Hub\Editor\2022.3.12f1\Editor\Unity.exe",
        "C:\Program Files\Unity\Hub\Editor\2023.3.0f1\Editor\Unity.exe",
        "C:\Program Files\Unity\Editor\Unity.exe"
    )
    
    foreach ($path in $possiblePaths) {
        if (Test-Path $path) {
            $UnityPath = $path
            break
        }
    }
}

if (-not $UnityPath -or -not (Test-Path $UnityPath)) {
    Write-Host "❌ Unity not found. Please install Unity 2022.3.11f1 or later." -ForegroundColor Red
    Write-Host "Download from: https://unity.com/download" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Found Unity at: $UnityPath" -ForegroundColor Green

# Check project
if (-not (Test-Path "$ProjectPath\Assets\Scenes\Main.unity")) {
    Write-Host "❌ Unity project not found or invalid" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Unity project found" -ForegroundColor Green

# Create output directory
if (-not (Test-Path $OutputPath)) {
    New-Item -ItemType Directory -Path $OutputPath -Force | Out-Null
}

# Build arguments
$UnityArgs = @(
    "-batchmode",
    "-nographics",
    "-silent-crashes",
    "-projectPath", $ProjectPath,
    "-buildWindows64Player", "$OutputPath\DesktopAvatar.exe",
    "-quit"
)

if ($Development) {
    $UnityArgs += "-development"
}

if ($Clean) {
    Write-Host "🧹 Cleaning build directory..." -ForegroundColor Yellow
    if (Test-Path $OutputPath) {
        Remove-Item -Path $OutputPath -Recurse -Force
    }
    New-Item -ItemType Directory -Path $OutputPath -Force | Out-Null
}

# Start build
Write-Host "🚀 Starting Unity build..." -ForegroundColor Cyan
Write-Host "Command: $UnityPath $($UnityArgs -join ' ')" -ForegroundColor Gray

try {
    $process = Start-Process -FilePath $UnityPath -ArgumentList $UnityArgs -Wait -PassThru -NoNewWindow
    
    if ($process.ExitCode -eq 0) {
        Write-Host "✅ Build completed successfully!" -ForegroundColor Green
        
        if (Test-Path "$OutputPath\DesktopAvatar.exe") {
            $fileSize = (Get-Item "$OutputPath\DesktopAvatar.exe").Length / 1MB
            Write-Host "📦 Output: DesktopAvatar.exe ($([math]::Round($fileSize, 2)) MB)" -ForegroundColor Green
            Write-Host "🎮 Ready to run: $OutputPath\DesktopAvatar.exe" -ForegroundColor Cyan
        }
    } else {
        Write-Host "❌ Build failed with exit code: $($process.ExitCode)" -ForegroundColor Red
        Write-Host "Check Unity Editor.log for details" -ForegroundColor Yellow
        exit 1
    }
}
catch {
    Write-Host "❌ Build process failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
