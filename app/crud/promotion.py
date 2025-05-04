from typing import List, Optional
from sqlmodel import Session, select
from app.models import Promotion, PromotionCreate

def get_promotion_by_id(session: Session, promotion_id: int) -> Optional[Promotion]:
    return session.get(Promotion, promotion_id)

def get_promotions(session: Session, skip: int = 0, limit: int = 100) -> List[Promotion]:
    return session.exec(select(Promotion).offset(skip).limit(limit)).all()

def create_promotion(session: Session, promotion_in: PromotionCreate) -> Promotion:
    db_obj = Promotion.model_validate(promotion_in)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj

def update_promotion(session: Session, db_obj: Promotion, obj_in: PromotionCreate) -> Promotion:
    obj_data = obj_in.model_dump(exclude_unset=True)
    for key, value in obj_data.items():
        setattr(db_obj, key, value)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj

def delete_promotion(session: Session, promotion_id: int) -> Optional[Promotion]:
    db_obj = session.get(Promotion, promotion_id)
    if db_obj:
        session.delete(db_obj)
        session.commit()
    return db_obj 