# Railway (API)

| Имя переменной | Значение |
|----------------|----------|
| `JWT_SECRET` | `замените-на-длинную-случайную-строку` |
| `DATABASE_URL` | *(только если есть Postgres — `${{Postgres.DATABASE_URL}}`)* |
| `CORS_MODE` | *(не задавать)* = любой сайт может ходить в API (CORS открыт). `strict` — только список ниже + Vercel по regex. |
| `CORS_ORIGINS` | *(только при `CORS_MODE=strict`)* `https://ВАШ-ФРОНТ.vercel.app,http://localhost:3000` |

# Vercel (Frontend) — обязательно

| Имя переменной | Значение |
|----------------|----------|
| `NEXT_PUBLIC_API_URL` | `https://ВАШ-API.up.railway.app` |

Без `/` в конце. Без этой переменной сборка ходит на `localhost` — с сайта Vercel запросы ломаются.

После добавления переменной на Vercel сделайте **Redeploy**.
