FROM python:3.14-slim

# Отключение проверки обновлений pip
ENV PIP_DISABLE_PIP_VERSION_CHECK 1
# Установка запрета на создание pyc-файлов
ENV PYTHONDONTWRITEBYTECODE 1
# Установка запрета на буферизацию Докером консольного вывода
ENV PYTHONUNBUFFERED 1

WORKDIR /code
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

EXPOSE 8000

ENTRYPOINT python manage.py runserver 0.0.0.0:8000