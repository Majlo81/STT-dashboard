@echo off
REM STT Analytics Platform - One-Click Launcher
REM Phase 1: Full pipeline execution (ingest, compute, dashboard)

setlocal enabledelayedexpansion

echo ========================================
echo STT Analytics Platform - One-Click Run
echo ========================================
echo.

REM Check Python installation
py --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.10+ from python.org
    pause
    exit /b 1
)

REM Create/activate virtual environment
if not exist .venv (
    echo [1/5] Creating virtual environment...
    py -m venv .venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
    
    call .venv\Scripts\activate
    
    echo [2/5] Upgrading pip...
    python -m pip install --upgrade pip --quiet
    
    echo [3/5] Installing dependencies...
    pip install -r requirements.txt --quiet
    
    echo [INFO] Virtual environment created successfully
    echo.
) else (
    echo [1/5] Activating existing virtual environment...
    call .venv\Scripts\activate
    
    REM Check if dependencies are installed
    python -c "import typer" 2>nul
    if errorlevel 1 (
        echo [2/5] Upgrading pip...
        python -m pip install --upgrade pip --quiet
        
        echo [3/5] Installing dependencies...
        pip install -r requirements.txt --quiet
        
        echo [INFO] Dependencies installed successfully
    ) else (
        echo [2/5] Dependencies already installed
    )
    echo.
)

REM Create directory structure if missing
if not exist data\raw mkdir data\raw
if not exist data\clean mkdir data\clean
if not exist artifacts\reports mkdir artifacts\reports
if not exist artifacts\charts mkdir artifacts\charts

REM Check if raw data exists
set RAW_COUNT=0
for %%f in (data\raw\*.csv) do set /a RAW_COUNT+=1

if %RAW_COUNT%==0 (
    echo [WARNING] No CSV files found in data/raw/
    echo Please place your CSV files in data/raw/ directory
    echo.
    echo Press any key to open data/raw folder...
    pause >nul
    explorer data\raw
    echo.
    echo After adding CSV files, run this script again.
    pause
    exit /b 0
)

echo [INFO] Found %RAW_COUNT% CSV file(s) in data/raw/
echo.

REM Step 1: Ingest & Clean
echo [4/5] Ingesting and cleaning data...
python -m stta.cli ingest --input data/raw --output data/clean
if errorlevel 1 (
    echo [ERROR] Data ingestion failed. Check artifacts/run.log for details.
    pause
    exit /b 1
)
echo [INFO] Data cleaning completed
echo.

REM Step 2: Compute Metrics
echo [5/5] Computing metrics...
python -m stta.cli compute --data data/clean
if errorlevel 1 (
    echo [ERROR] Metrics computation failed. Check artifacts/run.log for details.
    pause
    exit /b 1
)
echo [INFO] Metrics computed successfully
echo.

REM Step 3: Launch Dashboard
echo ========================================
echo Starting Streamlit Dashboard...
echo ========================================
echo.
echo Dashboard will open in your default browser.
echo Press Ctrl+C in this window to stop the server.
echo.

start "" streamlit run stta/dashboard/app.py -- --data data/clean

REM Keep window open
echo.
echo Dashboard running. Close this window to stop the server.
pause >nul

endlocal
