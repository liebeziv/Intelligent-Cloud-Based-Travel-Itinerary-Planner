

Write-Host " Starting development services..." -ForegroundColor Green


Write-Host " Starting databases..." -ForegroundColor Yellow
docker-compose up -d mysql mongo redis

Write-Host " Waiting for databases..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

Write-Host " Development services ready!" -ForegroundColor Green
Write-Host ""
Write-Host "URLs:" -ForegroundColor Yellow
Write-Host "Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "Backend API: http://localhost:8000" -ForegroundColor White
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "To start applications:" -ForegroundColor Yellow
Write-Host "Frontend: cd frontend && npm run dev" -ForegroundColor White
Write-Host "Backend: cd backend && uvicorn app.main:app --reload" -ForegroundColor White
