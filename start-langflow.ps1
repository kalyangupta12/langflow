# Langflow Startup Script
Write-Host "Starting Langflow..." -ForegroundColor Green

# Load .env file
$envFile = Join-Path $PSScriptRoot ".env"
if (Test-Path $envFile) {
    Write-Host "Loading environment variables from .env..." -ForegroundColor Cyan
    Get-Content $envFile | ForEach-Object {
        if ($_ -match '^\s*([^#][^=]*?)\s*=\s*(.*?)\s*$') {
            $name = $matches[1]
            $value = $matches[2]
            $value = $value -replace '^"(.*)"$', '$1'
            $value = $value -replace "^'(.*)'$", '$1'
            [Environment]::SetEnvironmentVariable($name, $value, "Process")
            Write-Host "  + $name" -ForegroundColor DarkGray
        }
    }
}

# Add uv to PATH
$env:Path = "C:\Users\new\.local\bin;" + $env:Path

# Start Langflow
Write-Host ""
Write-Host "Starting Langflow server on http://127.0.0.1:7860" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

uv run langflow run --host 127.0.0.1 --port 7860
