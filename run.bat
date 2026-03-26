@echo off
REM Run Hospital Supply Chain ML System (Windows)

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Run the system
python main.py

REM Exit
call deactivate.bat
