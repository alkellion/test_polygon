FROM python:3.11-slim

WORKDIR /app

COPY . .

# Установим зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Устанавливаем переменные окружения из .env
ENV DOTENV_PATH=.env


# Открываем порт
EXPOSE 8080

CMD ["python", "server.py"]
