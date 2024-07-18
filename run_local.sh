#!/bin/bash
# Запуск FastAPI
uvicorn app.main:app --reload &

# Запуск Streamlit
streamlit run streamlit_app/app.py
