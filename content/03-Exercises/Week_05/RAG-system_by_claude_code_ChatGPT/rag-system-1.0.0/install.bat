@echo off
REM RAG System Installation Script for Windows

setlocal enabledelayedexpansion

echo ======================================
echo     RAG System Installation Script    
echo ======================================
echo.

REM Configuration
set "INSTALL_DIR=%USERPROFILE%\.rag-system"
set "VENV_DIR=%INSTALL_DIR%\venv"
set "SCRIPT_DIR=%~dp0"

REM Check if we're in a distribution package or development environment
if exist "%SCRIPT_DIR%scripts" (
    REM Distribution package structure
    set "PROJECT_ROOT=%SCRIPT_DIR%"
) else (
    REM Development environment structure
    set "PROJECT_ROOT=%SCRIPT_DIR%.."
)

REM Check Python
echo Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Please install Python 3.8+ and try again.
    goto :error
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [OK] Python %PYTHON_VERSION% found

REM Create directories
echo Creating installation directories...
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"
if not exist "%INSTALL_DIR%\docs\originals" mkdir "%INSTALL_DIR%\docs\originals"
if not exist "%INSTALL_DIR%\knowledge\md" mkdir "%INSTALL_DIR%\knowledge\md"
if not exist "%INSTALL_DIR%\knowledge\index" mkdir "%INSTALL_DIR%\knowledge\index"
if not exist "%INSTALL_DIR%\scratch" mkdir "%INSTALL_DIR%\scratch"
echo [OK] Directories created

REM Copy files
echo Copying application files...

REM Copy scripts directory
if exist "%PROJECT_ROOT%\scripts" (
    xcopy /E /I /Y "%PROJECT_ROOT%\scripts" "%INSTALL_DIR%\scripts" >nul
    if %errorlevel% neq 0 goto :copy_error
) else (
    echo [ERROR] scripts directory not found in %PROJECT_ROOT%
    goto :copy_error
)

REM Copy main application file
if exist "%PROJECT_ROOT%\rag_system.py" (
    copy /Y "%PROJECT_ROOT%\rag_system.py" "%INSTALL_DIR%\" >nul
) else if exist "%SCRIPT_DIR%\rag_system.py" (
    copy /Y "%SCRIPT_DIR%\rag_system.py" "%INSTALL_DIR%\" >nul
) else (
    echo [ERROR] rag_system.py not found
    goto :copy_error
)

REM Copy requirements.txt
if exist "%PROJECT_ROOT%\requirements.txt" (
    copy /Y "%PROJECT_ROOT%\requirements.txt" "%INSTALL_DIR%\" >nul
) else (
    echo [ERROR] requirements.txt not found
    goto :copy_error
)

REM Copy documentation (optional)
if exist "%PROJECT_ROOT%\README.md" (
    copy /Y "%PROJECT_ROOT%\README.md" "%INSTALL_DIR%\" >nul
)
if exist "%PROJECT_ROOT%\CLAUDE.md" (
    copy /Y "%PROJECT_ROOT%\CLAUDE.md" "%INSTALL_DIR%\" >nul
)
echo [OK] Files copied

REM Create virtual environment
echo Creating Python virtual environment...
python -m venv "%VENV_DIR%"
echo [OK] Virtual environment created

REM Install dependencies
echo Installing Python dependencies...
echo This may take a few minutes...
call "%VENV_DIR%\Scripts\activate.bat"

echo   - Upgrading pip...
pip install --upgrade pip >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Failed to upgrade pip, continuing with existing version
)

echo   - Installing packages from requirements.txt...
pip install -r "%INSTALL_DIR%\requirements.txt"
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies
    echo Please check your internet connection and try again
    call "%VENV_DIR%\Scripts\deactivate.bat"
    goto :dep_error
)

call "%VENV_DIR%\Scripts\deactivate.bat"
echo [OK] Dependencies installed successfully

REM Create batch wrapper
echo Creating executable wrapper...
(
echo @echo off
echo set "INSTALL_DIR=%%USERPROFILE%%\.rag-system"
echo set "VENV_DIR=%%INSTALL_DIR%%\venv"
echo.
echo call "%%VENV_DIR%%\Scripts\activate.bat"
echo cd /d "%%INSTALL_DIR%%"
echo python rag_system.py %%*
echo call "%%VENV_DIR%%\Scripts\deactivate.bat"
) > "%INSTALL_DIR%\rag-system.bat"
echo [OK] Executable created

REM Add to PATH
echo Updating system PATH...
set "NEW_PATH=%INSTALL_DIR%"
for /f "tokens=2*" %%a in ('reg query "HKCU\Environment" /v PATH 2^>nul') do set "CURRENT_PATH=%%b"

echo !CURRENT_PATH! | findstr /C:"%INSTALL_DIR%" >nul
if %errorlevel% neq 0 (
    setx PATH "%CURRENT_PATH%;%INSTALL_DIR%" >nul 2>&1
    echo [OK] PATH updated
) else (
    echo [INFO] PATH already configured
)

echo.
echo ======================================
echo         Installation Complete!        
echo ======================================
echo.
echo To get started:
echo 1. Open a new Command Prompt window
echo 2. Add documents to: %INSTALL_DIR%\docs\originals\
echo 3. Run setup: rag-system setup
echo 4. Search: rag-system search "your query"
echo.
echo For help: rag-system --help
echo.

goto :end

:copy_error
echo.
echo Installation failed during file copy!
echo Please check that all required files are present in the package
exit /b 1

:dep_error
echo.
echo Installation failed during dependency installation!
echo You can try installing dependencies manually later with:
echo   call "%VENV_DIR%\Scripts\activate.bat"
echo   pip install -r "%INSTALL_DIR%\requirements.txt"
echo   call "%VENV_DIR%\Scripts\deactivate.bat"
exit /b 1

:error
echo.
echo Installation failed!
exit /b 1

:end
endlocal