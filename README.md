# Eduplat Backend API

FastAPI бэкенд для образовательной платформы **Eduplat**.

## Стек
- **Python 3.10+** + **FastAPI**
- **SQLite** (легко заменить на PostgreSQL)
- **SQLAlchemy** ORM
- **JWT** авторизация (PyJWT + bcrypt)
- **OpenAI GPT-4o-mini** для анализа мотивационных писем

---

## Быстрый старт

```bash
# 1. Клонируй или распакуй проект
cd eduplat-backend

# 2. Создай виртуальное окружение
python -m venv venv
source venv/bin/activate      # Mac/Linux
venv\Scripts\activate         # Windows

# 3. Установи зависимости
pip install -r requirements.txt

# 4. Настрой переменные окружения
cp .env.example .env
# Открой .env и вставь свой OPENAI_API_KEY

# 5. Запусти сервер
uvicorn main:app --reload --port 8000
```

База данных создаётся автоматически при первом запуске.
Тестовые данные (10 университетов, 6 возможностей) добавляются автоматически.

---

## Документация API

После запуска открой в браузере:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## Структура проекта

```
eduplat-backend/
├── main.py                        # Точка входа
├── requirements.txt
├── .env.example
└── app/
    ├── database.py                # Подключение к БД
    ├── models.py                  # SQLAlchemy модели
    ├── schemas.py                 # Pydantic схемы
    ├── auth.py                    # JWT утилиты
    ├── routers/
    │   ├── auth.py                # POST /auth/register, /auth/login
    │   ├── users.py               # GET /users/me
    │   ├── profile.py             # /profile/about, /academic, /extracurricular
    │   ├── universities.py        # /universities/ + сохранение
    │   ├── opportunities.py       # /opportunities/ + сохранение
    │   ├── dashboard.py           # GET /dashboard/
    │   ├── notifications.py       # GET /notifications/
    │   └── motivation_letter.py   # POST /motivation-letter/analyze
    └── services/
        ├── seed.py                # Тестовые данные
        └── probability.py         # Алгоритм расчёта вероятности
```

---

## Все эндпоинты

**Base URL:** `http://localhost:8000/api/v1`

Все эндпоинты кроме `/auth/*` требуют заголовок:
```
Authorization: Bearer <access_token>
```

### Auth
| Метод | Путь | Описание |
|-------|------|----------|
| POST | `/auth/register` | Создать аккаунт |
| POST | `/auth/login` | Войти, получить токен |

### Users
| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/users/me` | Полный профиль пользователя |
| DELETE | `/users/me` | Удалить аккаунт |

### Profile
| Метод | Путь | Описание |
|-------|------|----------|
| POST | `/profile/about` | Создать/обновить личную информацию |
| GET | `/profile/about` | Получить личную информацию |
| POST | `/profile/academic` | Создать/обновить академические данные |
| GET | `/profile/academic` | Получить академические данные |
| POST | `/profile/extracurricular` | Заменить все активности |
| GET | `/profile/extracurricular` | Список активностей |
| DELETE | `/profile/extracurricular/{id}` | Удалить одну запись |

### Universities
| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/universities/` | Список с фильтрами + вероятность поступления |
| GET | `/universities/countries` | Список стран |
| GET | `/universities/saved` | Моя доска университетов |
| GET | `/universities/{id}` | Детали университета |
| POST | `/universities/{id}/save` | Добавить на доску |
| DELETE | `/universities/{id}/save` | Убрать с доски |

**Query params для `/universities/`:**
- `country` — через запятую: `США,Германия`
- `label` — `Сложно`, `Средне`, `Реально`
- `sort_by` — `ranking`, `min_gpa`, `min_sat`, `min_ielts`, `probability`
- `sort_order` — `asc`, `desc`
- `search` — поиск по названию

### Opportunities
| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/opportunities/` | Лента возможностей |
| GET | `/opportunities/saved` | Сохранённые |
| GET | `/opportunities/{id}` | Детали |
| POST | `/opportunities/{id}/save` | Сохранить |
| DELETE | `/opportunities/{id}/save` | Убрать из сохранённых |

**Query params:** `type` (internship/volunteering/hackathon), `search`

### Dashboard
| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/dashboard/` | Главный экран: приветствие, дедлайны, счётчики |

### Notifications
| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/notifications/` | Все уведомления |
| PATCH | `/notifications/{id}/read` | Отметить как прочитанное |
| PATCH | `/notifications/read-all` | Отметить все как прочитанные |

### Motivation Letter
| Метод | Путь | Описание |
|-------|------|----------|
| POST | `/motivation-letter/analyze` | AI-анализ мотивационного письма |

---

## Алгоритм расчёта вероятности поступления

Учитывает GPA, SAT, IELTS/TOEFL пользователя относительно требований вуза.
Применяет коэффициент сложности: Сложно ×0.55, Средне ×0.80, Реально ×1.05.
Результат: от 1% до 99%.

---

## Переход на PostgreSQL

В `.env` замени:
```
DATABASE_URL=postgresql://user:password@localhost/eduplat
```

И установи:
```bash
pip install psycopg2-binary
```
