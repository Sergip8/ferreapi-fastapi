from typing import List, Optional
from sqlmodel import Session, select
from app.models import ProductionBatch, ProductionBatchCreate

def get_production_batch_by_id(session: Session, batch_id: int) -> Optional[ProductionBatch]:
    return session.get(ProductionBatch, batch_id)

def get_production_batches(session: Session, skip: int = 0, limit: int = 100) -> List[ProductionBatch]:
    return session.exec(select(ProductionBatch).offset(skip).limit(limit)).all()

def create_production_batch(session: Session, batch_in: ProductionBatchCreate) -> ProductionBatch:
    db_obj = ProductionBatch.model_validate(batch_in)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj

def update_production_batch(session: Session, db_obj: ProductionBatch, obj_in: ProductionBatchCreate) -> ProductionBatch:
    obj_data = obj_in.model_dump(exclude_unset=True)
    for key, value in obj_data.items():
        setattr(db_obj, key, value)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj

def delete_production_batch(session: Session, batch_id: int) -> Optional[ProductionBatch]:
    db_obj = session.get(ProductionBatch, batch_id)
    if db_obj:
        session.delete(db_obj)
        session.commit()
    return db_obj 