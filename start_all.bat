@echo off
set "VENV_PYTHON=%~dp0.venv\Scripts\python.exe"

echo === Starting services ===
start "Registration Service :8001" cmd /k ""%VENV_PYTHON%" -m uvicorn main:app --port 8001 --reload --app-dir "%~dp0registration_service""
start "Tournament Service   :8002" cmd /k ""%VENV_PYTHON%" -m uvicorn main:app --port 8002 --reload --app-dir "%~dp0tournament_service""
start "Feedback Service     :8003" cmd /k ""%VENV_PYTHON%" -m uvicorn main:app --port 8003 --reload --app-dir "%~dp0feedback_service""

echo.
echo Services started:
echo   Registration : http://localhost:8001/docs
echo   Tournament   : http://localhost:8002/docs
echo   Feedback     : http://localhost:8003/docs
