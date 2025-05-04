from typing import List, Optional
from sqlmodel import Session, select
from app.models import QualityControl, QualityControlCreate

def get_quality_control_by_id(session: Session, quality_check_id: int) -> Optional[QualityControl]:
    return session.get(QualityControl, quality_check_id)

def get_quality_controls(session: Session, skip: int = 0, limit: int = 100) -> List[QualityControl]:
    return session.exec(select(QualityControl).offset(skip).limit(limit)).all()

def create_quality_control(session: Session, qc_in: QualityControlCreate) -> QualityControl:
    db_obj = QualityControl.model_validate(qc_in)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj

def update_quality_control(session: Session, db_obj: QualityControl, obj_in: QualityControlCreate) -> QualityControl:
    obj_data = obj_in.model_dump(exclude_unset=True)
    for key, value in obj_data.items():
        setattr(db_obj, key, value)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj

def delete_quality_control(session: Session, quality_check_id: int) -> Optional[QualityControl]:
    db_obj = session.get(QualityControl, quality_check_id)
    if db_obj:
        session.delete(db_obj)
        session.commit()
    return db_obj 