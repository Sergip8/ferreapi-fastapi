from typing import List
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy import String
from sqlmodel import Session, select, func
from app.api.deps import get_db
from app.models import TechnicalSpecification, TechnicalSpecificationCreate
from app.crud.technical_specification import (
    get_technical_specification_by_id,
    get_technical_specifications,
    create_technical_specification,
    update_technical_specification,
    delete_technical_specification
)
from app.schemas import PaginatedUsersRequest
from pydantic import BaseModel

router = APIRouter()

@router.get("/", response_model=List[TechnicalSpecification])
def read_technical_specifications(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_technical_specifications(db, skip=skip, limit=limit)

@router.get("/{spec_id}", response_model=TechnicalSpecification)
def read_technical_specification(spec_id: int, db: Session = Depends(get_db)):
    spec = get_technical_specification_by_id(db, spec_id)
    if not spec:
        raise HTTPException(status_code=404, detail="Technical specification not found")
    return spec

@router.post("/", response_model=TechnicalSpecification)
def create_technical_specification_endpoint(spec_in: TechnicalSpecificationCreate, db: Session = Depends(get_db)):
    return create_technical_specification(db, spec_in)

@router.put("/{spec_id}", response_model=TechnicalSpecification)
def update_technical_specification_endpoint(spec_id: int, spec_in: TechnicalSpecificationCreate, db: Session = Depends(get_db)):
    db_obj = get_technical_specification_by_id(db, spec_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Technical specification not found")
    return update_technical_specification(db, db_obj, spec_in)

@router.delete("/{spec_id}", response_model=TechnicalSpecification)
def delete_technical_specification_endpoint(spec_id: int, db: Session = Depends(get_db)):
    db_obj = delete_technical_specification(db, spec_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Technical specification not found")
    return db_obj

class PaginatedTechnicalSpecificationResponse(BaseModel):
    data: list[TechnicalSpecification]
    total: int

@router.post("/paginated", response_model=PaginatedTechnicalSpecificationResponse)
def technical_specification_paginated(
    params: PaginatedUsersRequest = Body(...),
    db: Session = Depends(get_db)
):
    query = select(TechnicalSpecification)
    if params.search:
        query = query.where(
            (TechnicalSpecification.warehouse_location.ilike(f"%{params.search}%")) |
            (TechnicalSpecification.product_id.cast(String).ilike(f"%{params.search}%"))
        )
    sort_col = getattr(TechnicalSpecification, params.sort, TechnicalSpecification.spec_id)
    if params.order.lower() == "desc":
        query = query.order_by(sort_col.desc())
    else:
        query = query.order_by(sort_col.asc())
    total_count = db.exec(select(func.count()).select_from(TechnicalSpecification)).one()
    total_count = total_count[0] if isinstance(total_count, tuple) else total_count
    offset = (params.page - 1) * params.size
    items = db.exec(query.offset(offset).limit(params.size)).all()
    return PaginatedTechnicalSpecificationResponse(data=items, total=total_count) 