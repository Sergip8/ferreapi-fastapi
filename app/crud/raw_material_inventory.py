from typing import List, Optional
from sqlmodel import Session, select
from app.models import RawMaterialInventory, RawMaterialInventoryCreate

def get_raw_material_inventory_by_id(session: Session, material_id: int) -> Optional[RawMaterialInventory]:
    return session.get(RawMaterialInventory, material_id)

def get_raw_material_inventories(session: Session, skip: int = 0, limit: int = 100) -> List[RawMaterialInventory]:
    return session.exec(select(RawMaterialInventory).offset(skip).limit(limit)).all()

def create_raw_material_inventory(session: Session, inventory_in: RawMaterialInventoryCreate) -> RawMaterialInventory:
    db_obj = RawMaterialInventory.model_validate(inventory_in)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj

def update_raw_material_inventory(session: Session, db_obj: RawMaterialInventory, obj_in: RawMaterialInventoryCreate) -> RawMaterialInventory:
    obj_data = obj_in.model_dump(exclude_unset=True)
    for key, value in obj_data.items():
        setattr(db_obj, key, value)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj

def delete_raw_material_inventory(session: Session, material_id: int) -> Optional[RawMaterialInventory]:
    db_obj = session.get(RawMaterialInventory, material_id)
    if db_obj:
        session.delete(db_obj)
        session.commit()
    return db_obj 