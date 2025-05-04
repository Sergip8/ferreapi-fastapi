from typing import List
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlmodel import Session, select, func
from app.api.deps import get_db
from app.models import Brand, BrandCreate
from app.crud.brand import (
    get_brand_by_id,
    get_brands,
    create_brand,
    update_brand,
    delete_brand
)
from app.schemas import PaginatedUsersRequest
from pydantic import BaseModel

router = APIRouter()

@router.get("/", response_model=List[Brand])
def read_brands(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_brands(db, skip=skip, limit=limit)

@router.get("/{brand_id}", response_model=Brand)
def read_brand(brand_id: int, db: Session = Depends(get_db)):
    brand = get_brand_by_id(db, brand_id)
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    return brand

@router.post("/", response_model=Brand)
def create_brand_endpoint(brand_in: BrandCreate, db: Session = Depends(get_db)):
    return create_brand(db, brand_in)

@router.put("/{brand_id}", response_model=Brand)
def update_brand_endpoint(brand_id: int, brand_in: BrandCreate, db: Session = Depends(get_db)):
    db_obj = get_brand_by_id(db, brand_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Brand not found")
    return update_brand(db, db_obj, brand_in)

@router.delete("/{brand_id}", response_model=Brand)
def delete_brand_endpoint(brand_id: int, db: Session = Depends(get_db)):
    db_obj = delete_brand(db, brand_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Brand not found")
    return db_obj

class PaginatedBrandResponse(BaseModel):
    data: list[Brand]
    total: int

@router.post("/paginated", response_model=PaginatedBrandResponse)
def brand_paginated(
    params: PaginatedUsersRequest = Body(...),
    db: Session = Depends(get_db)
):
    query = select(Brand)
    if params.search:
        query = query.where(Brand.name.ilike(f"%{params.search}%"))
    sort_col = getattr(Brand, params.sort, Brand.brand_id)
    if params.order.lower() == "desc":
        query = query.order_by(sort_col.desc())
    else:
        query = query.order_by(sort_col.asc())
    total_count = db.exec(select(func.count()).select_from(Brand)).one()
    total_count = total_count[0] if isinstance(total_count, tuple) else total_count
    offset = (params.page - 1) * params.size
    items = db.exec(query.offset(offset).limit(params.size)).all()
    return PaginatedBrandResponse(data=items, total=total_count) 