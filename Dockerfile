# Сборка из корня монорепозитория (контекст = весь репозиторий).
# Для Railway: сервис получает явный образ вместо Railpack.
FROM python:3.11-slim

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

# Таблицы и сид создаются при старте приложения (main.py), здесь не дублируем — меньше точек отказа сборки

EXPOSE 8080

ENV PORT=8080
RUN chmod +x start.sh
CMD ["sh", "start.sh"]
