@echo off
setlocal
git pull
if errorlevel 1 goto :error
if not exist .venv (
  py -3 -m venv .venv
  if errorlevel 1 goto :error
)
call .venv\Scripts\activate.bat
if errorlevel 1 goto :error
pip install -r requirements.txt
if errorlevel 1 goto :error
python main.py
if errorlevel 1 goto :error
goto :eof

:error
echo.
echo [ERROR] Update/startup failed. Check messages above.
pause
exit /b 1
