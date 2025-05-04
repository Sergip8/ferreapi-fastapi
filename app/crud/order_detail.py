from typing import List, Optional
from sqlmodel import Session, select
from app.models import OrderDetail, OrderDetailCreate

def get_order_detail_by_id(session: Session, order_detail_id: int) -> Optional[OrderDetail]:
    return session.get(OrderDetail, order_detail_id)

def get_order_details(session: Session, skip: int = 0, limit: int = 100) -> List[OrderDetail]:
    return session.exec(select(OrderDetail).offset(skip).limit(limit)).all()

def create_order_detail(session: Session, order_detail_in: OrderDetailCreate) -> OrderDetail:
    db_obj = OrderDetail.model_validate(order_detail_in)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj

def update_order_detail(session: Session, db_obj: OrderDetail, obj_in: OrderDetailCreate) -> OrderDetail:
    obj_data = obj_in.model_dump(exclude_unset=True)
    for key, value in obj_data.items():
        setattr(db_obj, key, value)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj

def delete_order_detail(session: Session, order_detail_id: int) -> Optional[OrderDetail]:
    db_obj = session.get(OrderDetail, order_detail_id)
    if db_obj:
        session.delete(db_obj)
        session.commit()
    return db_obj 