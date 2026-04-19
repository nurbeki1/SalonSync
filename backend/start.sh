#!/bin/sh
# Start Telegram bot in background
python -m bot.main &

# Start FastAPI
exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}