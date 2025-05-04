from typing import List
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlmodel import Session, select, func
from app.api.deps import get_db
from app.models import Supplier, SupplierCreate
from app.crud.supplier import (
    get_supplier_by_id,
    get_suppliers,
    create_supplier,
    update_supplier,
    delete_supplier
)
from app.schemas import PaginatedUsersRequest
from pydantic import BaseModel

router = APIRouter()

@router.get("/", response_model=List[Supplier])
def read_suppliers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_suppliers(db, skip=skip, limit=limit)

@router.get("/{supplier_id}", response_model=Supplier)
def read_supplier(supplier_id: int, db: Session = Depends(get_db)):
    supplier = get_supplier_by_id(db, supplier_id)
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return supplier

@router.post("/", response_model=Supplier)
def create_supplier_endpoint(supplier_in: SupplierCreate, db: Session = Depends(get_db)):
    return create_supplier(db, supplier_in)

@router.put("/{supplier_id}", response_model=Supplier)
def update_supplier_endpoint(supplier_id: int, supplier_in: SupplierCreate, db: Session = Depends(get_db)):
    db_obj = get_supplier_by_id(db, supplier_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return update_supplier(db, db_obj, supplier_in)

@router.delete("/{supplier_id}", response_model=Supplier)
def delete_supplier_endpoint(supplier_id: int, db: Session = Depends(get_db)):
    db_obj = delete_supplier(db, supplier_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return db_obj

class PaginatedSupplierResponse(BaseModel):
    data: list[Supplier]
    total: int

@router.post("/paginated", response_model=PaginatedSupplierResponse)
def supplier_paginated(
    params: PaginatedUsersRequest = Body(...),
    db: Session = Depends(get_db)
):
    query = select(Supplier)
    if params.search:
        query = query.where(Supplier.supplier_name.ilike(f"%{params.search}%"))
    sort_col = getattr(Supplier, params.sort, Supplier.supplier_id)
    if params.order.lower() == "desc":
        query = query.order_by(sort_col.desc())
    else:
        query = query.order_by(sort_col.asc())
    total_count = db.exec(select(func.count()).select_from(Supplier)).one()
    total_count = total_count[0] if isinstance(total_count, tuple) else total_count
    offset = (params.page - 1) * params.size
    items = db.exec(query.offset(offset).limit(params.size)).all()
    return PaginatedSupplierResponse(data=items, total=total_count) 