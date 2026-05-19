@echo off
REM Startup script for the AI Quiz & Summarization System (Windows)

echo.
echo =========================================
echo 🎓 AI Quiz ^& Summarization System Setup
echo =========================================
echo.

REM Check if Python is installed
echo 📦 Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo Python 3 not found. Please install Python 3.9 or higher
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo ✓ %PYTHON_VERSION% found
echo.

REM Check if Node.js is installed
echo 📦 Checking Node.js installation...
node --version >nul 2>&1
if errorlevel 1 (
    echo Node.js not found. Please install Node.js 16 or higher
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('node --version') do set NODE_VERSION=%%i
echo ✓ Node.js %NODE_VERSION% found
echo.

REM Create and activate Python virtual environment
echo 🐍 Setting up Python virtual environment...
cd ai_core
if not exist "venv" (
    python -m venv venv
    echo ✓ Virtual environment created
) else (
    echo ✓ Virtual environment already exists
)

REM Activate virtual environment
call venv\Scripts\activate.bat
echo ✓ Virtual environment activated
echo.

REM Install Python dependencies
echo 📚 Installing Python dependencies...
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
echo ✓ Python dependencies installed
echo.

REM Create .env file if it doesn't exist
echo ⚙️  Configuring environment...
if not exist ".env" (
    copy ..\. .env >nul
    echo ⚠️  .env file created - Please update DATABASE_URL with your PostgreSQL credentials
) else (
    echo ✓ .env file exists
)
echo.

REM Initialize database
echo 🗄️  Initializing database...
python -c "from database import init_db; init_db(); print('✓ Database tables created')"
echo.

REM Go back to root
cd ..

REM Setup frontend
echo ⚛️  Setting up React frontend...
cd frontend
if not exist "node_modules" (
    call npm install
    echo ✓ Frontend dependencies installed
) else (
    echo ✓ Frontend dependencies already installed
)
cd ..
echo.

echo.
echo =========================================
echo ✨ Setup Complete!
echo =========================================
echo.
echo 🚀 To start the system:
echo.
echo Terminal 1 - Backend:
echo   cd ai_core
echo   venv\Scripts\activate
echo   python main.py
echo.
echo Terminal 2 - Frontend:
echo   cd frontend
echo   npm run dev
echo.
echo 📍 Access the application:
echo   Frontend: http://localhost:5173
echo   Backend: http://localhost:8000
echo   API Docs: http://localhost:8000/api/docs
echo.
echo ⚠️  Important: Update .env with your PostgreSQL credentials before running
echo.
pause
