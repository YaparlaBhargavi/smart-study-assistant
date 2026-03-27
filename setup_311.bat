@echo off
echo Setting up Smart Study Assistant with Python 3.11...

REM Check if Python 3.11 is installed
python --version | findstr "3.11" >nul
if errorlevel 1 (
    echo Downloading Python 3.11 installer...
    powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe' -OutFile 'python-3.11.9-amd64.exe'"
    python-3.11.9-amd64.exe /quiet InstallAllUsers=1 PrependPath=1
    del python-3.11.9-amd64.exe
    echo Python 3.11 installed. Restarting batch...
    timeout /t 5
    goto :eof
)

echo Python 3.11 ready. Creating virtual environment...
python -m venv venv

echo Activating venv and installing requirements...
call venv/Scripts/activate.bat
pip install --upgrade pip
pip install -r requirements.txt

echo Setup complete! Run 'call venv/Scripts/activate.bat && flask run' to start.
pause

