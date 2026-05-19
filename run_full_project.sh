#!/bin/bash
set -e
ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

echo "========================================="
echo "Starting full project: AI Core + Backend + Frontend"
echo "========================================="

echo "\nPreparing Python virtual environment for ai_core..."
if [ ! -d "ai_core/venv" ]; then
  python3 -m venv ai_core/venv
fi

source ai_core/venv/bin/activate

echo "Starting ai_core service..."
(cd ai_core && python server.py) &
AI_CORE_PID=$!

echo "Starting Express backend service..."
(cd backend && if [ ! -d "node_modules" ]; then npm install; fi && npm run dev) &
BACKEND_PID=$!

echo "Starting React frontend service..."
(cd frontend && if [ ! -d "node_modules" ]; then npm install; fi && npm run dev) &
FRONTEND_PID=$!

echo "\nAll services are starting..."
echo "Frontend: http://localhost:5173"
echo "AI Core: http://localhost:5000"
echo "Express backend: http://localhost:3001"
echo ""
echo "Press Ctrl+C to stop all services."

wait ${AI_CORE_PID} ${BACKEND_PID} ${FRONTEND_PID}
