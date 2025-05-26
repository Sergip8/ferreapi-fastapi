from typing import List
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlmodel import Session, select, func
from app.api.deps import get_db
from app.models import Category, CategoryCreate
from app.crud.category import (
    get_category_by_id,
    get_categories,
    create_category,
    get_main_categories,
    update_category,
    delete_category
)
from app.schemas import PaginatedUsersRequest
from pydantic import BaseModel

router = APIRouter()

@router.get("/main", response_model=List[Category])
def read_main_categories(
    db: Session = Depends(get_db),
) -> List[Category]:
    """
    Retrieve all main categories (categories without parent).
    """
    categories = get_main_categories(session=db)
    return categories

@router.get("/", response_model=List[Category])
def read_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_categories(db, skip=skip, limit=limit)

@router.get("/menu", response_model=List[Category])
def get_menu_categories(db: Session = Depends(get_db)) -> List[Category]:
    """
    Retrieve all categories for menu.
    """
    categories = db.exec(select(Category)).all()
    return categories

@router.get("/{category_id}", response_model=Category)
def read_category(category_id: int, db: Session = Depends(get_db)):
    category = get_category_by_id(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@router.post("/", response_model=Category)
def create_category_endpoint(category_in: CategoryCreate, db: Session = Depends(get_db)):
    return create_category(db, category_in)

@router.put("/{category_id}", response_model=Category)
def update_category_endpoint(category_id: int, category_in: CategoryCreate, db: Session = Depends(get_db)):
    db_obj = get_category_by_id(db, category_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Category not found")
    return update_category(db, db_obj, category_in)

@router.delete("/{category_id}", response_model=Category)
def delete_category_endpoint(category_id: int, db: Session = Depends(get_db)):
    db_obj = delete_category(db, category_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Category not found")
    return db_obj

class PaginatedCategoryResponse(BaseModel):
    data: list[Category]
    total: int

@router.post("/paginated", response_model=PaginatedCategoryResponse)
def category_paginated(
    params: PaginatedUsersRequest = Body(...),
    db: Session = Depends(get_db)
):
    query = select(Category)
    if params.search:
        query = query.where(Category.category_name.ilike(f"%{params.search}%"))
    sort_col = getattr(Category, params.sort, Category.category_id)
    if params.order.lower() == "desc":
        query = query.order_by(sort_col.desc())
    else:
        query = query.order_by(sort_col.asc())
    total_count = db.exec(select(func.count()).select_from(Category)).one()
    total_count = total_count[0] if isinstance(total_count, tuple) else total_count
    offset = (params.page - 1) * params.size
    items = db.exec(query.offset(offset).limit(params.size)).all()
    return PaginatedCategoryResponse(data=items, total=total_count) 


