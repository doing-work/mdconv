@echo off
REM Quick test script for Docker container (Windows)

echo ==========================================
echo Testing mdconv Docker Container
echo ==========================================
echo.

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo Error: Docker is not running
    exit /b 1
)

REM Build the image
echo Building Docker image...
docker build -t mdconv-api .

REM Start container in background
echo Starting container...
docker run -d --name mdconv-test -p 8000:8000 mdconv-api

REM Wait for container to be ready
echo Waiting for API to be ready...
timeout /t 5 /nobreak >nul

REM Test health endpoint
echo Testing health endpoint...
curl -f http://localhost:8000/health >nul 2>&1
if errorlevel 1 (
    echo Health check failed
    docker logs mdconv-test
    docker stop mdconv-test
    docker rm mdconv-test
    exit /b 1
) else (
    echo Health check passed
)

REM Test formats endpoint
echo Testing formats endpoint...
curl -f http://localhost:8000/formats >nul 2>&1
if errorlevel 1 (
    echo Formats endpoint failed
) else (
    echo Formats endpoint working
)

REM Run Python test script if available
if exist "test_docker_conversions.py" (
    echo Running comprehensive conversion tests...
    python test_docker_conversions.py --all-formats
)

REM Cleanup
echo Stopping and removing container...
docker stop mdconv-test
docker rm mdconv-test

echo.
echo ==========================================
echo Docker test completed!
echo ==========================================
