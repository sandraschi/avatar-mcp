#!/usr/bin/env python3
"""
Unity Desktop Avatar Build Helper

This script helps build the Unity desktop avatar project when Unity is available.
It provides fallback options and guidance for Unity installation.
"""

import os
import sys
from pathlib import Path


def find_unity_installations():
    """Find Unity installations on the system."""
    possible_paths = [
        r"C:\Program Files\Unity\Hub\Editor\*\Editor\Unity.exe",
        r"C:\Program Files\Unity\Editor\Unity.exe",
        r"C:\Program Files (x86)\Unity\Editor\Unity.exe",
        r"C:\Unity\Editor\Unity.exe",
    ]

    found_installations = []

    for pattern in possible_paths:
        if "*" in pattern:
            # Handle wildcard patterns
            import glob

            matches = glob.glob(pattern)
            found_installations.extend(matches)
        else:
            if os.path.exists(pattern):
                found_installations.append(pattern)

    return found_installations


def check_unity_project():
    """Check if Unity project exists and is valid."""
    project_path = Path("unity-desktop-avatar")

    if not project_path.exists():
        return False, "Unity project directory not found"

    # Check for essential Unity files
    essential_files = [
        "Assets/Scenes/Main.unity",
        "Assets/Scripts/AvatarController.cs",
        "ProjectSettings/ProjectSettings.asset",
    ]

    missing_files = []
    for file_path in essential_files:
        if not (project_path / file_path).exists():
            missing_files.append(file_path)

    if missing_files:
        return False, f"Missing essential files: {', '.join(missing_files)}"

    return True, "Unity project is valid"


def create_build_script():
    """Create a PowerShell build script for Unity."""
    script_content = """# Unity Desktop Avatar Build Script
# This script builds the Unity desktop avatar project

param(
    [string]$UnityPath = "",
    [string]$ProjectPath = "$PSScriptRoot\\unity-desktop-avatar",
    [string]$OutputPath = "$PSScriptRoot\\Builds",
    [switch]$Clean,
    [switch]$Development
)

# Auto-detect Unity if not provided
if (-not $UnityPath) {
    $possiblePaths = @(
        "C:\\Program Files\\Unity\\Hub\\Editor\\2022.3.11f1\\Editor\\Unity.exe",
        "C:\\Program Files\\Unity\\Hub\\Editor\\2022.3.12f1\\Editor\\Unity.exe",
        "C:\\Program Files\\Unity\\Hub\\Editor\\2023.3.0f1\\Editor\\Unity.exe",
        "C:\\Program Files\\Unity\\Editor\\Unity.exe"
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
if (-not (Test-Path "$ProjectPath\\Assets\\Scenes\\Main.unity")) {
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
    "-buildWindows64Player", "$OutputPath\\DesktopAvatar.exe",
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
        
        if (Test-Path "$OutputPath\\DesktopAvatar.exe") {
            $fileSize = (Get-Item "$OutputPath\\DesktopAvatar.exe").Length / 1MB
            Write-Host "📦 Output: DesktopAvatar.exe ($([math]::Round($fileSize, 2)) MB)" -ForegroundColor Green
            Write-Host "🎮 Ready to run: $OutputPath\\DesktopAvatar.exe" -ForegroundColor Cyan
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
"""

    script_path = Path("build-unity-avatar.ps1")
    script_path.write_text(script_content, encoding="utf-8")
    return script_path


def main():
    """Main function to check Unity setup and create build script."""
    print("🎮 Unity Desktop Avatar Build Helper")
    print("=" * 50)

    # Check Unity installations
    print("\n🔍 Checking for Unity installations...")
    unity_installations = find_unity_installations()

    if unity_installations:
        print(f"✅ Found {len(unity_installations)} Unity installation(s):")
        for installation in unity_installations:
            print(f"   📁 {installation}")
    else:
        print("❌ No Unity installations found")
        print("\n📥 To install Unity:")
        print("   1. Download Unity Hub from https://unity.com/download")
        print("   2. Install Unity 2022.3.11f1 LTS or later")
        print("   3. Run this script again")

    # Check Unity project
    print("\n🔍 Checking Unity project...")
    project_valid, message = check_unity_project()

    if project_valid:
        print(f"✅ {message}")
    else:
        print(f"❌ {message}")
        print("\n📁 Make sure the unity-desktop-avatar directory exists")
        print("   and contains a valid Unity project")

    # Create build script
    print("\n📝 Creating build script...")
    script_path = create_build_script()
    print(f"✅ Created build script: {script_path}")

    # Instructions
    print("\n🚀 Next steps:")
    if unity_installations and project_valid:
        print("   1. Run: .\\build-unity-avatar.ps1")
        print("   2. Wait for build to complete")
        print("   3. Run: .\\Builds\\DesktopAvatar.exe")
    else:
        print("   1. Install Unity (see instructions above)")
        print("   2. Ensure Unity project is valid")
        print("   3. Run: .\\build-unity-avatar.ps1")

    print("\n🎯 Unity Desktop Avatar Features:")
    print("   • VRM 1.0 avatar loading")
    print("   • Real-time animation control")
    print("   • Facial expression support")
    print("   • OSC communication (port 9000)")
    print("   • Transparent window overlay")
    print("   • Click-through mode")

    return 0


if __name__ == "__main__":
    sys.exit(main())
