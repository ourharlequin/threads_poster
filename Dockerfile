# Используем легкий образ Python
FROM python:3.10-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем зависимости и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем все файлы проекта
COPY . .

# Создаем пустые файлы, если их нет, чтобы скрипты не падали
RUN touch posts.csv archive.csv

# По умолчанию запускаем паблишер
CMD ["python", "publisher.py"]