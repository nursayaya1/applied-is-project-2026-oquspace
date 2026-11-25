# Информационная система Jasyl

**Курс:** Прикладное программное обеспечение информационных систем, 2026 г.

**Автор:** Нұрсая Жұматай, группа ИС 24 а1

## Описание предметной области

Jasyl помогает вести домашнюю коллекцию растений. Я могу добавить растение, указать его комнату, категорию и период полива. В журнале сохраняются выполненные действия по уходу. Поиск и фильтры помогают быстро найти нужное растение.

## Архитектура данных

![ER-диаграмма](docs/er-diagram.png)

- Category — категория растений, связь один ко многим с Plant.
- Room — комната, связь один ко многим с Plant.
- Plant — растение, связь один ко многим с CareLog.
- CareLog — запись об уходе за растением.

## Технологический стек

Python 3.11+, FastAPI, Uvicorn, SQLite, SQLModel, Streamlit, Requests, Docker Compose, pytest. ИИ-помощник использован для подготовки структуры и проверки кода.

## Локальный запуск

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux / macOS: source .venv/bin/activate
pip install -r requirements.txt
python -m app.database.seed
uvicorn app.main:app --reload
```

В другом терминале с активным окружением:

```bash
streamlit run app/frontend/ui.py
```

Интерфейс: http://localhost:8501. Swagger: http://localhost:8000/docs.

## Запуск в Docker

```bash
docker compose up --build
```

Данные сохраняются в томе `jasyl_data`. Команда `docker compose down` не удаляет этот том.

## Тестирование

```bash
python -m pytest -q
```

Тесты используют отдельную базу в памяти и не изменяют коллекцию.
