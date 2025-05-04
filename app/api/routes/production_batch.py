from typing import List
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlmodel import Session, select, func
from app.api.deps import get_db
from app.models import ProductionBatch, ProductionBatchCreate
from app.crud.production_batch import (
    get_production_batch_by_id,
    get_production_batches,
    create_production_batch,
    update_production_batch,
    delete_production_batch
)
from app.schemas import PaginatedUsersRequest
from pydantic import BaseModel

router = APIRouter()

@router.get("/", response_model=List[ProductionBatch])
def read_production_batches(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_production_batches(db, skip=skip, limit=limit)

@router.get("/{batch_id}", response_model=ProductionBatch)
def read_production_batch(batch_id: int, db: Session = Depends(get_db)):
    batch = get_production_batch_by_id(db, batch_id)
    if not batch:
        raise HTTPException(status_code=404, detail="ProductionBatch not found")
    return batch

@router.post("/", response_model=ProductionBatch)
def create_production_batch_endpoint(batch_in: ProductionBatchCreate, db: Session = Depends(get_db)):
    return create_production_batch(db, batch_in)

@router.put("/{batch_id}", response_model=ProductionBatch)
def update_production_batch_endpoint(batch_id: int, batch_in: ProductionBatchCreate, db: Session = Depends(get_db)):
    db_obj = get_production_batch_by_id(db, batch_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="ProductionBatch not found")
    return update_production_batch(db, db_obj, batch_in)

@router.delete("/{batch_id}", response_model=ProductionBatch)
def delete_production_batch_endpoint(batch_id: int, db: Session = Depends(get_db)):
    db_obj = delete_production_batch(db, batch_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="ProductionBatch not found")
    return db_obj

class PaginatedProductionBatchResponse(BaseModel):
    data: list[ProductionBatch]
    total: int

@router.post("/paginated", response_model=PaginatedProductionBatchResponse)
def production_batch_paginated(
    params: PaginatedUsersRequest = Body(...),
    db: Session = Depends(get_db)
):
    query = select(ProductionBatch)
    if params.search:
        query = query.where(ProductionBatch.batch_id.cast(String).ilike(f"%{params.search}%"))
    sort_col = getattr(ProductionBatch, params.sort, ProductionBatch.batch_id)
    if params.order.lower() == "desc":
        query = query.order_by(sort_col.desc())
    else:
        query = query.order_by(sort_col.asc())
    total_count = db.exec(select(func.count()).select_from(ProductionBatch)).one()
    total_count = total_count[0] if isinstance(total_count, tuple) else total_count
    offset = (params.page - 1) * params.size
    items = db.exec(query.offset(offset).limit(params.size)).all()
    return PaginatedProductionBatchResponse(data=items, total=total_count) 