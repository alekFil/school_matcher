FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5001

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5001"]
