#!/bin/bash
# Startup script for the AI Quiz & Summarization System
# Supports both Linux/Mac and Windows (via Git Bash)

set -e

echo "========================================="
echo "🎓 AI Quiz & Summarization System Setup"
echo "========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Python is installed
echo "📦 Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 not found. Please install Python 3.9 or higher${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python 3 found$(python3 --version)${NC}"
echo ""

# Check if Node.js is installed
echo "📦 Checking Node.js installation..."
if ! command -v node &> /dev/null; then
    echo -e "${RED}Node.js not found. Please install Node.js 16 or higher${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Node.js found: $(node --version)${NC}"
echo ""

# Create and activate Python virtual environment
echo "🐍 Setting up Python virtual environment..."
cd ai_core
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${YELLOW}Virtual environment already exists${NC}"
fi

# Activate virtual environment
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi
echo -e "${GREEN}✓ Virtual environment activated${NC}"
echo ""

# Install Python dependencies
echo "📚 Installing Python dependencies..."
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
echo -e "${GREEN}✓ Python dependencies installed${NC}"
echo ""

# Create .env file if it doesn't exist
echo "⚙️  Configuring environment..."
if [ ! -f ".env" ]; then
    cp ../.env .env
    echo -e "${YELLOW}⚠️  .env file created - Please update DATABASE_URL with your PostgreSQL credentials${NC}"
else
    echo -e "${GREEN}✓ .env file exists${NC}"
fi
echo ""

# Initialize database
echo "🗄️  Initializing database..."
python -c "
from database import init_db
init_db()
print('✓ Database tables created')
"
echo ""

# Go back to root
cd ..

# Setup frontend
echo "⚛️  Setting up React frontend..."
cd frontend
if [ ! -d "node_modules" ]; then
    npm install
    echo -e "${GREEN}✓ Frontend dependencies installed${NC}"
else
    echo -e "${YELLOW}Frontend dependencies already installed${NC}"
fi
cd ..
echo ""

echo -e "${GREEN}========================================="
echo "✨ Setup Complete!"
echo "=========================================${NC}"
echo ""
echo "🚀 To start the system:"
echo ""
echo "Terminal 1 - Backend:"
echo "  cd ai_core"
echo "  source venv/bin/activate  # On Windows: venv\\Scripts\\activate"
echo "  python main.py"
echo ""
echo "Terminal 2 - Frontend:"
echo "  cd frontend"
echo "  npm run dev"
echo ""
echo "📍 Access the application:"
echo "  Frontend: http://localhost:5173"
echo "  Backend: http://localhost:8000"
echo "  API Docs: http://localhost:8000/api/docs"
echo ""
echo -e "${YELLOW}Important: Update .env with your PostgreSQL credentials before running${NC}"
echo ""
