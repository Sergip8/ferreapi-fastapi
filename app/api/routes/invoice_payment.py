from typing import List
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlmodel import Session, select, func
from app.api.deps import get_db
from app.models import InvoicePayment, InvoicePaymentCreate
from app.crud.invoice_payment import (
    get_invoice_payment_by_id,
    get_invoice_payments,
    create_invoice_payment,
    update_invoice_payment,
    delete_invoice_payment
)
from app.schemas import PaginatedUsersRequest
from pydantic import BaseModel

router = APIRouter()

@router.get("/", response_model=List[InvoicePayment])
def read_invoice_payments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_invoice_payments(db, skip=skip, limit=limit)

@router.get("/{invoice_id}", response_model=InvoicePayment)
def read_invoice_payment(invoice_id: int, db: Session = Depends(get_db)):
    invoice = get_invoice_payment_by_id(db, invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="InvoicePayment not found")
    return invoice

@router.post("/", response_model=InvoicePayment)
def create_invoice_payment_endpoint(invoice_in: InvoicePaymentCreate, db: Session = Depends(get_db)):
    return create_invoice_payment(db, invoice_in)

@router.put("/{invoice_id}", response_model=InvoicePayment)
def update_invoice_payment_endpoint(invoice_id: int, invoice_in: InvoicePaymentCreate, db: Session = Depends(get_db)):
    db_obj = get_invoice_payment_by_id(db, invoice_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="InvoicePayment not found")
    return update_invoice_payment(db, db_obj, invoice_in)

@router.delete("/{invoice_id}", response_model=InvoicePayment)
def delete_invoice_payment_endpoint(invoice_id: int, db: Session = Depends(get_db)):
    db_obj = delete_invoice_payment(db, invoice_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="InvoicePayment not found")
    return db_obj

class PaginatedInvoicePaymentResponse(BaseModel):
    data: list[InvoicePayment]
    total: int

@router.post("/paginated", response_model=PaginatedInvoicePaymentResponse)
def invoice_payment_paginated(
    params: PaginatedUsersRequest = Body(...),
    db: Session = Depends(get_db)
):
    query = select(InvoicePayment)
    if params.search:
        query = query.where(InvoicePayment.invoice_number.ilike(f"%{params.search}%"))
    sort_col = getattr(InvoicePayment, params.sort, InvoicePayment.invoice_id)
    if params.order.lower() == "desc":
        query = query.order_by(sort_col.desc())
    else:
        query = query.order_by(sort_col.asc())
    total_count = db.exec(select(func.count()).select_from(InvoicePayment)).one()
    total_count = total_count[0] if isinstance(total_count, tuple) else total_count
    offset = (params.page - 1) * params.size
    items = db.exec(query.offset(offset).limit(params.size)).all()
    return PaginatedInvoicePaymentResponse(data=items, total=total_count) 