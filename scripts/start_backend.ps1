# Start Well-Architected Backend Server
# Run this in a dedicated terminal to keep the backend running

Write-Host "Starting Azure Well-Architected Backend..." -ForegroundColor Cyan
Write-Host "Backend will be available at http://localhost:8000" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

Set-Location $PSScriptRoot
& "$PSScriptRoot\venv\Scripts\python.exe" -m uvicorn backend.server:app --host 0.0.0.0 --port 8000
