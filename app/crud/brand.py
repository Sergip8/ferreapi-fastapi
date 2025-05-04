from typing import List, Optional
from sqlmodel import Session, select
from app.models import Brand, BrandCreate

def get_brand_by_id(session: Session, brand_id: int) -> Optional[Brand]:
    return session.get(Brand, brand_id)

def get_brands(session: Session, skip: int = 0, limit: int = 100) -> List[Brand]:
    return session.exec(select(Brand).offset(skip).limit(limit)).all()

def create_brand(session: Session, brand_in: BrandCreate) -> Brand:
    db_obj = Brand.model_validate(brand_in)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj

def update_brand(session: Session, db_obj: Brand, obj_in: BrandCreate) -> Brand:
    obj_data = obj_in.model_dump(exclude_unset=True)
    for key, value in obj_data.items():
        setattr(db_obj, key, value)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj

def delete_brand(session: Session, brand_id: int) -> Optional[Brand]:
    db_obj = session.get(Brand, brand_id)
    if db_obj:
        session.delete(db_obj)
        session.commit()
    return db_obj 