@echo off
REM Полный путь к uvicorn
set UVICORN_PATH=C:\Users\filat\Documents\projects\school_matcher\.conda\Scripts\uvicorn.exe

REM Полный путь к streamlit
set STREAMLIT_PATH=C:\Users\filat\Documents\projects\school_matcher\.conda\Scripts\streamlit.exe

REM Запуск FastAPI
start /b %UVICORN_PATH% app.main:app --reload

REM Запуск Streamlit
start %STREAMLIT_PATH% run streamlit_app/app.py

pause
