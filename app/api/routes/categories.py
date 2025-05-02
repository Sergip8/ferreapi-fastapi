from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from app.api.deps import get_db, get_current_user
from app.models import User, UserType
from app.crud.category import (
    get_main_categories,
    get_categories,
    create_category,
    get_category_by_id,
    update_category,
    delete_category,
)
from app.models import Category, CategoryCreate, CategoryBase

router = APIRouter()

@router.get("/", response_model=dict)
def read_categories(
    *,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    search: str | None = None,
    is_active: bool | None = None,
    is_main: bool | None = None,
):
    """
    Retrieve all categories with pagination and filters.
    """
    categories, total = get_categories(
        session=db,
        skip=skip,
        limit=limit,
        search=search,
        is_active=is_active,
        is_main=is_main
    )
    return {
        "data": categories,
        "total": total
    }

@router.get("/main", response_model=List[Category])
def read_main_categories(
    db: Session = Depends(get_db),
) -> List[Category]:
    """
    Retrieve all main categories (categories without parent).
    """
    categories = get_main_categories(session=db)
    return categories

@router.get("/{category_id}", response_model=Category)
def read_category(
    *,
    db: Session = Depends(get_db),
    category_id: int,
):
    """
    Get category by ID.
    """
    category = get_category_by_id(session=db, category_id=category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@router.post("/", response_model=Category)
def create_new_category(
    *,
    db: Session = Depends(get_db),
    category_in: CategoryCreate,
    current_user: User = Depends(get_current_user),
):
    """
    Create new category.
    Only admin users can create categories.
    """
    if current_user.user_type != UserType.admin:
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions"
        )
    """
    Create new category.
    """
    if category_in.parent_category_id:
        parent = get_category_by_id(session=db, category_id=category_in.parent_category_id)
        if not parent:
            raise HTTPException(
                status_code=400,
                detail="Parent category not found"
            )
    return create_category(session=db, category_in=category_in)

@router.put("/{category_id}", response_model=Category)
def update_existing_category(
    *,
    db: Session = Depends(get_db),
    category_id: int,
    category_in: CategoryCreate,
    current_user: User = Depends(get_current_user),
):
    """
    Update category.
    Only admin users can update categories.
    """
    if current_user.user_type != UserType.admin:
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions"
        )
    """
    Update category.
    """
    category = get_category_by_id(session=db, category_id=category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    if category_in.parent_category_id and category_in.parent_category_id != category.parent_category_id:
        parent = get_category_by_id(session=db, category_id=category_in.parent_category_id)
        if not parent:
            raise HTTPException(
                status_code=400,
                detail="Parent category not found"
            )
    
    return update_category(session=db, db_obj=category, obj_in=category_in)

@router.delete("/{category_id}", response_model=Category)
def delete_existing_category(
    *,
    db: Session = Depends(get_db),
    category_id: int,
    current_user: User = Depends(get_current_user),
):
    """
    Delete category.
    Only admin users can delete categories.
    """
    if current_user.user_type != UserType.admin:
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions"
        )
    """
    Delete category.
    """
    category = get_category_by_id(session=db, category_id=category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return delete_category(session=db, category_id=category_id)
