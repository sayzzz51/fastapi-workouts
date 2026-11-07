# Workouts API

Backend-проект для отслеживания тренировочных упражнений по группам мышц и прогрессии весов в тренажёрном зале.

## Стек
- Python 3.15
- FastAPI
- PostgreSQL + psycopg 3
- Pydantic

## Возможности
- CRUD для упражнений (включая частичное обновление через PATCH)
- Фильтры по группе мышц и минимальному весу
- Статистика по каждой группе мышц: количество упражнений и максимальный вес
- Валидация входных данных через Pydantic
- Защита от SQL-инъекций через параметризованные запросы

## Эндпоинты

| Метод | Путь | Описание |
|---|---|---|
| GET | `/workouts` | Список упражнений. Фильтры: `?muscle_group=chest&min_weight=50` |
| GET | `/workouts/stats` | Количество упражнений и максимальный вес по каждой группе мышц |
| GET | `/workouts/{workout_id}` | Одно упражнение по id |
| POST | `/workouts` | Добавить упражнение |
| PUT | `/workouts/{workout_id}` | Полностью изменить упражнение |
| PATCH | `/workouts/{workout_id}` | Частично изменить упражнение |
| DELETE | `/workouts/{workout_id}` | Удалить упражнение |

## Как запустить

1. Клонировать репозиторий
```bash
git clone https://github.com/sayzzz51/fastapi-workouts.git
cd fastapi-workouts
```

2. Создать и активировать виртуальное окружение
```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Linux / macOS
```

3. Установить зависимости
```bash
pip install -r requirements.txt
```

4. Создать базу данных в PostgreSQL и выполнить в ней `schema.sql`
```sql
CREATE TABLE workouts (
    id SERIAL PRIMARY KEY,
    exercise VARCHAR(50) NOT NULL,
    muscle_group VARCHAR(50) NOT NULL CHECK (muscle_group IN ('chest', 'back', 'arms', 'legs')),
    weight INTEGER NOT NULL CHECK (weight >= 0),
    reps INTEGER NOT NULL CHECK (reps BETWEEN 1 AND 100)
);
```

5. Создать файл `.env` по примеру `.env.example`
```
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/YOUR_DB
```

6. Запустить сервер
```bash
uvicorn main:app --reload
```

Документация (Swagger) будет доступна на http://127.0.0.1:8000/docs

## Структура проекта
```
fastapi_workouts/
├── main.py            # создание приложения, подключение роутеров
├── db.py              # подключение к PostgreSQL
├── schemas.py         # Pydantic-модели
├── routers/
│   ├── __init__.py
│   └── workouts.py    # эндпоинты /workouts
├── schema.sql         # создание таблицы
├── requirements.txt
└── .env.example
```
