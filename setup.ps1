$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "========================================"
Write-Host " Technical QA Lab - Environment Setup"
Write-Host "========================================"
Write-Host ""

# ----------------------------------------
# 1. Docker 설치 여부 확인
# ----------------------------------------

Write-Host "[1/5] Checking Docker..."

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "Docker is not installed."
    Write-Host "Please install Docker Desktop first."
    exit 1
}

docker info *> $null

if ($LASTEXITCODE -ne 0) {
    Write-Host "Docker Desktop is not running."
    Write-Host "Please start Docker Desktop and try again."
    exit 1
}

Write-Host "Docker is ready."
Write-Host ""


# ----------------------------------------
# 2. Random 값 생성 함수
# ----------------------------------------

function New-RandomHex {
    param (
        [int]$Bytes = 32
    )

    $data = New-Object byte[] $Bytes

    $rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()

    try {
        $rng.GetBytes($data)
    }
    finally {
        $rng.Dispose()
    }

    return -join ($data | ForEach-Object { $_.ToString("x2") })
}


# ----------------------------------------
# 3. .env 생성
# ----------------------------------------

Write-Host "[2/5] Checking environment variables..."

if (-not (Test-Path ".env")) {

    Write-Host ".env not found. Creating a new environment file..."

    $postgresPassword = New-RandomHex -Bytes 16
    $adminPassword = New-RandomHex -Bytes 16
    $jwtSecret = New-RandomHex -Bytes 32

    @"
POSTGRES_USER=qa_user
POSTGRES_PASSWORD=$postgresPassword
POSTGRES_DB=qa_lab

ADMIN_USERNAME=admin01
ADMIN_PASSWORD=$adminPassword

JWT_SECRET_KEY=$jwtSecret
"@ | Set-Content ".env"

    Write-Host ".env created."

    Write-Host ""
    Write-Host "Initial ADMIN credentials"
    Write-Host "Username : admin01"
    Write-Host "Password : $adminPassword"
    Write-Host ""
    Write-Host "Save this password for local testing."
}
else {
    Write-Host "Existing .env found. Keeping current values."
}

Write-Host ""


# ----------------------------------------
# 4. Docker Compose 실행
# ----------------------------------------

Write-Host "[3/5] Building and starting containers..."

docker compose up -d --build

if ($LASTEXITCODE -ne 0) {
    Write-Host "Docker Compose startup failed."
    exit 1
}

Write-Host ""
Write-Host "Containers started."
Write-Host ""


# ----------------------------------------
# 5. API Health Check
# ----------------------------------------

Write-Host "[4/5] Waiting for API..."

$healthUrl = "http://127.0.0.1:8000/db-health"
$maxRetries = 20
$success = $false

for ($i = 1; $i -le $maxRetries; $i++) {

    try {
        $response = Invoke-RestMethod `
            -Uri $healthUrl `
            -Method Get `
            -TimeoutSec 3

        if ($response.status -eq "ok") {
            $success = $true
            break
        }
    }
    catch {
        Start-Sleep -Seconds 2
    }
}

if (-not $success) {

    Write-Host ""
    Write-Host "API health check failed."
    Write-Host ""
    Write-Host "Check logs with:"
    Write-Host "docker compose logs api"
    exit 1
}


# ----------------------------------------
# 완료
# ----------------------------------------

Write-Host ""
Write-Host "[5/5] Environment verification completed."
Write-Host ""
Write-Host "========================================"
Write-Host " Technical QA Lab is ready"
Write-Host "========================================"
Write-Host ""
Write-Host "API      : http://127.0.0.1:8000"
Write-Host "Swagger  : http://127.0.0.1:8000/docs"
Write-Host "DB Check : http://127.0.0.1:8000/db-health"
Write-Host ""
Write-Host "Docker containers:"
docker compose ps
Write-Host ""