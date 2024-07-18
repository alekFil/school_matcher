import os

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")
api_url = os.getenv("API_URL")

st.set_page_config(layout="wide")

st.title("Имплементация сервиса распознавания наименований школ")

school_name = st.text_input("Введите название школы")
region = st.text_input("Введите регион школы (не обязательно)")
print(api_url)

if st.button("Распознать наименование"):
    if school_name:
        response = requests.post(
            api_url + "find_matches/",
            json={"school_name": school_name, "region": region},
        )
        if response.status_code == 200:
            matches = response.json()
            st.subheader("Результаты распознавания")
            st.write(matches)
        else:
            st.write(response.status_code)
            st.write("Ошибка работы сервиса... Сообщите разработчику")
    else:
        st.write("Пожалуйста, введите название и регион школы")
