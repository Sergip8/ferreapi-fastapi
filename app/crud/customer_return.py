from typing import List, Optional
from sqlmodel import Session, select
from app.models import CustomerReturn, CustomerReturnCreate

def get_customer_return_by_id(session: Session, return_id: int) -> Optional[CustomerReturn]:
    return session.get(CustomerReturn, return_id)

def get_customer_returns(session: Session, skip: int = 0, limit: int = 100) -> List[CustomerReturn]:
    return session.exec(select(CustomerReturn).offset(skip).limit(limit)).all()

def create_customer_return(session: Session, return_in: CustomerReturnCreate) -> CustomerReturn:
    db_obj = CustomerReturn.model_validate(return_in)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj

def update_customer_return(session: Session, db_obj: CustomerReturn, obj_in: CustomerReturnCreate) -> CustomerReturn:
    obj_data = obj_in.model_dump(exclude_unset=True)
    for key, value in obj_data.items():
        setattr(db_obj, key, value)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj

def delete_customer_return(session: Session, return_id: int) -> Optional[CustomerReturn]:
    db_obj = session.get(CustomerReturn, return_id)
    if db_obj:
        session.delete(db_obj)
        session.commit()
    return db_obj 