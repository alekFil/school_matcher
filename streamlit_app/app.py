import os

import requests
import streamlit as st
from dotenv import load_dotenv

# Загрузка переменных окружения из файла .env
load_dotenv(dotenv_path=".env")

# Получение URL API из переменных окружения
api_url = os.getenv("API_URL")

st.title("Имплементация сервиса распознавания наименований школ")
school_name = st.text_input("Введите название школы")

if st.button("Распознать наименование"):
    if school_name:
        # Отправка POST-запроса к API для распознавания наименования школы
        response = requests.post(
            api_url + "find_matches/",
            json={"school_name": school_name},
        )
        if response.status_code == 200:
            # Обработка успешного ответа от API
            matches = response.json()
            st.subheader("Результаты распознавания")
            st.write(matches)
        else:
            # Обработка ошибок при работе с API
            st.write(response.status_code)
            st.write("Ошибка работы сервиса... Сообщите разработчику")
    else:
        # Вывод сообщения, если не введено название школы
        st.write("Пожалуйста, введите название школы")
