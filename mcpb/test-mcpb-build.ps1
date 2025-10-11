#!/usr/bin/env powershell
<#
.SYNOPSIS
    Test MCPB package build and validation

.DESCRIPTION
    This script tests the MCPB package build process and validates
    that all components are working correctly.

.PARAMETER FullTest
    Run full validation including package installation test

.EXAMPLE
    .\test-mcpb-build.ps1

.EXAMPLE
    .\test-mcpb-build.ps1 -FullTest
#>

param(
    [switch]$FullTest
)

# Set error action preference
$ErrorActionPreference = "Stop"

# Color output functions
function Write-ColorOutput {
    param([string]$Message, [string]$Color = "White")
    $originalColor = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $Color
    Write-Host $Message
    $host.UI.RawUI.ForegroundColor = $originalColor
}

function Write-Success { param([string]$Message) Write-ColorOutput $Message "Green" }
function Write-Error { param([string]$Message) Write-ColorOutput $Message "Red" }
function Write-Warning { param([string]$Message) Write-ColorOutput $Message "Yellow" }
function Write-Info { param([string]$Message) Write-ColorOutput $Message "Cyan" }

# Test functions
function Test-FileExists {
    param([string]$Path, [string]$Description)

    if (Test-Path $Path) {
        Write-Success "✅ $Description found: $Path"
        return $true
    }
    else {
        Write-Error "❌ $Description not found: $Path"
        return $false
    }
}

function Test-JsonValid {
    param([string]$Path, [string]$Description)

    try {
        $content = Get-Content $Path -Raw | ConvertFrom-Json
        Write-Success "✅ $Description is valid JSON"
        return $true
    }
    catch {
        Write-Error "❌ $Description is invalid JSON: $_"
        return $false
    }
}

function Test-MCPBCLI {
    try {
        $version = & mcpb --version 2>$null
        Write-Success "✅ MCPB CLI available: $version"
        return $true
    }
    catch {
        Write-Error "❌ MCPB CLI not found. Install with: npm install -g @anthropic-ai/mcpb"
        return $false
    }
}

function Test-Python {
    try {
        $version = & python --version 2>$null
        Write-Success "✅ Python available: $version"
        return $true
    }
    catch {
        Write-Error "❌ Python not found"
        return $false
    }
}

function Test-ManifestValidation {
    try {
        $result = & mcpb validate mcpb/manifest.json 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Success "✅ Manifest validation passed"
            return $true
        }
        else {
            Write-Error "❌ Manifest validation failed:"
            Write-Error $result
            return $false
        }
    }
    catch {
        Write-Error "❌ Manifest validation error: $_"
        return $false
    }
}

function Test-PackageBuild {
    param([string]$OutputDir = "./dist")

    # Create output directory
    if (!(Test-Path $OutputDir)) {
        New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
    }

    $packagePath = Join-Path $OutputDir "avatarmcp.mcpb"

    # Remove existing package
    if (Test-Path $packagePath) {
        Remove-Item $packagePath -Force
    }

    Write-Info "🔨 Building test MCPB package..."

    try {
        # Change to project root
        Push-Location (Split-Path -Parent (Split-Path -Parent $PSScriptRoot))

        # Build package
        $buildArgs = @("pack", "-c", "mcpb/mcpb.json", "-o", $packagePath, "--no-sign")
        $result = & mcpb $buildArgs 2>&1

        Pop-Location

        if ($LASTEXITCODE -eq 0 -and (Test-Path $packagePath)) {
            $fileSize = (Get-Item $packagePath).Length
            $fileSizeMB = [math]::Round($fileSize / 1MB, 2)
            Write-Success "✅ Package built successfully: $packagePath ($fileSizeMB MB)"
            return $true
        }
        else {
            Write-Error "❌ Package build failed:"
            Write-Error $result
            return $false
        }
    }
    catch {
        Write-Error "❌ Package build error: $_"
        Pop-Location
        return $false
    }
}

# Main test execution
function main {
    Write-Info "🧪 AvatarMCP MCPB Build Test"
    Write-Info "=" * 40
    Write-Info ""

    $allTestsPass = $true

    # Basic file checks
    Write-Info "📁 Checking files..."
    $allTestsPass = $allTestsPass -and (Test-FileExists "mcpb/manifest.json" "Manifest file")
    $allTestsPass = $allTestsPass -and (Test-FileExists "mcpb/mcpb.json" "MCPB config")
    $allTestsPass = $allTestsPass -and (Test-FileExists "mcpb/build-mcpb-package.ps1" "Build script")
    $allTestsPass = $allTestsPass -and (Test-FileExists "src/avatarmcp/mcp_main.py" "MCP entry point")
    $allTestsPass = $allTestsPass -and (Test-FileExists "pyproject.toml" "Python project config")
    Write-Info ""

    # JSON validation
    Write-Info "🔍 Validating JSON files..."
    $allTestsPass = $allTestsPass -and (Test-JsonValid "mcpb/manifest.json" "Manifest")
    $allTestsPass = $allTestsPass -and (Test-JsonValid "mcpb/mcpb.json" "MCPB config")
    $allTestsPass = $allTestsPass -and (Test-JsonValid "pyproject.toml" "Project config (partial)")
    Write-Info ""

    # Tool availability
    Write-Info "🔧 Checking tools..."
    $allTestsPass = $allTestsPass -and (Test-Python)
    $allTestsPass = $allTestsPass -and (Test-MCPBCLI)
    Write-Info ""

    # Manifest validation
    Write-Info "📋 Validating manifest..."
    $allTestsPass = $allTestsPass -and (Test-ManifestValidation)
    Write-Info ""

    # Build test
    Write-Info "📦 Testing package build..."
    $buildSuccess = Test-PackageBuild
    $allTestsPass = $allTestsPass -and $buildSuccess
    Write-Info ""

    # Full test (optional)
    if ($FullTest) {
        Write-Info "🔬 Running full validation..."

        # Test Python imports
        try {
            $pythonResult = & python -c "import sys; sys.path.insert(0, 'src'); import avatarmcp.mcp_main; print('✅ Python imports successful')" 2>&1
            if ($pythonResult -match "✅") {
                Write-Success "✅ Python imports successful"
            }
            else {
                Write-Error "❌ Python import failed:"
                Write-Error $pythonResult
                $allTestsPass = $false
            }
        }
        catch {
            Write-Error "❌ Python import test failed: $_"
            $allTestsPass = $false
        }

        Write-Info ""
    }

    # Results
    Write-Info "=" * 40
    if ($allTestsPass) {
        Write-Success "🎉 All tests passed! MCPB packaging is ready."
        Write-Info ""
        Write-Info "📦 Next steps:"
        Write-Info "1. Run: .\mcpb\build-mcpb-package.ps1 -NoSign"
        Write-Info "2. Test: Drag dist/avatarmcp.mcpb to Claude Desktop"
        Write-Info "3. Configure: Set VRM models directory"
        Write-Info "4. Use: Try 'avatar_list' command"
        Write-Info ""
        Write-Info "📚 Documentation: mcpb/README.md"
    }
    else {
        Write-Error "💥 Some tests failed. Please fix the issues above."
        Write-Info ""
        Write-Info "🔧 Common fixes:"
        Write-Info "- Install MCPB CLI: npm install -g @anthropic-ai/mcpb"
        Write-Info "- Check file paths and JSON syntax"
        Write-Info "- Ensure Python 3.9+ is available"
        Write-Info ""
        Write-Info "📚 See: mcpb/README.md for detailed troubleshooting"
        exit 1
    }
}

# Run main function
try {
    main
}
catch {
    Write-Error "💥 Test execution failed: $_"
    Write-Error "Stack trace: $($_.ScriptStackTrace)"
    exit 1
}
