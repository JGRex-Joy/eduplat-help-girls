from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import User, About, Academic, Extracurricular
from app.schemas import (
    AboutRequest, AboutResponse,
    AcademicRequest, AcademicResponse,
    ExtracurricularRequest, ExtracurricularResponse,
)
from app.auth import get_current_user
from datetime import datetime

router = APIRouter(prefix="/profile", tags=["Profile"])


# ── About ─────────────────────────────────────────────────────────────────────

@router.post("/about", response_model=AboutResponse, status_code=201)
def upsert_about(
    data: AboutRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    about = db.query(About).filter(About.user_id == user.id).first()
    if not about:
        about = About(user_id=user.id)
        db.add(about)

    if data.name is not None:
        about.name = data.name
    if data.school is not None:
        about.school = data.school
    if data.grade is not None:
        about.grade = data.grade
    about.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(about)
    return about


@router.get("/about", response_model=AboutResponse)
def get_about(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    about = db.query(About).filter(About.user_id == user.id).first()
    if not about:
        raise HTTPException(404, "Информация о себе ещё не заполнена")
    return about


# ── Academic ──────────────────────────────────────────────────────────────────

@router.post("/academic", response_model=AcademicResponse, status_code=201)
def upsert_academic(
    data: AcademicRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    academic = db.query(Academic).filter(Academic.user_id == user.id).first()
    if not academic:
        academic = Academic(user_id=user.id)
        db.add(academic)

    if data.gpa is not None:
        academic.gpa = data.gpa
    if data.sat is not None:
        academic.sat = data.sat
    if data.ielts is not None:
        academic.ielts = data.ielts
    if data.toefl is not None:
        academic.toefl = data.toefl
    if data.act is not None:
        academic.act = data.act
    academic.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(academic)
    return academic


@router.get("/academic", response_model=AcademicResponse)
def get_academic(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    academic = db.query(Academic).filter(Academic.user_id == user.id).first()
    if not academic:
        raise HTTPException(404, "Академическая информация ещё не заполнена")
    return academic


# ── Extracurricular ───────────────────────────────────────────────────────────

@router.post("/extracurricular", response_model=List[ExtracurricularResponse], status_code=201)
def upsert_extracurricular(
    data: ExtracurricularRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Удаляем все старые записи и создаём новые
    db.query(Extracurricular).filter(Extracurricular.user_id == user.id).delete()

    entries = [
        Extracurricular(
            user_id=user.id,
            category=cat,
            years_active=data.years_active
        )
        for cat in data.categories
    ]
    db.add_all(entries)
    db.commit()
    return entries


@router.get("/extracurricular", response_model=List[ExtracurricularResponse])
def get_extracurricular(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Extracurricular).filter(Extracurricular.user_id == user.id).all()


@router.delete("/extracurricular/{entry_id}", status_code=204)
def delete_extracurricular(
    entry_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    entry = db.query(Extracurricular).filter(
        Extracurricular.id == entry_id,
        Extracurricular.user_id == user.id
    ).first()
    if not entry:
        raise HTTPException(404, "Запись не найдена")
    db.delete(entry)
    db.commit()
