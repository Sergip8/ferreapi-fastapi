from typing import List
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlmodel import Session, select, func
from app.api.deps import get_db
from app.models import ManufacturingMachine, ManufacturingMachineCreate
from app.crud.manufacturing_machine import (
    get_manufacturing_machine_by_id,
    get_manufacturing_machines,
    create_manufacturing_machine,
    update_manufacturing_machine,
    delete_manufacturing_machine
)
from app.schemas import PaginatedUsersRequest
from pydantic import BaseModel

router = APIRouter()

@router.get("/", response_model=List[ManufacturingMachine])
def read_manufacturing_machines(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_manufacturing_machines(db, skip=skip, limit=limit)

@router.get("/{machine_id}", response_model=ManufacturingMachine)
def read_manufacturing_machine(machine_id: int, db: Session = Depends(get_db)):
    machine = get_manufacturing_machine_by_id(db, machine_id)
    if not machine:
        raise HTTPException(status_code=404, detail="ManufacturingMachine not found")
    return machine

@router.post("/", response_model=ManufacturingMachine)
def create_manufacturing_machine_endpoint(machine_in: ManufacturingMachineCreate, db: Session = Depends(get_db)):
    return create_manufacturing_machine(db, machine_in)

@router.put("/{machine_id}", response_model=ManufacturingMachine)
def update_manufacturing_machine_endpoint(machine_id: int, machine_in: ManufacturingMachineCreate, db: Session = Depends(get_db)):
    db_obj = get_manufacturing_machine_by_id(db, machine_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="ManufacturingMachine not found")
    return update_manufacturing_machine(db, db_obj, machine_in)

@router.delete("/{machine_id}", response_model=ManufacturingMachine)
def delete_manufacturing_machine_endpoint(machine_id: int, db: Session = Depends(get_db)):
    db_obj = delete_manufacturing_machine(db, machine_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="ManufacturingMachine not found")
    return db_obj

class PaginatedManufacturingMachineResponse(BaseModel):
    data: list[ManufacturingMachine]
    total: int

@router.post("/paginated", response_model=PaginatedManufacturingMachineResponse)
def manufacturing_machine_paginated(
    params: PaginatedUsersRequest = Body(...),
    db: Session = Depends(get_db)
):
    query = select(ManufacturingMachine)
    if params.search:
        query = query.where(ManufacturingMachine.machine_name.ilike(f"%{params.search}%"))
    sort_col = getattr(ManufacturingMachine, params.sort, ManufacturingMachine.machine_id)
    if params.order.lower() == "desc":
        query = query.order_by(sort_col.desc())
    else:
        query = query.order_by(sort_col.asc())
    total_count = db.exec(select(func.count()).select_from(ManufacturingMachine)).one()
    total_count = total_count[0] if isinstance(total_count, tuple) else total_count
    offset = (params.page - 1) * params.size
    items = db.exec(query.offset(offset).limit(params.size)).all()
    return PaginatedManufacturingMachineResponse(data=items, total=total_count) 