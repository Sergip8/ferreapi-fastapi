from typing import List, Optional
from sqlmodel import Session, select
from app.models import TechnicalSpecification, TechnicalSpecificationCreate

def get_technical_specification_by_id(session: Session, spec_id: int) -> Optional[TechnicalSpecification]:
    return session.get(TechnicalSpecification, spec_id)

def get_technical_specifications(session: Session, skip: int = 0, limit: int = 100) -> List[TechnicalSpecification]:
    return session.exec(select(TechnicalSpecification).offset(skip).limit(limit)).all()

def create_technical_specification(session: Session, spec_in: TechnicalSpecificationCreate) -> TechnicalSpecification:
    db_obj = TechnicalSpecification.model_validate(spec_in)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj

def update_technical_specification(session: Session, db_obj: TechnicalSpecification, obj_in: TechnicalSpecificationCreate) -> TechnicalSpecification:
    obj_data = obj_in.model_dump(exclude_unset=True)
    for key, value in obj_data.items():
        setattr(db_obj, key, value)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj

def delete_technical_specification(session: Session, spec_id: int) -> Optional[TechnicalSpecification]:
    db_obj = session.get(TechnicalSpecification, spec_id)
    if db_obj:
        session.delete(db_obj)
        session.commit()
    return db_obj 