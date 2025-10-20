@echo off
REM ========================================
REM STT Analytics - GitHub Deployment Script
REM ========================================

echo ========================================
echo STT Analytics - GitHub Deployment
echo ========================================
echo.

REM Check if git is installed
git --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Git not found. Please install Git from git-scm.com
    pause
    exit /b 1
)

echo [1/6] Checking repository status...
echo.

REM Check if git repo exists
if not exist .git (
    echo [!] Git repository not initialized
    echo Initializing git repository...
    git init
    git branch -M main
    echo.
)

echo [2/6] Copying deployment files...
echo.

REM Copy README for GitHub
if exist README_GITHUB.md (
    copy /Y README_GITHUB.md README.md
    echo ✓ README.md copied
)

REM Ensure deployment files exist
if not exist streamlit_app.py (
    echo [ERROR] streamlit_app.py not found!
    pause
    exit /b 1
)

if not exist requirements_streamlit.txt (
    echo [ERROR] requirements_streamlit.txt not found!
    pause
    exit /b 1
)

echo.
echo [3/6] Checking .gitignore...
echo.

REM Ensure important folders are in .gitignore
findstr /C:"data/" .gitignore >nul 2>&1
if errorlevel 1 (
    echo data/ >> .gitignore
    echo ✓ Added data/ to .gitignore
)

findstr /C:".venv/" .gitignore >nul 2>&1
if errorlevel 1 (
    echo .venv/ >> .gitignore
    echo ✓ Added .venv/ to .gitignore
)

findstr /C:"*.pyc" .gitignore >nul 2>&1
if errorlevel 1 (
    echo *.pyc >> .gitignore
    echo __pycache__/ >> .gitignore
    echo ✓ Added Python cache to .gitignore
)

echo.
echo [4/6] Adding files to git...
echo.

git add .
git status

echo.
echo [5/6] Creating commit...
echo.

set /p commit_msg="Enter commit message (or press Enter for default): "
if "%commit_msg%"=="" set commit_msg=Update STT Analytics Dashboard

git commit -m "%commit_msg%"

echo.
echo [6/6] Checking remote repository...
echo.

git remote -v | findstr origin >nul 2>&1
if errorlevel 1 (
    echo [!] No remote repository configured
    echo.
    echo Please add your GitHub repository:
    echo git remote add origin https://github.com/Majlo81/STT-dashboard.git
    echo.
    echo Then run:
    echo git push -u origin main
    pause
    exit /b 0
)

echo Remote repository configured:
git remote -v
echo.

set /p dopush="Push to GitHub now? (y/n): "
if /i "%dopush%"=="y" (
    echo Pushing to GitHub...
    git push -u origin main
    
    if errorlevel 1 (
        echo [ERROR] Push failed. You may need to:
        echo 1. Check your GitHub credentials
        echo 2. Ensure you have push access
        echo 3. Run: git pull origin main --rebase
        pause
        exit /b 1
    )
    
    echo.
    echo ========================================
    echo ✓ Successfully pushed to GitHub!
    echo ========================================
    echo.
    echo Next steps:
    echo 1. Go to https://share.streamlit.io
    echo 2. Click "New app"
    echo 3. Select repository: Majlo81/STT-dashboard
    echo 4. Main file: streamlit_app.py
    echo 5. Advanced settings:
    echo    - Requirements: requirements_streamlit.txt
    echo    - Python version: 3.10 or 3.11
    echo.
    echo See DEPLOYMENT.md for detailed instructions
    echo ========================================
) else (
    echo.
    echo Commit created but not pushed.
    echo To push manually, run:
    echo   git push -u origin main
)

echo.
pause
