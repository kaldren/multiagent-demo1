#!/bin/bash

echo "Starting development servers..."

# Start FastAPI server in background
echo "Starting FastAPI server..."
cd src/api
uvicorn main:app --reload --host 127.0.0.1 --port 8000 &
FASTAPI_PID=$!

# Wait a moment for FastAPI to start
sleep 2

# Start React development server
echo "Starting React development server..."
cd ../web
npm start

# Clean up FastAPI process when script exits
trap "kill $FASTAPI_PID" EXIT