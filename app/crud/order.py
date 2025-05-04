from typing import List, Optional
from sqlmodel import Session, select
from app.models import Order, OrderCreate

def get_order_by_id(session: Session, order_id: int) -> Optional[Order]:
    return session.get(Order, order_id)

def get_orders(session: Session, skip: int = 0, limit: int = 100) -> List[Order]:
    return session.exec(select(Order).offset(skip).limit(limit)).all()

def create_order(session: Session, order_in: OrderCreate) -> Order:
    db_obj = Order.model_validate(order_in)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj

def update_order(session: Session, db_obj: Order, obj_in: OrderCreate) -> Order:
    obj_data = obj_in.model_dump(exclude_unset=True)
    for key, value in obj_data.items():
        setattr(db_obj, key, value)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj

def delete_order(session: Session, order_id: int) -> Optional[Order]:
    db_obj = session.get(Order, order_id)
    if db_obj:
        session.delete(db_obj)
        session.commit()
    return db_obj 