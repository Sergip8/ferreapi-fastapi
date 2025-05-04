from typing import List
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlmodel import Session, select, func
from app.api.deps import get_db
from app.models import RawMaterialInventory, RawMaterialInventoryCreate
from app.crud.raw_material_inventory import (
    get_raw_material_inventory_by_id,
    get_raw_material_inventories,
    create_raw_material_inventory,
    update_raw_material_inventory,
    delete_raw_material_inventory
)
from app.schemas import PaginatedUsersRequest
from pydantic import BaseModel

router = APIRouter()

@router.get("/", response_model=List[RawMaterialInventory])
def read_raw_material_inventories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_raw_material_inventories(db, skip=skip, limit=limit)

@router.get("/{material_id}", response_model=RawMaterialInventory)
def read_raw_material_inventory(material_id: int, db: Session = Depends(get_db)):
    inventory = get_raw_material_inventory_by_id(db, material_id)
    if not inventory:
        raise HTTPException(status_code=404, detail="RawMaterialInventory not found")
    return inventory

@router.post("/", response_model=RawMaterialInventory)
def create_raw_material_inventory_endpoint(inventory_in: RawMaterialInventoryCreate, db: Session = Depends(get_db)):
    return create_raw_material_inventory(db, inventory_in)

@router.put("/{material_id}", response_model=RawMaterialInventory)
def update_raw_material_inventory_endpoint(material_id: int, inventory_in: RawMaterialInventoryCreate, db: Session = Depends(get_db)):
    db_obj = get_raw_material_inventory_by_id(db, material_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="RawMaterialInventory not found")
    return update_raw_material_inventory(db, db_obj, inventory_in)

@router.delete("/{material_id}", response_model=RawMaterialInventory)
def delete_raw_material_inventory_endpoint(material_id: int, db: Session = Depends(get_db)):
    db_obj = delete_raw_material_inventory(db, material_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="RawMaterialInventory not found")
    return db_obj

class PaginatedRawMaterialInventoryResponse(BaseModel):
    data: list[RawMaterialInventory]
    total: int

@router.post("/paginated", response_model=PaginatedRawMaterialInventoryResponse)
def raw_material_inventory_paginated(
    params: PaginatedUsersRequest = Body(...),
    db: Session = Depends(get_db)
):
    query = select(RawMaterialInventory)
    if params.search:
        query = query.where(RawMaterialInventory.material_name.ilike(f"%{params.search}%"))
    sort_col = getattr(RawMaterialInventory, params.sort, RawMaterialInventory.material_id)
    if params.order.lower() == "desc":
        query = query.order_by(sort_col.desc())
    else:
        query = query.order_by(sort_col.asc())
    total_count = db.exec(select(func.count()).select_from(RawMaterialInventory)).one()
    total_count = total_count[0] if isinstance(total_count, tuple) else total_count
    offset = (params.page - 1) * params.size
    items = db.exec(query.offset(offset).limit(params.size)).all()
    return PaginatedRawMaterialInventoryResponse(data=items, total=total_count) 