#!/usr/bin/env powershell
<#
.SYNOPSIS
    Build MCPB package for AvatarMCP server

.DESCRIPTION
    This script builds a complete MCPB (MCP Bundle) package for the AvatarMCP server.
    It validates prerequisites, builds the package, and optionally signs it.

.PARAMETER OutputDir
    Output directory for the built package (default: ./dist)

.PARAMETER NoSign
    Skip package signing (for development builds)

.PARAMETER Clean
    Clean output directory before building

.EXAMPLE
    .\build-mcpb-package.ps1

.EXAMPLE
    .\build-mcpb-package.ps1 -OutputDir "C:\builds" -NoSign

.EXAMPLE
    .\build-mcpb-package.ps1 -Clean
#>

param(
    [string]$OutputDir = "./dist",
    [switch]$NoSign,
    [switch]$Clean
)

# Set error action preference
$ErrorActionPreference = "Stop"

# Color output functions
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    $originalColor = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $Color
    Write-Host $Message
    $host.UI.RawUI.ForegroundColor = $originalColor
}

function Write-Success { param([string]$Message) Write-ColorOutput $Message "Green" }
function Write-Error { param([string]$Message) Write-ColorOutput $Message "Red" }
function Write-Warning { param([string]$Message) Write-ColorOutput $Message "Yellow" }
function Write-Info { param([string]$Message) Write-ColorOutput $Message "Cyan" }

# Script variables
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDir
$manifestPath = Join-Path $scriptDir "manifest.json"
$mcpbConfigPath = Join-Path $scriptDir "mcpb.json"
$packageName = "avatarmcp"
$version = "0.1.0"

Write-Info "ðŸ”¨ AvatarMCP MCPB Package Builder"
Write-Info "=================================="

# Prerequisites check
function Test-Prerequisites {
    Write-Info "ðŸ“‹ Checking prerequisites..."

    # Check Node.js and npm
    try {
        $nodeVersion = & node --version 2>$null
        $npmVersion = & npm --version 2>$null
        Write-Success "âœ… Node.js: $nodeVersion"
        Write-Success "âœ… npm: $npmVersion"
    }
    catch {
        Write-Error "âŒ Node.js/npm not found. Please install Node.js from https://nodejs.org/"
        exit 1
    }

    # Check MCPB CLI
    try {
        $mcpbVersion = & mcpb --version 2>$null
        Write-Success "âœ… MCPB CLI: $mcpbVersion"
    }
    catch {
        Write-Warning "âš ï¸  MCPB CLI not found. Installing @anthropic-ai/mcpb..."
        try {
            & npm install -g @anthropic-ai/mcpb
            Write-Success "âœ… MCPB CLI installed successfully"
        }
        catch {
            Write-Error "âŒ Failed to install MCPB CLI. Please install manually: npm install -g @anthropic-ai/mcpb"
            exit 1
        }
    }

    # Check Python
    try {
        $pythonVersion = & python --version 2>$null
        Write-Success "âœ… Python: $pythonVersion"
    }
    catch {
        Write-Error "âŒ Python not found. Please install Python 3.9+ from https://python.org/"
        exit 1
    }

    # Check configuration files
    if (!(Test-Path $manifestPath)) {
        Write-Error "âŒ manifest.json not found at $manifestPath"
        exit 1
    }
    Write-Success "âœ… manifest.json found"

    if (!(Test-Path $mcpbConfigPath)) {
        Write-Error "âŒ mcpb.json not found at $mcpbConfigPath"
        exit 1
    }
    Write-Success "âœ… mcpb.json found"

    Write-Success "ðŸŽ‰ All prerequisites satisfied!"
}

# Validate manifest
function Test-Manifest {
    Write-Info "ðŸ” Validating manifest.json..."

    try {
        $validationResult = & mcpb validate $manifestPath 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Success "âœ… Manifest validation passed"
        }
        else {
            Write-Error "âŒ Manifest validation failed:"
            Write-Error $validationResult
            exit 1
        }
    }
    catch {
        Write-Error "âŒ Manifest validation error: $_"
        exit 1
    }
}

# Clean output directory
function Clear-OutputDirectory {
    if ($Clean -and (Test-Path $OutputDir)) {
        Write-Info "ðŸ§¹ Cleaning output directory: $OutputDir"
        Remove-Item -Recurse -Force $OutputDir -ErrorAction SilentlyContinue
    }

    # Create output directory
    if (!(Test-Path $OutputDir)) {
        New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
        Write-Success "ðŸ“ Created output directory: $OutputDir"
    }
}

# Build MCPB package
function New-MCPBPackage {
    Write-Info "ðŸ“¦ Building MCPB package..."

    $packagePath = Join-Path $OutputDir "$packageName.mcpb"

    # Remove existing package if it exists
    if (Test-Path $packagePath) {
        Remove-Item $packagePath -Force
    }

    # Change to project root for relative paths to work
    Push-Location $projectRoot

    try {
        $buildArgs = @("pack", "-c", $mcpbConfigPath, "-o", $packagePath)

        if ($NoSign) {
            $buildArgs += "--no-sign"
            Write-Info "ðŸ”“ Building without signing (development mode)"
        }
        else {
            Write-Info "ðŸ” Building with signing (production mode)"
        }

        $buildResult = & mcpb $buildArgs 2>&1

        if ($LASTEXITCODE -eq 0) {
            Write-Success "âœ… MCPB package built successfully"
            Write-Success "ðŸ“¦ Package: $packagePath"
        }
        else {
            Write-Error "âŒ MCPB build failed:"
            Write-Error $buildResult
            exit 1
        }
    }
    finally {
        Pop-Location
    }
}

# Verify package
function Test-Package {
    param([string]$PackagePath)

    Write-Info "ðŸ” Verifying package..."

    if (!(Test-Path $PackagePath)) {
        Write-Error "âŒ Package not found: $PackagePath"
        exit 1
    }

    # Check file size
    $fileSize = (Get-Item $PackagePath).Length
    $fileSizeMB = [math]::Round($fileSize / 1MB, 2)

    Write-Success "âœ… Package exists: $PackagePath"
    Write-Success "ðŸ“ Package size: $fileSizeMB MB"

    # Basic validation (check if it's a valid MCPB file)
    try {
        $packageInfo = & mcpb info $PackagePath 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Success "âœ… Package validation passed"
            Write-Info "ðŸ“‹ Package info:"
            Write-Info $packageInfo
        }
        else {
            Write-Warning "âš ï¸  Package validation warning:"
            Write-Warning $packageInfo
        }
    }
    catch {
        Write-Warning "âš ï¸  Could not validate package info: $_"
    }
}

# Main execution
function main {
    Write-Info "ðŸš€ Starting AvatarMCP MCPB build process..."
    Write-Info ""

    # Prerequisites
    Test-Prerequisites
    Write-Info ""

    # Validation
    Test-Manifest
    Write-Info ""

    # Clean and prepare
    Clear-OutputDirectory
    Write-Info ""

    # Build
    New-MCPBPackage
    Write-Info ""

    # Verify
    $finalPackagePath = Join-Path $OutputDir "$packageName.mcpb"
    Test-Package $finalPackagePath
    Write-Info ""

    # Summary
    Write-Success "ðŸŽ‰ Build completed successfully!"
    Write-Success "ðŸ“¦ Package: $finalPackagePath"
    Write-Success "ðŸ“ Version: $version"
    Write-Success "ðŸ› ï¸  Tools: 21 MCP tools available"

    if ($NoSign) {
        Write-Warning "âš ï¸  Package built without signing (development mode)"
        Write-Info "ðŸ’¡ For production use, run without -NoSign flag to enable signing"
    }

    Write-Info ""
    Write-Info "ðŸ“š Next steps:"
    Write-Info "1. Test the package: Drag $finalPackagePath to Claude Desktop"
    Write-Info "2. Configure settings: Set VRM models directory and OSC preferences"
    Write-Info "3. Try the tools: Use avatar_load, animation_play, etc."
    Write-Info ""
    Write-Info "ðŸ”- Documentation: See docs/mcpb-packaging/README.md"
}

# Run main function
try {
    main
}
catch {
    Write-Error "ðŸ’¥ Build failed with error: $_"
    Write-Error "Stack trace: $($_.ScriptStackTrace)"
    exit 1
}
