from typing import List, Optional
from sqlmodel import Session, select
from app.models import Category, CategoryCreate

def get_categories(
    *,
    session: Session,
    skip: int = 0,
    limit: int = 100,
    is_active: bool | None = None,
    search: str | None = None,
    is_main: bool | None = None
) -> tuple[List[Category], int]:
    """Get all categories with pagination and filters"""
    query = select(Category)
    
    if is_active is not None:
        query = query.where(Category.is_active == is_active)
    
    if search:
        query = query.where(Category.category_name.ilike(f"%{search}%"))
    
    if is_main is not None:
        if is_main:
            query = query.where(Category.parent_category_id == None)
        else:
            query = query.where(Category.parent_category_id != None)
    
    total = len(session.exec(query).all())
    query = query.order_by(Category.display_order, Category.category_name)
    categories = session.exec(query.offset(skip).limit(limit)).all()
    return categories, total

def get_main_categories(*, session: Session) -> List[Category]:
    """Get all main categories (categories without a parent)"""
    statement = select(Category).where(Category.parent_category_id == None)
    categories = session.exec(statement).all()
    return categories

def get_category_by_id(session: Session, category_id: int) -> Optional[Category]:
    return session.get(Category, category_id)

def create_category(session: Session, category_in: CategoryCreate) -> Category:
    db_obj = Category.model_validate(category_in)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj

def update_category(session: Session, db_obj: Category, obj_in: CategoryCreate) -> Category:
    obj_data = obj_in.model_dump(exclude_unset=True)
    for key, value in obj_data.items():
        setattr(db_obj, key, value)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj

def delete_category(session: Session, category_id: int) -> Optional[Category]:
    db_obj = session.get(Category, category_id)
    if db_obj:
        session.delete(db_obj)
        session.commit()
    return db_obj
