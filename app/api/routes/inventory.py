from typing import List
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy import String
from sqlmodel import Session, select, func
from app.api.deps import get_db
from app.models import Inventory, InventoryCreate
from app.crud.inventory import (
    get_inventory_by_id,
    get_inventories,
    create_inventory,
    update_inventory,
    delete_inventory
)
from app.schemas import PaginatedUsersRequest
from pydantic import BaseModel

router = APIRouter()

@router.get("/", response_model=List[Inventory])
def read_inventories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_inventories(db, skip=skip, limit=limit)

@router.get("/{inventory_id}", response_model=Inventory)
def read_inventory(inventory_id: int, db: Session = Depends(get_db)):
    inventory = get_inventory_by_id(db, inventory_id)
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory not found")
    return inventory

@router.post("/", response_model=Inventory)
def create_inventory_endpoint(inventory_in: InventoryCreate, db: Session = Depends(get_db)):
    return create_inventory(db, inventory_in)

@router.put("/{inventory_id}", response_model=Inventory)
def update_inventory_endpoint(inventory_id: int, inventory_in: InventoryCreate, db: Session = Depends(get_db)):
    db_obj = get_inventory_by_id(db, inventory_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Inventory not found")
    return update_inventory(db, db_obj, inventory_in)

@router.delete("/{inventory_id}", response_model=Inventory)
def delete_inventory_endpoint(inventory_id: int, db: Session = Depends(get_db)):
    db_obj = delete_inventory(db, inventory_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Inventory not found")
    return db_obj

class PaginatedInventoryResponse(BaseModel):
    data: list[Inventory]
    total: int

@router.post("/paginated", response_model=PaginatedInventoryResponse)
def inventory_paginated(
    params: PaginatedUsersRequest = Body(...),
    db: Session = Depends(get_db)
):
    query = select(Inventory)
    if params.search:
        query = query.where(
            (Inventory.warehouse_location.ilike(f"%{params.search}%")) |
            (Inventory.product_id.cast(String).ilike(f"%{params.search}%"))
        )
    # Sorting
    sort_col = getattr(Inventory, params.sort, Inventory.inventory_id)
    if params.order.lower() == "desc":
        query = query.order_by(sort_col.desc())
    else:
        query = query.order_by(sort_col.asc())
    # Pagination
    total_count = db.exec(select(func.count()).select_from(Inventory)).one()
    total_count = total_count[0] if isinstance(total_count, tuple) else total_count
    offset = (params.page - 1) * params.size
    items = db.exec(query.offset(offset).limit(params.size)).all()
    return PaginatedInventoryResponse(data=items, total=total_count) 