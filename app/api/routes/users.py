import uuid
from typing import Any, Dict, List, Optional, Union

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from sqlalchemy import text
from sqlmodel import col, delete, func, select

from app.crud import user
from app.api.deps import (
    CurrentUser,
    SessionDep,
    get_current_active_superuser,
)
from app.core.config import settings
from app.core.security import get_password_hash, verify_password
from app.models import (
    Administrator,
    AdministratorBase,
    Customer,
    CustomerBase,
    Distributor,
    DistributorBase,
    Employee,
    EmployeeBase,
    Message,
    PaginatedResponse,
    UpdatePassword,
    User,
    UserCreate,
    UserPublic,
    UserRegister,
    UserResponse,
    UserType,
    UsersPublic,
    UserUpdate,
    UserUpdateMe,
)
from app.schemas import PaginatedUsersRequest
from app.utils import generate_new_account_email, send_email

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/paginated", response_model=PaginatedResponse)
async def get_users_paginated(
   *,
    session: SessionDep,
    current_user: CurrentUser,
    params: PaginatedUsersRequest = Body(...)
):
    """
    Get paginated users with search, sort, and filter capabilities.
    Only accessible by administrators.
    """
    print(current_user.role)
    if current_user.role != UserType.administrator:
        raise HTTPException(
            status_code=403,
            detail="Only administrators can access this endpoint"
        )
    
    count_query = text("""
        SELECT get_users_count(:search_term, :filter_role)
    """)

    total_count = session.execute(
        count_query,
        {
            "search_term": params.search,
            "filter_role": params.role
        }
    ).scalar()

    # Call the PostgreSQL function
    query = text("""
        SELECT * FROM get_users_paginated(
            :search_term,
            :sort_column,
            :sort_direction,
            :page_number,
            :page_size,
            :filter_role
        )
    """)
    
    result = session.execute(
        query,
        {
            "search_term": params.search,
            "sort_column": params.sort,
            "sort_direction": params.order,
            "page_number": params.page,
            "page_size": params.size,
            "filter_role": params.role
        }
    ).fetchall()
    
    users = []
    for row in result:
        # Convert the SQLAlchemy Row to a dictionary
        # This approach works for most SQLAlchemy versions
        try:
            user_data = dict(zip([c.name for c in row._fields], row))
        except (AttributeError, TypeError):
            # Fallback for different SQLAlchemy versions
            user_data = {
                "user_id": row[0],
                "email": row[1],
                "full_name": row[2],
                "phone": row[3],
                "registration_date": row[4],
                "last_login": row[5],
                "is_active": row[6],
                "role": row[7]
            }
        
        users.append(UserResponse(**user_data))
    
    # Calculate total pages
 
    
    # Return the paginated response
    return PaginatedResponse(
        items=users,
        total_count=total_count,
      
    )


@router.get("/{user_id}/role/{role}", response_model=Union[Customer, Administrator, Employee, Distributor])
async def get_user_by_role(
    *,
    session: SessionDep,
    current_user: CurrentUser,
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
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get the specific role information based on the role typep
    if role == UserType.customer:
        customer = session.exec(select(Customer).where(Customer.user_id == user_id)).first()
        if not customer:
            raise HTTPException(status_code=404, detail="Customer information not found")
        return customer
    elif role == UserType.administrator:
        admin = session.exec(select(Administrator).where(Administrator.user_id == user_id)).first()
        if not admin:
            raise HTTPException(status_code=404, detail="Administrator information not found")
        return admin
    elif role == UserType.employee:
        employee = session.exec(select(Employee).where(Employee.user_id == user_id)).first()
        if not employee:
            raise HTTPException(status_code=404, detail="Employee information not found")
        return employee
    elif role == UserType.distributor:
        distributor = session.exec(select(Distributor).where(Distributor.user_id == user_id)).first()
        if not distributor:
            raise HTTPException(status_code=404, detail="Distributor information not found")
        return distributor
    else:
        raise HTTPException(status_code=400, detail="Invalid role type")


@router.get(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=UsersPublic,
)
def read_users(session: SessionDep, skip: int = 0, limit: int = 100) -> Any:
    """
    Retrieve users.
    """

    count_statement = select(func.count()).select_from(User)
    count = session.exec(count_statement).one()

    statement = select(User).offset(skip).limit(limit)
    users = session.exec(statement).all()

    return UsersPublic(data=users, count=count)


@router.post(
    "/", dependencies=[Depends(get_current_active_superuser)], response_model=UserPublic
)
def create_user(*, session: SessionDep, user_in: UserCreate) -> Any:
    """
    Create new user.
    """
    user = user.get_user_by_email(session=session, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )

    user = user.create_user(session=session, user_create=user_in)
    if settings.emails_enabled and user_in.email:
        email_data = generate_new_account_email(
            email_to=user_in.email, username=user_in.email, password=user_in.password
        )
        send_email(
            email_to=user_in.email,
            subject=email_data.subject,
            html_content=email_data.html_content,
        )
    return user


@router.patch("/me", response_model=UserPublic)
def update_user_me(
    *, session: SessionDep, user_in: UserUpdateMe, current_user: CurrentUser
) -> Any:
    """
    Update own user.
    """

    if user_in.email:
        existing_user = user.get_user_by_email(session=session, email=user_in.email)
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(
                status_code=409, detail="User with this email already exists"
            )
    user_data = user_in.model_dump(exclude_unset=True)
    current_user.sqlmodel_update(user_data)
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    return current_user


@router.patch("/me/password", response_model=Message)
def update_password_me(
    *, session: SessionDep, body: UpdatePassword, current_user: CurrentUser
) -> Any:
    """
    Update own password.
    """
    if not verify_password(body.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect password")
    if body.current_password == body.new_password:
        raise HTTPException(
            status_code=400, detail="New password cannot be the same as the current one"
        )
    hashed_password = get_password_hash(body.new_password)
    current_user.hashed_password = hashed_password
    session.add(current_user)
    session.commit()
    return Message(message="Password updated successfully")


@router.get("/me", response_model=UserPublic)
def read_user_me(current_user: CurrentUser) -> Any:
    """
    Get current user.
    """
    return current_user


@router.delete("/me", response_model=Message)
def delete_user_me(session: SessionDep, current_user: CurrentUser) -> Any:
    """
    Delete own user.
    """
    if current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="Super users are not allowed to delete themselves"
        )
    session.delete(current_user)
    session.commit()
    return Message(message="User deleted successfully")


@router.post("/signup", response_model=UserPublic)
def register_user(session: SessionDep, user_in: UserRegister) -> Any:
    """
    Create new user without the need to be logged in.
    """
    userdb = user.get_user_by_email(session=session, email=user_in.email)
    if userdb:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system",
        )
    user_create = UserCreate.model_validate(user_in)
    userdb = user.create_user(session=session, user_create=user_create)
    return userdb


@router.get("/{user_id}", response_model=UserPublic)
def read_user_by_id(
    user_id: uuid.UUID, session: SessionDep, current_user: CurrentUser
) -> Any:
    """
    Get a specific user by id.
    """
    user = session.get(User, user_id)
    if user == current_user:
        return user
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="The user doesn't have enough privileges",
        )
    return user


@router.patch(
    "/{user_id}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=UserPublic,
)
def update_user(
    *,
    session: SessionDep,
    user_id: uuid.UUID,
    user_in: UserUpdate,
) -> Any:
    """
    Update a user.
    """

    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )
    if user_in.email:
        existing_user = user.get_user_by_email(session=session, email=user_in.email)
        if existing_user and existing_user.id != user_id:
            raise HTTPException(
                status_code=409, detail="User with this email already exists"
            )

    db_user = user.update_user(session=session, db_user=db_user, user_in=user_in)
    return db_user


@router.delete("/{user_id}", dependencies=[Depends(get_current_active_superuser)])
def delete_user(
    session: SessionDep, current_user: CurrentUser, user_id: uuid.UUID
) -> Message:
    """
    Delete a user.
    """
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user == current_user:
        raise HTTPException(
            status_code=403, detail="Super users are not allowed to delete themselves"
        )
    session.delete(user)
    session.commit()
    return Message(message="User deleted successfully")


@router.patch("/{user_id}/role/{role}", response_model=Union[Customer, Administrator, Employee, Distributor])
async def update_user_by_role(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    user_id: int,
    role: UserType,
    update_data: Dict = Body(...)
):
    print(update_data)
    """
    Update user role-specific information based on their ID and role.
    Only accessible by administrators.
    """
    if current_user.role != UserType.administrator:
        raise HTTPException(
            status_code=403,
            detail="Only administrators can access this endpoint"
        )

    # Get the base user first
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get and update the specific role information based on the role type
    if role == UserType.customer:
        validated_data = CustomerBase(**update_data)
        customer = session.exec(select(Customer).where(Customer.user_id == user_id)).first()
        if not customer:
            raise HTTPException(status_code=404, detail="Customer information not found")
        for key, value in validated_data.model_dump(exclude_unset=True).items():
            setattr(customer, key, value)
        session.add(customer)
        session.commit()
        session.refresh(customer)
        return customer
        
    elif role == UserType.administrator:
        validated_data = AdministratorBase(**update_data)
        admin = session.exec(select(Administrator).where(Administrator.user_id == user_id)).first()
        if not admin:
            raise HTTPException(status_code=404, detail="Administrator information not found")
        for key, value in validated_data.model_dump(exclude_unset=True).items():
            setattr(admin, key, value)
        print(admin)
        session.add(admin)
        session.commit()
        session.refresh(admin)
        return admin
        
    elif role == UserType.employee:
        validated_data = EmployeeBase(**update_data)
        employee = session.exec(select(Employee).where(Employee.user_id == user_id)).first()
        if not employee:
            raise HTTPException(status_code=404, detail="Employee information not found")
        for key, value in validated_data.model_dump(exclude_unset=True).items():
            setattr(employee, key, value)
        session.add(employee)
        session.commit()
        session.refresh(employee)
        return employee
        
    elif role == UserType.distributor:
        validated_data = DistributorBase(**update_data)
        distributor = session.exec(select(Distributor).where(Distributor.user_id == user_id)).first()
        if not distributor:
            raise HTTPException(status_code=404, detail="Distributor information not found")
        for key, value in validated_data.model_dump(exclude_unset=True).items():
            setattr(distributor, key, value)
        session.add(distributor)
        session.commit()
        session.refresh(distributor)
        return distributor
        
    else:
        raise HTTPException(status_code=400, detail="Invalid role type")


@router.patch("/{user_id}/update", response_model=UserPublic)
async def update_user_table(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    user_id: int,
    update_data: Dict = Body(...)
):
    """
    Update user information in the users table.
    Only accessible by administrators.
    """
    if current_user.role != UserType.administrator:
        raise HTTPException(
            status_code=403,
            detail="Only administrators can access this endpoint"
        )

    # Get the user
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Validate and update the data
    try:
        # Update only the fields that are provided in update_data
        for key, value in update_data.items():
            if hasattr(user, key):
                setattr(user, key, value)
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid field: {key}"
                )

        # If email is being updated, check for duplicates
        if "email" in update_data:
            existing_user = user.get_user_by_email(session=session, email=update_data["email"])
            if existing_user and existing_user.user_id != user_id:
                raise HTTPException(
                    status_code=409,
                    detail="User with this email already exists"
                )

        session.add(user)
        session.commit()
        session.refresh(user)
        return user

    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

