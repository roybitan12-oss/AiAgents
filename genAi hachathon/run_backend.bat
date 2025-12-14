@echo off
echo Installing dependencies...
pip install -r backend/requirements.txt

echo Starting Backend Server...
cd backend
uvicorn main:app --reload
pause
