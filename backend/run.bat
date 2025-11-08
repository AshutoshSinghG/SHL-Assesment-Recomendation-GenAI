@echo off
REM Script to run the FastAPI backend server on Windows

REM Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else if exist env\Scripts\activate.bat (
    call env\Scripts\activate.bat
)

REM Run the server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

