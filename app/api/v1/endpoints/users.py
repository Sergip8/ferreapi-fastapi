from typing import List, Optional, Union
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from app.core.deps import get_current_user, get_db
from app.models import (
    User, UserPublic, UserCreate, UserUpdate, UpdatePassword, UserRegister, 
    UsersPublic, UserUpdateMe, UserResponse, PaginatedResponse, UserType,
    Customer, Administrator, Employee
)
from app.core.security import get_password_hash, verify_password
from app.core.config import settings
from datetime import datetime
from sqlalchemy import text

router = APIRouter()


@router.get("/{user_id}/role/{role}", response_model=Union[Customer, Administrator, Employee])
async def get_user_by_role(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    user_id: int,
    role: UserType
):
    """
    Get user information based on their ID and role.
    Only accessible by administrators.
    """
    if current_user.role != UserType.administrator:
        raise HTTPException(
            status_code=403,
            detail="Only administrators can access this endpoint"
        )

    # Get the base user first
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get the specific role information based on the role type
    if role == UserType.customer:
        customer = db.get(Customer, user_id)
        if not customer:
            raise HTTPException(status_code=404, detail="Customer information not found")
        return customer
    elif role == UserType.administrator:
        admin = db.get(Administrator, user_id)
        if not admin:
            raise HTTPException(status_code=404, detail="Administrator information not found")
        return admin
    elif role == UserType.employee:
        employee = db.get(Employee, user_id)
        if not employee:
            raise HTTPException(status_code=404, detail="Employee information not found")
        return employee
    else:
        raise HTTPException(status_code=400, detail="Invalid role specified") 