# Windows开发环境设置脚本

Write-Host " Setting up development environment..." -ForegroundColor Green

# 检查前置条件
 = node --version 2>
 = python --version 2>
 = docker --version 2>

if (-not ) {
    Write-Host " Node.js is required but not installed." -ForegroundColor Red
    Write-Host "Please install Node.js from https://nodejs.org/" -ForegroundColor Yellow
    exit 1
}

if (-not ) {
    Write-Host " Python is required but not installed." -ForegroundColor Red
    Write-Host "Please install Python from https://python.org/" -ForegroundColor Yellow
    exit 1
}

if (-not ) {
    Write-Host " Docker is required but not installed." -ForegroundColor Red
    Write-Host "Please install Docker Desktop from https://docker.com/" -ForegroundColor Yellow
    exit 1
}

Write-Host " Prerequisites check passed" -ForegroundColor Green

# 设置前端
Write-Host " Installing frontend dependencies..." -ForegroundColor Yellow
Set-Location frontend
npm install
Set-Location ..

# 设置后端
Write-Host " Setting up backend..." -ForegroundColor Yellow
Set-Location backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Set-Location ..

# 复制环境文件
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host " Created .env file from example" -ForegroundColor Green
}

Write-Host " Development environment ready!" -ForegroundColor Green
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Update .env with your configurations" -ForegroundColor White
Write-Host "2. Run: .\scripts\start-dev.ps1" -ForegroundColor White
