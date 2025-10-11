# AvatarMCP Desktop Avatar Build Script
# Builds the Unity desktop avatar application for Windows

param(
    [string]$UnityPath = "C:\Program Files\Unity\Hub\Editor\2022.3.11f1\Editor\Unity.exe",
    [string]$ProjectPath = $PSScriptRoot,
    [string]$OutputPath = "$PSScriptRoot\Builds",
    [string]$BuildTarget = "Win64",
    [switch]$Clean,
    [switch]$NoGraphicsTests,
    [switch]$Development
)

# Configuration
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

if ($NoGraphicsTests) {
    $UnityArgs += "-noGraphicsTests"
}

# Functions
function Write-Header {
    param([string]$Message)
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host " $Message" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
}

function Write-Step {
    param([string]$Message)
    Write-Host "[$((Get-Date).ToString('HH:mm:ss'))] $Message" -ForegroundColor Yellow
}

function Write-Success {
    param([string]$Message)
    Write-Host "✓ $Message" -ForegroundColor Green
}

function Write-Error {
    param([string]$Message)
    Write-Host "✗ $Message" -ForegroundColor Red
}

# Main build process
function Start-Build {
    Write-Header "AvatarMCP Desktop Avatar Build"

    # Check prerequisites
    Write-Step "Checking prerequisites..."
    if (!(Test-Path $UnityPath)) {
        Write-Error "Unity not found at: $UnityPath"
        Write-Host "Please update the UnityPath parameter to point to your Unity installation" -ForegroundColor Yellow
        exit 1
    }
    Write-Success "Unity found"

    # Check project path
    if (!(Test-Path $ProjectPath)) {
        Write-Error "Project path not found: $ProjectPath"
        exit 1
    }
    Write-Success "Project path valid"

    # Clean build directory if requested
    if ($Clean) {
        Write-Step "Cleaning build directory..."
        if (Test-Path $OutputPath) {
            Remove-Item -Path $OutputPath -Recurse -Force
        }
        New-Item -ItemType Directory -Path $OutputPath -Force | Out-Null
        Write-Success "Build directory cleaned"
    }

    # Create output directory
    if (!(Test-Path $OutputPath)) {
        New-Item -ItemType Directory -Path $OutputPath -Force | Out-Null
    }

    # Start build
    Write-Step "Starting Unity build..."
    Write-Host "Command: $UnityPath $($UnityArgs -join ' ')" -ForegroundColor Gray

    try {
        $process = Start-Process -FilePath $UnityPath -ArgumentList $UnityArgs -Wait -PassThru -NoNewWindow

        if ($process.ExitCode -eq 0) {
            Write-Success "Build completed successfully"

            # Check output
            if (Test-Path "$OutputPath\DesktopAvatar.exe") {
                $fileSize = (Get-Item "$OutputPath\DesktopAvatar.exe").Length / 1MB
                Write-Success "Output file created: DesktopAvatar.exe ($([math]::Round($fileSize, 2)) MB)"

                # Create additional files
                Create-AdditionalFiles
            } else {
                Write-Error "Build completed but output file not found"
                exit 1
            }
        } else {
            Write-Error "Build failed with exit code: $($process.ExitCode)"
            Write-Host "Check Unity Editor.log for detailed error information" -ForegroundColor Yellow
            exit 1
        }
    }
    catch {
        Write-Error "Build process failed: $($_.Exception.Message)"
        exit 1
    }
}

function Create-AdditionalFiles {
    Write-Step "Creating additional build files..."

    # Create config directory
    $configDir = "$OutputPath\DesktopAvatar_Data\Config"
    New-Item -ItemType Directory -Path $configDir -Force | Out-Null

    # Copy default config
    Copy-Item -Path "$ProjectPath\Assets\Resources\Config\config.json" -Destination "$configDir\" -Force
    Write-Success "Configuration files copied"

    # Create README for distribution
    $readmeContent = @"
AvatarMCP Desktop Avatar
========================

This is the desktop avatar application for AvatarMCP.

Installation:
1. Extract all files to a folder
2. Run DesktopAvatar.exe
3. The application will start in transparent window mode

Configuration:
- Edit Config/config.json to customize settings
- Place VRM files in StreamingAssets/Avatars/
- Place plugins in StreamingAssets/Plugins/

Controls:
- OSC messages can be sent to port 9000 for avatar control
- See documentation for available OSC commands

For more information, visit: https://github.com/yourusername/avatar-mcp
"@

    $readmeContent | Out-File -FilePath "$OutputPath\README.txt" -Encoding UTF8
    Write-Success "README created"

    # Create run script
    $runScript = @'
@echo off
echo Starting AvatarMCP Desktop Avatar...
start "" "DesktopAvatar.exe"
echo Avatar started. OSC control available on port 9000.
pause
'@

    $runScript | Out-File -FilePath "$OutputPath\Run.bat" -Encoding ASCII
    Write-Success "Run script created"
}

# Run build
Start-Build
