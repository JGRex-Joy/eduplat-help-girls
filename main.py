from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine
from app.routers import auth, users, profile, universities, opportunities, dashboard, notifications, motivation_letter
from app.services.seed import seed

app = FastAPI(
    title="Eduplat API",
    description="Backend образовательной платформы Eduplat. FastAPI + SQLAlchemy.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем все роутеры
app.include_router(auth.router,               prefix="/api/v1")
app.include_router(users.router,              prefix="/api/v1")
app.include_router(profile.router,            prefix="/api/v1")
app.include_router(universities.router,       prefix="/api/v1")
app.include_router(opportunities.router,      prefix="/api/v1")
app.include_router(dashboard.router,          prefix="/api/v1")
app.include_router(notifications.router,      prefix="/api/v1")
app.include_router(motivation_letter.router,  prefix="/api/v1")


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    seed()


@app.get("/", tags=["Root"])
def root():
    return {
        "message": "Eduplat API работает!",
        "version": "1.0.0",
        "docs": "/docs",
    }
