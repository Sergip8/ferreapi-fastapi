from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from pydantic import EmailStr
from .enums import UserType

class UserBase(SQLModel):
    email: str = Field(max_length=255, unique=True)
    full_name: Optional[str] = Field(default=None, max_length=100)
    phone: Optional[str] = Field(default=None, max_length=20)
    is_active: bool = Field(default=True)

class CustomerBase(SQLModel):
    shipping_address: Optional[str] = None
    billing_address: Optional[str] = None
    membership_level: str = Field(default="basic", max_length=20)
    birth_date: Optional[datetime.date] = None
    purchase_count: int = Field(default=0)

class DistributorBase(SQLModel):
    company_name: str = Field(max_length=255)
    tax_id: Optional[str] = Field(default=None, max_length=20)
    business_address: str
    distribution_zone: Optional[str] = None
    credit_limit: Decimal = Field(default=Decimal("0.00"), max_digits=10, decimal_places=2)
    contract_date: Optional[datetime.date] = None

class AdministratorBase(SQLModel):
    access_level: str = Field(max_length=20)
    department: Optional[str] = Field(default=None, max_length=100)
    can_create_users: bool = Field(default=False)
    can_modify_products: bool = Field(default=False)
    can_view_reports: bool = Field(default=False)
    assignment_date: Optional[datetime.date] = None

class EmployeeBase(SQLModel):
    position: str = Field(max_length=100)
    department: str = Field(max_length=100)
    hire_date: datetime.date
    salary: Optional[Decimal] = Field(default=None, max_digits=10, decimal_places=2)
    employee_number: Optional[str] = Field(default=None, max_length=20, unique=True)
    schedule: Optional[str] = Field(default=None, max_length=100)

class User(UserBase, table=True):
    __tablename__ = "users"
    user_id: int = Field(default=None, primary_key=True)
    password: str = Field(max_length=255)
    role: UserType = Field(default=UserType.customer)
    registration_date: datetime = Field(default_factory=datetime.now)
    customer: Optional["Customer"] = Relationship(back_populates="user")
    distributor: Optional["Distributor"] = Relationship(back_populates="user")
    administrator: Optional["Administrator"] = Relationship(back_populates="user")
    employee: Optional["Employee"] = Relationship(back_populates="user")
    last_login: Optional[datetime] = None

class Customer(CustomerBase, table=True):
    __tablename__ = "customers"
    customer_id: int = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.user_id", unique=True)
    user: Optional[User] = Relationship(back_populates="customer")

class Distributor(DistributorBase, table=True):
    __tablename__ = "distributors"
    distributor_id: int = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.user_id", unique=True)
    user: Optional[User] = Relationship(back_populates="distributor")

class Administrator(AdministratorBase, table=True):
    __tablename__ = "administrators"
    administrator_id: int = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.user_id", unique=True)
    user: Optional[User] = Relationship(back_populates="administrator")

class Employee(EmployeeBase, table=True):
    __tablename__ = "employees"
    employee_id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.user_id", unique=True, index=True)
    supervisor_id: Optional[int] = Field(default=None, foreign_key="employees.employee_id", index=True)
    user: Optional[User] = Relationship(back_populates="employee")
    supervisor: Optional["Employee"] = Relationship(
        back_populates="subordinates",
        sa_relationship_kwargs={
            "remote_side": "[Employee.employee_id]",
            "foreign_keys": "[Employee.supervisor_id]"
        }
    )
    subordinates: List["Employee"] = Relationship(
        back_populates="supervisor",
        sa_relationship_kwargs={
            "foreign_keys": "[Employee.supervisor_id]"
        }
    )

class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)
    role: UserType

class UserUpdate(SQLModel):
    email: Optional[str] = Field(default=None, max_length=255)
    full_name: Optional[str] = Field(default=None, max_length=100)
    phone: Optional[str] = Field(default=None, max_length=20)
    is_active: Optional[bool] = None

class UserRegister(UserBase):
    password: str = Field(min_length=8, max_length=40)
    role: UserType = UserType.customer

class UserResponse(SQLModel):
    user_id: int
    email: str
    full_name: Optional[str] = None
    phone: Optional[str] = None
    registration_date: datetime
    last_login: Optional[datetime] = None
    is_active: bool
    role: str

    class Config:
        orm_mode = True

class UserUpdateMe(SQLModel):
    full_name: Optional[str] = Field(default=None, max_length=100)
    phone: Optional[str] = Field(default=None, max_length=20)

class UserPublic(UserBase):
    user_id: int
    role: UserType
    registration_date: datetime
    last_login: Optional[datetime] = None

class UsersPublic(SQLModel):
    users: List[UserPublic] 