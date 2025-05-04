from typing import List, Optional
from sqlmodel import Session, select
from app.models import ShippingDelivery, ShippingDeliveryCreate

def get_shipping_delivery_by_id(session: Session, shipping_id: int) -> Optional[ShippingDelivery]:
    return session.get(ShippingDelivery, shipping_id)

def get_shipping_deliveries(session: Session, skip: int = 0, limit: int = 100) -> List[ShippingDelivery]:
    return session.exec(select(ShippingDelivery).offset(skip).limit(limit)).all()

def create_shipping_delivery(session: Session, shipping_in: ShippingDeliveryCreate) -> ShippingDelivery:
    db_obj = ShippingDelivery.model_validate(shipping_in)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj

def update_shipping_delivery(session: Session, db_obj: ShippingDelivery, obj_in: ShippingDeliveryCreate) -> ShippingDelivery:
    obj_data = obj_in.model_dump(exclude_unset=True)
    for key, value in obj_data.items():
        setattr(db_obj, key, value)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj

def delete_shipping_delivery(session: Session, shipping_id: int) -> Optional[ShippingDelivery]:
    db_obj = session.get(ShippingDelivery, shipping_id)
    if db_obj:
        session.delete(db_obj)
        session.commit()
    return db_obj 