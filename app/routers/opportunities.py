from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import User, Opportunity, SavedOpportunity
from app.schemas import OpportunityResponse
from app.auth import get_current_user

router = APIRouter(prefix="/opportunities", tags=["Opportunities"])


def build_response(opp: Opportunity, saved_ids: set) -> OpportunityResponse:
    return OpportunityResponse(
        id=opp.id,
        type=opp.type,
        title=opp.title,
        short_description=opp.short_description,
        full_description=opp.full_description,
        image_url=opp.image_url,
        event_date=opp.event_date,
        deadline=opp.deadline,
        organizer=opp.organizer,
        is_online=opp.is_online,
        is_saved=(opp.id in saved_ids),
        created_at=opp.created_at,
    )


@router.get("/", response_model=List[OpportunityResponse])
def list_opportunities(
    type: Optional[str] = Query(None, description="internship / volunteering / hackathon"),
    search: Optional[str] = Query(None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Opportunity)
    if type:
        query = query.filter(Opportunity.type == type)
    if search:
        query = query.filter(Opportunity.title.ilike(f"%{search}%"))

    opportunities = query.order_by(Opportunity.deadline_date).all()
    saved = db.query(SavedOpportunity).filter(SavedOpportunity.user_id == user.id).all()
    saved_ids = {s.opportunity_id for s in saved}

    return [build_response(o, saved_ids) for o in opportunities]


@router.get("/saved", response_model=List[OpportunityResponse])
def get_saved_opportunities(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    saved = db.query(SavedOpportunity).filter(SavedOpportunity.user_id == user.id).all()
    opp_ids = {s.opportunity_id for s in saved}
    opps = db.query(Opportunity).filter(Opportunity.id.in_(opp_ids)).all()
    return [build_response(o, opp_ids) for o in opps]


@router.get("/{opportunity_id}", response_model=OpportunityResponse)
def get_opportunity(
    opportunity_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    opp = db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()
    if not opp:
        raise HTTPException(404, "Возможность не найдена")

    saved = db.query(SavedOpportunity).filter_by(
        user_id=user.id, opportunity_id=opportunity_id
    ).first()
    return build_response(opp, {opportunity_id} if saved else set())


@router.post("/{opportunity_id}/save", status_code=201)
def save_opportunity(
    opportunity_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    opp = db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()
    if not opp:
        raise HTTPException(404, "Возможность не найдена")

    exists = db.query(SavedOpportunity).filter_by(
        user_id=user.id, opportunity_id=opportunity_id
    ).first()
    if exists:
        raise HTTPException(400, "Уже сохранено")

    db.add(SavedOpportunity(user_id=user.id, opportunity_id=opportunity_id))
    db.commit()
    return {"message": f"«{opp.title}» сохранено в профиль ✓"}


@router.delete("/{opportunity_id}/save", status_code=204)
def remove_opportunity(
    opportunity_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    saved = db.query(SavedOpportunity).filter_by(
        user_id=user.id, opportunity_id=opportunity_id
    ).first()
    if not saved:
        raise HTTPException(404, "Не найдено в сохранённых")
    db.delete(saved)
    db.commit()
