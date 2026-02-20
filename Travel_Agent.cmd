@echo off
setlocal
cd /d "%~dp0"

if /I not "%OS%"=="Windows_NT" (
    echo This launcher is for Windows.
    goto :end
)

set "PYTHON_CMD="
where py >nul 2>&1
if %errorlevel%==0 (
    set "PYTHON_CMD=py"
) else (
    where python >nul 2>&1
    if %errorlevel%==0 set "PYTHON_CMD=python"
)

if "%PYTHON_CMD%"=="" (
    echo Python is not installed or not in PATH. Install Python 3.10+ and try again.
    goto :end
)

if not exist ".venv\Scripts\python.exe" (
    echo Creating local virtual environment (.venv^)...
    %PYTHON_CMD% -m venv .venv
    if errorlevel 1 goto :fail
)

set "VENV_PY=.venv\Scripts\python.exe"

%VENV_PY% -c "import smolagents,requests,dotenv,ddgs; from smolagents import DuckDuckGoSearchTool" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages (this may take a minute^)...
    %VENV_PY% -m pip install --upgrade pip || goto :fail
    %VENV_PY% -m pip install "smolagents[openai]" python-dotenv requests ddgs || goto :fail
)

if "%HUGGINGFACE_HUB_TOKEN%"=="" (
    if not exist ".env" (
        echo Missing Hugging Face token. Create .env with:
        echo HUGGINGFACE_HUB_TOKEN=hf_your_token_here
        goto :end
    )
    findstr /B /I "HUGGINGFACE_HUB_TOKEN=" ".env" >nul 2>&1
    if errorlevel 1 (
        echo Missing Hugging Face token. Create .env with:
        echo HUGGINGFACE_HUB_TOKEN=hf_your_token_here
        goto :end
    )
)

%VENV_PY% travel_agent.py
goto :end

:fail
echo Launcher failed with error code %errorlevel%.

:end
echo.
echo Press any key to close...
pause >nul
