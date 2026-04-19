from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import User, University, Academic, SavedUniversity
from app.schemas import UniversityResponse
from app.auth import get_current_user
from app.services.probability import calculate_probability

router = APIRouter(prefix="/universities", tags=["Universities"])


def build_response(uni: University, academic, saved_ids: set) -> UniversityResponse:
    return UniversityResponse(
        id=uni.id,
        name=uni.name,
        country=uni.country,
        city=uni.city,
        min_gpa=uni.min_gpa,
        min_sat=uni.min_sat,
        min_ielts=uni.min_ielts,
        min_toefl=uni.min_toefl,
        probability=calculate_probability(uni, academic),
        label=uni.label,
        color=uni.color,
        full_description=uni.full_description,
        website=uni.website,
        logo_url=uni.logo_url,
        deadline=uni.deadline,
        ranking=uni.ranking,
        is_saved=(uni.id in saved_ids),
    )


@router.get("/countries", response_model=List[str])
def get_countries(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.query(University.country).distinct().order_by(University.country).all()
    return [r[0] for r in rows]


@router.get("/", response_model=List[UniversityResponse])
def list_universities(
    country: Optional[str] = Query(None),
    label: Optional[str] = Query(None),
    sort_by: str = Query("ranking", pattern="^(ranking|min_gpa|min_sat|min_ielts|probability)$"),
    sort_order: str = Query("asc", pattern="^(asc|desc)$"),
    search: Optional[str] = Query(None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(University)

    if country:
        countries = [c.strip() for c in country.split(",")]
        query = query.filter(University.country.in_(countries))
    if label:
        labels = [l.strip() for l in label.split(",")]
        query = query.filter(University.label.in_(labels))
    if search:
        query = query.filter(University.name.ilike(f"%{search}%"))

    universities = query.all()

    academic = db.query(Academic).filter(Academic.user_id == user.id).first()
    saved = db.query(SavedUniversity).filter(SavedUniversity.user_id == user.id).all()
    saved_ids = {s.university_id for s in saved}

    result = [build_response(u, academic, saved_ids) for u in universities]

    # Сортировка
    reverse = sort_order == "desc"
    if sort_by == "probability":
        result.sort(key=lambda x: x.probability or 0, reverse=reverse)
    elif sort_by == "ranking":
        result.sort(key=lambda x: x.ranking or 9999, reverse=reverse)
    elif sort_by == "min_gpa":
        result.sort(key=lambda x: x.min_gpa or 0, reverse=reverse)
    elif sort_by == "min_sat":
        result.sort(key=lambda x: x.min_sat or 0, reverse=reverse)
    elif sort_by == "min_ielts":
        result.sort(key=lambda x: x.min_ielts or 0, reverse=reverse)

    return result


@router.get("/saved", response_model=List[UniversityResponse])
def get_saved_universities(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    saved = db.query(SavedUniversity).filter(SavedUniversity.user_id == user.id).all()
    uni_ids = [s.university_id for s in saved]
    universities = db.query(University).filter(University.id.in_(uni_ids)).all()

    academic = db.query(Academic).filter(Academic.user_id == user.id).first()
    saved_ids = set(uni_ids)

    result = [build_response(u, academic, saved_ids) for u in universities]
    result.sort(key=lambda x: x.probability or 0, reverse=True)
    return result


@router.get("/{university_id}", response_model=UniversityResponse)
def get_university(
    university_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    uni = db.query(University).filter(University.id == university_id).first()
    if not uni:
        raise HTTPException(404, "Университет не найден")

    academic = db.query(Academic).filter(Academic.user_id == user.id).first()
    saved = db.query(SavedUniversity).filter_by(user_id=user.id, university_id=university_id).first()
    return build_response(uni, academic, {university_id} if saved else set())


@router.post("/{university_id}/save", status_code=201)
def save_university(
    university_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    uni = db.query(University).filter(University.id == university_id).first()
    if not uni:
        raise HTTPException(404, "Университет не найден")

    exists = db.query(SavedUniversity).filter_by(
        user_id=user.id, university_id=university_id
    ).first()
    if exists:
        raise HTTPException(400, "Уже добавлен в список")

    db.add(SavedUniversity(user_id=user.id, university_id=university_id))
    db.commit()
    return {"message": f"«{uni.name}» добавлен на доску"}


@router.delete("/{university_id}/save", status_code=204)
def remove_university(
    university_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    saved = db.query(SavedUniversity).filter_by(
        user_id=user.id, university_id=university_id
    ).first()
    if not saved:
        raise HTTPException(404, "Университет не найден в вашем списке")

    db.delete(saved)
    db.commit()
