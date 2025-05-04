from typing import List, Optional
from sqlmodel import Session, select
from app.models import Inventory, InventoryCreate

def get_inventory_by_id(session: Session, inventory_id: int) -> Optional[Inventory]:
    return session.get(Inventory, inventory_id)

def get_inventories(session: Session, skip: int = 0, limit: int = 100) -> List[Inventory]:
    return session.exec(select(Inventory).offset(skip).limit(limit)).all()

def create_inventory(session: Session, inventory_in: InventoryCreate) -> Inventory:
    db_obj = Inventory.model_validate(inventory_in)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj

def update_inventory(session: Session, db_obj: Inventory, obj_in: InventoryCreate) -> Inventory:
    obj_data = obj_in.model_dump(exclude_unset=True)
    for key, value in obj_data.items():
        setattr(db_obj, key, value)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj

def delete_inventory(session: Session, inventory_id: int) -> Optional[Inventory]:
    db_obj = session.get(Inventory, inventory_id)
    if db_obj:
        session.delete(db_obj)
        session.commit()
    return db_obj 