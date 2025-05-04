from typing import List
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlmodel import Session, select, func
from app.api.deps import get_db
from app.models import ShippingDelivery, ShippingDeliveryCreate
from app.crud.shipping_delivery import (
    get_shipping_delivery_by_id,
    get_shipping_deliveries,
    create_shipping_delivery,
    update_shipping_delivery,
    delete_shipping_delivery
)
from app.schemas import PaginatedUsersRequest
from pydantic import BaseModel

router = APIRouter()

@router.get("/", response_model=List[ShippingDelivery])
def read_shipping_deliveries(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_shipping_deliveries(db, skip=skip, limit=limit)

@router.get("/{shipping_id}", response_model=ShippingDelivery)
def read_shipping_delivery(shipping_id: int, db: Session = Depends(get_db)):
    shipping = get_shipping_delivery_by_id(db, shipping_id)
    if not shipping:
        raise HTTPException(status_code=404, detail="ShippingDelivery not found")
    return shipping

@router.post("/", response_model=ShippingDelivery)
def create_shipping_delivery_endpoint(shipping_in: ShippingDeliveryCreate, db: Session = Depends(get_db)):
    return create_shipping_delivery(db, shipping_in)

@router.put("/{shipping_id}", response_model=ShippingDelivery)
def update_shipping_delivery_endpoint(shipping_id: int, shipping_in: ShippingDeliveryCreate, db: Session = Depends(get_db)):
    db_obj = get_shipping_delivery_by_id(db, shipping_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="ShippingDelivery not found")
    return update_shipping_delivery(db, db_obj, shipping_in)

@router.delete("/{shipping_id}", response_model=ShippingDelivery)
def delete_shipping_delivery_endpoint(shipping_id: int, db: Session = Depends(get_db)):
    db_obj = delete_shipping_delivery(db, shipping_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="ShippingDelivery not found")
    return db_obj

class PaginatedShippingDeliveryResponse(BaseModel):
    data: list[ShippingDelivery]
    total: int

@router.post("/paginated", response_model=PaginatedShippingDeliveryResponse)
def shipping_delivery_paginated(
    params: PaginatedUsersRequest = Body(...),
    db: Session = Depends(get_db)
):
    query = select(ShippingDelivery)
    if params.search:
        query = query.where(ShippingDelivery.tracking_number.ilike(f"%{params.search}%"))
    sort_col = getattr(ShippingDelivery, params.sort, ShippingDelivery.shipping_id)
    if params.order.lower() == "desc":
        query = query.order_by(sort_col.desc())
    else:
        query = query.order_by(sort_col.asc())
    total_count = db.exec(select(func.count()).select_from(ShippingDelivery)).one()
    total_count = total_count[0] if isinstance(total_count, tuple) else total_count
    offset = (params.page - 1) * params.size
    items = db.exec(query.offset(offset).limit(params.size)).all()
    return PaginatedShippingDeliveryResponse(data=items, total=total_count) 