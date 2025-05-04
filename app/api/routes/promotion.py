from typing import List
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlmodel import Session, select, func
from app.api.deps import get_db
from app.models import Promotion, PromotionCreate
from app.crud.promotion import (
    get_promotion_by_id,
    get_promotions,
    create_promotion,
    update_promotion,
    delete_promotion
)
from app.schemas import PaginatedUsersRequest
from pydantic import BaseModel

router = APIRouter()

@router.get("/", response_model=List[Promotion])
def read_promotions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_promotions(db, skip=skip, limit=limit)

@router.get("/{promotion_id}", response_model=Promotion)
def read_promotion(promotion_id: int, db: Session = Depends(get_db)):
    promotion = get_promotion_by_id(db, promotion_id)
    if not promotion:
        raise HTTPException(status_code=404, detail="Promotion not found")
    return promotion

@router.post("/", response_model=Promotion)
def create_promotion_endpoint(promotion_in: PromotionCreate, db: Session = Depends(get_db)):
    return create_promotion(db, promotion_in)

@router.put("/{promotion_id}", response_model=Promotion)
def update_promotion_endpoint(promotion_id: int, promotion_in: PromotionCreate, db: Session = Depends(get_db)):
    db_obj = get_promotion_by_id(db, promotion_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Promotion not found")
    return update_promotion(db, db_obj, promotion_in)

@router.delete("/{promotion_id}", response_model=Promotion)
def delete_promotion_endpoint(promotion_id: int, db: Session = Depends(get_db)):
    db_obj = delete_promotion(db, promotion_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Promotion not found")
    return db_obj

class PaginatedPromotionResponse(BaseModel):
    data: list[Promotion]
    total: int

@router.post("/paginated", response_model=PaginatedPromotionResponse)
def promotion_paginated(
    params: PaginatedUsersRequest = Body(...),
    db: Session = Depends(get_db)
):
    query = select(Promotion)
    if params.search:
        query = query.where(Promotion.promotion_name.ilike(f"%{params.search}%"))
    sort_col = getattr(Promotion, params.sort, Promotion.promotion_id)
    if params.order.lower() == "desc":
        query = query.order_by(sort_col.desc())
    else:
        query = query.order_by(sort_col.asc())
    total_count = db.exec(select(func.count()).select_from(Promotion)).one()
    total_count = total_count[0] if isinstance(total_count, tuple) else total_count
    offset = (params.page - 1) * params.size
    items = db.exec(query.offset(offset).limit(params.size)).all()
    return PaginatedPromotionResponse(data=items, total=total_count) 