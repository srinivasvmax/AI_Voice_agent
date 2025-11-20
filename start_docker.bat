@echo off
echo ========================================
echo Starting Voice Agent with Docker
echo ========================================
echo.
echo Checking Docker...

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker is not running!
    echo.
    echo Please start Docker Desktop first.
    echo.
    pause
    exit /b 1
)

echo Docker is running!
echo.
echo Starting services...
echo - Llama Server: http://localhost:8080
echo - Voice Agent Web: http://localhost:8000
echo.
echo Press Ctrl+C to stop
echo.

cd docker
docker-compose up --build
