from typing import List, Optional
from sqlmodel import Session, select
from app.models import InvoicePayment, InvoicePaymentCreate

def get_invoice_payment_by_id(session: Session, invoice_id: int) -> Optional[InvoicePayment]:
    return session.get(InvoicePayment, invoice_id)

def get_invoice_payments(session: Session, skip: int = 0, limit: int = 100) -> List[InvoicePayment]:
    return session.exec(select(InvoicePayment).offset(skip).limit(limit)).all()

def create_invoice_payment(session: Session, invoice_in: InvoicePaymentCreate) -> InvoicePayment:
    db_obj = InvoicePayment.model_validate(invoice_in)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj

def update_invoice_payment(session: Session, db_obj: InvoicePayment, obj_in: InvoicePaymentCreate) -> InvoicePayment:
    obj_data = obj_in.model_dump(exclude_unset=True)
    for key, value in obj_data.items():
        setattr(db_obj, key, value)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj

def delete_invoice_payment(session: Session, invoice_id: int) -> Optional[InvoicePayment]:
    db_obj = session.get(InvoicePayment, invoice_id)
    if db_obj:
        session.delete(db_obj)
        session.commit()
    return db_obj 