@echo off
echo === Installing dependencies ===
pip install fastapi uvicorn pyodbc python-dotenv

echo.
echo === Initialising database schemas ===
cd registration_service
python init_db.py
cd ..

cd tournament_service
python init_db.py
cd ..

cd feedback_service
python init_db.py
cd ..

echo.
echo === Starting services ===
start "Registration Service :8001" cmd /k "cd /d %~dp0registration_service && python -m uvicorn main:app --port 8001 --reload"
start "Tournament Service   :8002" cmd /k "cd /d %~dp0tournament_service   && python -m uvicorn main:app --port 8002 --reload"
start "Feedback Service     :8003" cmd /k "cd /d %~dp0feedback_service     && python -m uvicorn main:app --port 8003 --reload"

echo.
echo Services started:
echo   Registration : http://localhost:8001/docs
echo   Tournament   : http://localhost:8002/docs
echo   Feedback     : http://localhost:8003/docs
