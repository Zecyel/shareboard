#!/bin/bash

# Shareboard startup script
# This script starts both the backend and frontend servers

echo "Starting Shareboard..."
echo "========================="

# Check if Python and Node.js are available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python3 is not installed"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo "Error: npm is not installed"
    exit 1
fi

# Start backend server in background
echo "Starting FastAPI backend server on port 8000..."
cd backend
python3 -m pip install -r requirements.txt > /dev/null 2>&1
python3 main.py &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 2

# Start frontend server
echo "Starting Vue3 frontend server on port 5173..."
cd frontend
npm install > /dev/null 2>&1
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ Shareboard is starting up!"
echo "🔧 Backend API: http://localhost:8000"
echo "🌐 Frontend:    http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop both servers"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "Stopping servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "Shareboard stopped."
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Wait for either process to exit
wait