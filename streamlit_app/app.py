import requests
import streamlit as st

st.set_page_config(layout="wide")

st.title(
    "Текущие результаты разработки модели для распознавания наименований спортивных школ"
)

school_name = st.text_input("Введите название школы")
region = st.text_input("Введите регион школы")

if st.button("Распознать наименование"):
    if school_name and region:
        response = requests.post(
            "http://45.67.59.211:5001/find_matches/",
            json={"school_name": school_name, "region": region},
        )
        if response.status_code == 200:
            matches = response.json()
            st.subheader("Предсказание")
            st.write(matches)
        else:
            st.write(response.status_code)
            st.write("Совпадения не найдены!")
    else:
        st.write("Пожалуйста, введите название и регион школы")
