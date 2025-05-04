from typing import List
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlmodel import Session, select, func
from app.api.deps import get_db
from app.models import CustomerReturn, CustomerReturnCreate
from app.crud.customer_return import (
    get_customer_return_by_id,
    get_customer_returns,
    create_customer_return,
    update_customer_return,
    delete_customer_return
)
from app.schemas import PaginatedUsersRequest
from pydantic import BaseModel

router = APIRouter()

@router.get("/", response_model=List[CustomerReturn])
def read_customer_returns(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_customer_returns(db, skip=skip, limit=limit)

@router.get("/{return_id}", response_model=CustomerReturn)
def read_customer_return(return_id: int, db: Session = Depends(get_db)):
    ret = get_customer_return_by_id(db, return_id)
    if not ret:
        raise HTTPException(status_code=404, detail="CustomerReturn not found")
    return ret

@router.post("/", response_model=CustomerReturn)
def create_customer_return_endpoint(return_in: CustomerReturnCreate, db: Session = Depends(get_db)):
    return create_customer_return(db, return_in)

@router.put("/{return_id}", response_model=CustomerReturn)
def update_customer_return_endpoint(return_id: int, return_in: CustomerReturnCreate, db: Session = Depends(get_db)):
    db_obj = get_customer_return_by_id(db, return_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="CustomerReturn not found")
    return update_customer_return(db, db_obj, return_in)

@router.delete("/{return_id}", response_model=CustomerReturn)
def delete_customer_return_endpoint(return_id: int, db: Session = Depends(get_db)):
    db_obj = delete_customer_return(db, return_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="CustomerReturn not found")
    return db_obj

class PaginatedCustomerReturnResponse(BaseModel):
    data: list[CustomerReturn]
    total: int

@router.post("/paginated", response_model=PaginatedCustomerReturnResponse)
def customer_return_paginated(
    params: PaginatedUsersRequest = Body(...),
    db: Session = Depends(get_db)
):
    query = select(CustomerReturn)
    if params.search:
        query = query.where(CustomerReturn.return_id.cast(String).ilike(f"%{params.search}%"))
    sort_col = getattr(CustomerReturn, params.sort, CustomerReturn.return_id)
    if params.order.lower() == "desc":
        query = query.order_by(sort_col.desc())
    else:
        query = query.order_by(sort_col.asc())
    total_count = db.exec(select(func.count()).select_from(CustomerReturn)).one()
    total_count = total_count[0] if isinstance(total_count, tuple) else total_count
    offset = (params.page - 1) * params.size
    items = db.exec(query.offset(offset).limit(params.size)).all()
    return PaginatedCustomerReturnResponse(data=items, total=total_count) 