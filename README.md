# wedding_backend

Простейший backend на FastAPI для регистрации гостей на свадьбу.

## Быстрый старт

```bash
.venv\Scripts\Activate.ps1
pip install -e .
uvicorn wedding_backend.main:app --reload
```

## Docker

Запуск через Docker Compose:

```bash
docker compose up --build -d
```

Сервис будет доступен на `http://localhost:7777`.

Остановка:

```bash
docker compose down
```

Переменная `WEDDING_API_KEY` берётся из `.env`.
Файл с ответами монтируется с хоста: `./guests.json -> /app/guests.json`.

## API

### Authorization

Все методы требуют заголовок `Authorization`.

Ключ берётся из переменной окружения `WEDDING_API_KEY`.

Для локальной разработки создай `.env` в корне проекта:

```text
WEDDING_API_KEY=wdg_8f21d77b4b8a4d98
```

Можно передавать как:
- `Authorization: wdg_8f21d77b4b8a4d98`
- `Authorization: Bearer wdg_8f21d77b4b8a4d98`

Если заголовка нет или ключ неверный, API вернёт `401`.

### `POST /guests`

Тело запроса:

```json
{
	"guests": ["Иван Иванов", "Мария Петрова"],
	"attendance": 1
}
```

`attendance`:
- `1` — Да, с удовольствием
- `2` — К сожалению не смогу
- `3` — Отвечу позже (до 25.04.2026)

Ответы сохраняются в локальный файл `guests.json` в корне проекта.

### `GET /guests`

Возвращает список всех гостей с их ответами.

### `GET /guests/csv`

Возвращает CSV-файл со списком гостей и их ответами.
Колонки: `guest`, `attendance`, `attendance_label`.
