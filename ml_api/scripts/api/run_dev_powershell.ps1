# Get the directory where the script is located
$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$BASE_DIR = Split-Path -Parent (Split-Path -Parent $SCRIPT_DIR)
$SRC_DIR = Join-Path $BASE_DIR "src"

Write-Host "BASE_DIR: $BASE_DIR"
Write-Host "SRC_DIR: $SRC_DIR"

# Load environment variables from .env file
$envFile = Join-Path $SRC_DIR ".env"
if (Test-Path $envFile) {
    Get-Content $envFile | ForEach-Object {
        if ($_ -match '^([^#][^=]+)=(.*)$') {
            $name = $matches[1]
            $value = $matches[2]
            Set-Variable -Name $name -Value $value -Scope Global
            [Environment]::SetEnvironmentVariable($name, $value)
        }
    }
}

# Use API_PORT from .env or default to 8001
$PORT = if ($env:API_PORT) { $env:API_PORT } else { "8001" }

Write-Host "# Running fraud-detection-ml-api in dev mode"
Write-Host ""

uvicorn src.app:app --host=0.0.0.0 --port $PORT --reload 