from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import get_db
from app.models import User, About, Academic, SavedUniversity, University
from app.schemas import DashboardResponse
from app.auth import get_current_user

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/", response_model=DashboardResponse)
def get_dashboard(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    about = db.query(About).filter(About.user_id == user.id).first()
    academic = db.query(Academic).filter(Academic.user_id == user.id).first()
    saved = db.query(SavedUniversity).filter(SavedUniversity.user_id == user.id).all()

    # Имя для приветствия
    name = (about.name.split()[0] if about and about.name else None)
    greeting = f"Привет, {name}👋" if name else "Привет👋"

    # Ближайший дедлайн среди сохранённых университетов
    days_to_deadline = None
    nearest_name = None

    if saved:
        uni_ids = [s.university_id for s in saved]
        unis = db.query(University).filter(
            University.id.in_(uni_ids),
            University.deadline_date != None,
            University.deadline_date > datetime.utcnow()
        ).order_by(University.deadline_date).all()

        if unis:
            nearest = unis[0]
            delta = nearest.deadline_date - datetime.utcnow()
            days_to_deadline = delta.days
            nearest_name = nearest.name

    # Проверка заполненности профиля
    profile_complete = bool(
        about and about.name and
        academic and academic.gpa
    )

    return DashboardResponse(
        greeting=greeting,
        days_to_nearest_deadline=days_to_deadline,
        nearest_deadline_university=nearest_name,
        saved_universities_count=len(saved),
        profile_complete=profile_complete,
    )
