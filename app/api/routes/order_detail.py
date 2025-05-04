from typing import List
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlmodel import Session, select, func
from app.api.deps import get_db
from app.models import OrderDetail, OrderDetailCreate
from app.crud.order_detail import (
    get_order_detail_by_id,
    get_order_details,
    create_order_detail,
    update_order_detail,
    delete_order_detail
)
from app.schemas import PaginatedUsersRequest
from pydantic import BaseModel

router = APIRouter()

@router.get("/", response_model=List[OrderDetail])
def read_order_details(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_order_details(db, skip=skip, limit=limit)

@router.get("/{order_detail_id}", response_model=OrderDetail)
def read_order_detail(order_detail_id: int, db: Session = Depends(get_db)):
    order_detail = get_order_detail_by_id(db, order_detail_id)
    if not order_detail:
        raise HTTPException(status_code=404, detail="OrderDetail not found")
    return order_detail

@router.post("/", response_model=OrderDetail)
def create_order_detail_endpoint(order_detail_in: OrderDetailCreate, db: Session = Depends(get_db)):
    return create_order_detail(db, order_detail_in)

@router.put("/{order_detail_id}", response_model=OrderDetail)
def update_order_detail_endpoint(order_detail_id: int, order_detail_in: OrderDetailCreate, db: Session = Depends(get_db)):
    db_obj = get_order_detail_by_id(db, order_detail_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="OrderDetail not found")
    return update_order_detail(db, db_obj, order_detail_in)

@router.delete("/{order_detail_id}", response_model=OrderDetail)
def delete_order_detail_endpoint(order_detail_id: int, db: Session = Depends(get_db)):
    db_obj = delete_order_detail(db, order_detail_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="OrderDetail not found")
    return db_obj

class PaginatedOrderDetailResponse(BaseModel):
    data: list[OrderDetail]
    total: int

@router.post("/paginated", response_model=PaginatedOrderDetailResponse)
def order_detail_paginated(
    params: PaginatedUsersRequest = Body(...),
    db: Session = Depends(get_db)
):
    query = select(OrderDetail)
    if params.search:
        query = query.where(OrderDetail.order_detail_id.cast(String).ilike(f"%{params.search}%"))
    sort_col = getattr(OrderDetail, params.sort, OrderDetail.order_detail_id)
    if params.order.lower() == "desc":
        query = query.order_by(sort_col.desc())
    else:
        query = query.order_by(sort_col.asc())
    total_count = db.exec(select(func.count()).select_from(OrderDetail)).one()
    total_count = total_count[0] if isinstance(total_count, tuple) else total_count
    offset = (params.page - 1) * params.size
    items = db.exec(query.offset(offset).limit(params.size)).all()
    return PaginatedOrderDetailResponse(data=items, total=total_count) 