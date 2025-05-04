from typing import List, Optional
from sqlmodel import Session, select
from app.models import Supplier, SupplierCreate

def get_supplier_by_id(session: Session, supplier_id: int) -> Optional[Supplier]:
    return session.get(Supplier, supplier_id)

def get_suppliers(session: Session, skip: int = 0, limit: int = 100) -> List[Supplier]:
    return session.exec(select(Supplier).offset(skip).limit(limit)).all()

def create_supplier(session: Session, supplier_in: SupplierCreate) -> Supplier:
    db_obj = Supplier.model_validate(supplier_in)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj

def update_supplier(session: Session, db_obj: Supplier, obj_in: SupplierCreate) -> Supplier:
    obj_data = obj_in.model_dump(exclude_unset=True)
    for key, value in obj_data.items():
        setattr(db_obj, key, value)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj

def delete_supplier(session: Session, supplier_id: int) -> Optional[Supplier]:
    db_obj = session.get(Supplier, supplier_id)
    if db_obj:
        session.delete(db_obj)
        session.commit()
    return db_obj 