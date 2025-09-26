# Pre-commit hook for Spacecraft Subsystem Limits (PowerShell version)
# Automatically builds dist/ folder when limits/ folder changes are committed

Write-Host "🚀 Spacecraft Limits Pre-commit Hook" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan

# Check if any files in limits/ folder are being committed
$limitsChanged = git diff --cached --name-only | Where-Object { $_ -match "^limits/" }

if ($limitsChanged) {
    Write-Host "📁 Changes detected in limits/ folder:" -ForegroundColor Yellow
    $limitsChanged | ForEach-Object { Write-Host "   - $_" }
    Write-Host ""
    
    Write-Host "🔧 Running build script to update dist/ folder..." -ForegroundColor Blue
    
    # Run the build script
    $buildResult = python tools/build.py
    $buildExitCode = $LASTEXITCODE
    
    if ($buildExitCode -eq 0) {
        Write-Host ""
        Write-Host "✅ Build completed successfully!" -ForegroundColor Green
        
        # Check if dist files were generated/updated
        if ((Test-Path "dist/master.csv") -and (Test-Path "dist/latest.json") -and (Test-Path "dist/manifest.json")) {
            Write-Host "📦 Adding updated dist files to commit..." -ForegroundColor Blue
            
            # Temporarily unlock the files so git can read them
            try {
                Set-ItemProperty -Path "dist/master.csv" -Name IsReadOnly -Value $false
                Set-ItemProperty -Path "dist/latest.json" -Name IsReadOnly -Value $false  
                Set-ItemProperty -Path "dist/manifest.json" -Name IsReadOnly -Value $false
            } catch {
                # Ignore errors if files are already writable
            }
            
            # Add the updated dist files to the commit
            git add dist/master.csv dist/latest.json dist/manifest.json
            
            Write-Host "   - dist/master.csv"
            Write-Host "   - dist/latest.json"
            Write-Host "   - dist/manifest.json"
            Write-Host ""
            Write-Host "🔒 Dist files will be locked after commit completes" -ForegroundColor Magenta
        } else {
            Write-Host "❌ ERROR: Expected dist files were not generated" -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host ""
        Write-Host "❌ ERROR: Build script failed!" -ForegroundColor Red
        Write-Host "Commit aborted. Please fix the issues and try again." -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "ℹ️  No changes in limits/ folder - skipping build" -ForegroundColor Gray
}

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "✅ Pre-commit hook completed successfully" -ForegroundColor Green
