# Сервис распознавания наименований школ

Этот проект реализует сервис распознавания наименований школ с использованием FastAPI и Streamlit. Сервис позволяет пользователям вводить название школы и регион, после чего возвращает совпадающие наименования школ из заранее определенной базы данных. Сервис упакован в Docker для удобного развертывания.

* **Демонстрация приложения**: [My Champion App](https://my-champion-app.streamlit.app/)
 <img src="images\my-champion-app.streamlit.app.gif" alt="covers">


## Установка и запуск

1. **Клонирование репозитория:**
   ```sh
   git clone https://github.com/alekfil/school-matcher.git
   cd school-name-recognition
   ```

2. **Сборка Docker-образа:**

   ```sh
   docker build -t school-matcher .
   ```

3. **Запуск Docker-контейнера:**

   ```sh
   docker run -d -p 5001:5001 school-matcher
   ```
   
4. **Доступ к приложению FastAPI:**

   ```text
   Откройте браузер и перейдите по адресу http://localhost:5001
   ```

5. **Документация API:**

   ```text
   Откройте браузер и перейдите по адресу http://localhost:5001/docs
   ```

6. **Направление запроса в API:**
Для направления запроса в API используйте любой HTTP-клиент, например, `curl`, `Postman` или библиотеки на Python, такие как `requests`.

   * Пример использования с curl

   ```sh
   curl -X POST "http://localhost:5001/find_matches/" -H "Content-Type: application/json" -d '{"school_name": "Примерная школа"}'
   ```

## Использование интерфейса сервиса при запущенном docker-контейнере
1. Создание виртуального окружения:
   ```sh
    python -m venv venv
    source venv/bin/activate   # Для Windows используйте `venv\Scripts\activate`
    ```

2. Установка зависимостей:
   ```sh
    pip install -r requirements_small.txt
    ```

3. Создание файла `.env` в корне проекта с содержимым:
   ```text
   API_URL = http://localhost:5001/
   ```

4. Запуск Streamlit приложение:
   ```sh
   streamlit run streamlit_app/app.py
   ```

## Быстрый локальный запуск без запуска docker-контейнера
1. Создание виртуального окружения:
   ```sh
    python -m venv venv
    source venv/bin/activate   # Для Windows используйте `venv\Scripts\activate`
    ```

2. Установка зависимостей:
   ```sh
    pip install -r requirements_small.txt
    ```

3. Создание файла `.env` в корне проекта с содержимым:
   ```text
   API_URL = http://localhost:5001/
   ```
   
4. Запуск скриптов `run_local_windows.bat` (windows) или `run_local.sh` (linux).

## Контакты
Автор проекта - Алексей Филатов: [telegram @alekFil](https://t.me/alekfil).