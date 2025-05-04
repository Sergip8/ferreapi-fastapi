from typing import List, Optional
from sqlmodel import Session, select
from app.models import ManufacturingMachine, ManufacturingMachineCreate

def get_manufacturing_machine_by_id(session: Session, machine_id: int) -> Optional[ManufacturingMachine]:
    return session.get(ManufacturingMachine, machine_id)

def get_manufacturing_machines(session: Session, skip: int = 0, limit: int = 100) -> List[ManufacturingMachine]:
    return session.exec(select(ManufacturingMachine).offset(skip).limit(limit)).all()

def create_manufacturing_machine(session: Session, machine_in: ManufacturingMachineCreate) -> ManufacturingMachine:
    db_obj = ManufacturingMachine.model_validate(machine_in)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj

def update_manufacturing_machine(session: Session, db_obj: ManufacturingMachine, obj_in: ManufacturingMachineCreate) -> ManufacturingMachine:
    obj_data = obj_in.model_dump(exclude_unset=True)
    for key, value in obj_data.items():
        setattr(db_obj, key, value)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj

def delete_manufacturing_machine(session: Session, machine_id: int) -> Optional[ManufacturingMachine]:
    db_obj = session.get(ManufacturingMachine, machine_id)
    if db_obj:
        session.delete(db_obj)
        session.commit()
    return db_obj 