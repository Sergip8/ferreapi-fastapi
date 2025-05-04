from typing import List
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy import String
from sqlmodel import Session, select, func
from app.api.deps import get_db
from app.models import Order, OrderCreate
from app.crud.order import (
    get_order_by_id,
    get_orders,
    create_order,
    update_order,
    delete_order
)
from app.schemas import PaginatedUsersRequest
from pydantic import BaseModel

router = APIRouter()

@router.get("/", response_model=List[Order])
def read_orders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_orders(db, skip=skip, limit=limit)

@router.get("/{order_id}", response_model=Order)
def read_order(order_id: int, db: Session = Depends(get_db)):
    order = get_order_by_id(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.post("/", response_model=Order)
def create_order_endpoint(order_in: OrderCreate, db: Session = Depends(get_db)):
    return create_order(db, order_in)

@router.put("/{order_id}", response_model=Order)
def update_order_endpoint(order_id: int, order_in: OrderCreate, db: Session = Depends(get_db)):
    db_obj = get_order_by_id(db, order_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Order not found")
    return update_order(db, db_obj, order_in)

@router.delete("/{order_id}", response_model=Order)
def delete_order_endpoint(order_id: int, db: Session = Depends(get_db)):
    db_obj = delete_order(db, order_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Order not found")
    return db_obj

class PaginatedOrderResponse(BaseModel):
    data: list[Order]
    total: int

@router.post("/paginated", response_model=PaginatedOrderResponse)
def order_paginated(
    params: PaginatedUsersRequest = Body(...),
    db: Session = Depends(get_db)
):
    query = select(Order)
    if params.search:
        query = query.where(Order.order_id.cast(String).ilike(f"%{params.search}%"))
    sort_col = getattr(Order, params.sort, Order.order_id)
    if params.order.lower() == "desc":
        query = query.order_by(sort_col.desc())
    else:
        query = query.order_by(sort_col.asc())
    total_count = db.exec(select(func.count()).select_from(Order)).one()
    total_count = total_count[0] if isinstance(total_count, tuple) else total_count
    offset = (params.page - 1) * params.size
    items = db.exec(query.offset(offset).limit(params.size)).all()
    return PaginatedOrderResponse(data=items, total=total_count) 