#!/bin/bash

# Talent AI - Startup Script
# Launches both backend and frontend servers

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting Talent AI Platform...${NC}"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 is not installed. Please install Python 3.8+ first.${NC}"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js is not installed. Please install Node.js 16+ first.${NC}"
    exit 1
fi

# Install backend dependencies
echo -e "${YELLOW}📦 Installing backend dependencies...${NC}"
cd backend
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt --quiet
playwright install chromium --quiet

# Start backend server
echo -e "${GREEN}✅ Starting backend server on port 8100...${NC}"
uvicorn app:app --host 0.0.0.0 --port 8100 --reload &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"

# Install frontend dependencies
echo -e "${YELLOW}📦 Installing frontend dependencies...${NC}"
cd ../frontend
if [ ! -d "node_modules" ]; then
    npm install --silent
fi

# Start frontend server
echo -e "${GREEN}✅ Starting frontend server on port 3100...${NC}"
PORT=3100 npm start &
FRONTEND_PID=$!
echo "Frontend PID: $FRONTEND_PID"

# Wait a bit for servers to start
sleep 5

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}🎯 Talent AI is running!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "Frontend: ${GREEN}http://localhost:3100${NC}"
echo -e "Backend API: ${GREEN}http://localhost:8100${NC}"
echo -e "API Docs: ${GREEN}http://localhost:8100/docs${NC}"
echo ""
echo -e "Press ${YELLOW}Ctrl+C${NC} to stop all servers"
echo ""

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}Shutting down Talent AI...${NC}"
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo -e "${GREEN}✅ Talent AI stopped${NC}"
    exit 0
}

# Set trap to cleanup on Ctrl+C
trap cleanup INT

# Keep script running
wait $BACKEND_PID
wait $FRONTEND_PID