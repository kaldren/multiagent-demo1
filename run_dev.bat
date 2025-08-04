@echo off
echo Starting development servers...

:: Start FastAPI server in background
echo Starting FastAPI server...
start "FastAPI Server" cmd /c "cd src\api && uvicorn main:app --reload --host 127.0.0.1 --port 8000"

:: Wait a moment for FastAPI to start
timeout /t 2 /nobreak > nul

:: Start React development server
echo Starting React development server...
cd src\web
npm start