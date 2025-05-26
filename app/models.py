import datetime
from enum import Enum as PyEnum
from decimal import Decimal
from typing import List, Optional
import uuid

from pydantic import BaseModel, EmailStr
from sqlalchemy import Column
from sqlmodel import Enum, Field, Relationship, SQLModel
from sqlalchemy.dialects.postgresql import JSONB


class UserType(PyEnum):
    customer = "customer"
    distributor = "distributor"
    administrator = "administrator"
    employee = "employee"

class ProductStatus(PyEnum):
    active = "active"
    out_of_stock = "out_of_stock"
    by_order = "by_order"
    discontinued = "discontinued"

class PromotionType(PyEnum):
    percentage = "percentage"
    fixed_amount = "fixed_amount"
    bundle = "bundle"

class PromotionStatus(PyEnum):
    active = "active"
    inactive = "inactive"

class OrderStatus(PyEnum):
    pending = "pending"
    processing = "processing"
    shipped = "shipped"
    delivered = "delivered"
    cancelled = "cancelled"

class ManufacturingStatus(PyEnum):
    operational = "operational"
    maintenance = "maintenance"
    repair = "repair"
    offline = "offline"

class QualityCheckStatus(PyEnum):
    pending = "pending"
    passed = "passed"
    failed = "failed"

class QCStatus(PyEnum):
    passed = "passed"
    failed = "failed"

class PaymentStatus(PyEnum):
    paid = "paid"
    partially_paid = "partially_paid"
    pending = "pending"
    overdue = "overdue"

class ShippingStatus(PyEnum):
    processing = "processing"
    shipped = "shipped"
    in_transit = "in_transit"
    delivered = "delivered"
    failed = "failed"

class ReturnStatus(PyEnum):
    pending = "pending"
    processed = "processed"
    rejected = "rejected"

class BaseModelWithConfig(SQLModel):
    model_config = {"arbitrary_types_allowed": True}

# Generic message
class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=40)


# --- Category Models ---
class CategoryBase(SQLModel):
    category_name: str = Field(max_length=100)
    parent_category_id: Optional[int] = Field(default=None, foreign_key="categories.category_id")
    description: Optional[str] = None
    display_order: int = 0
    image_url: Optional[str] = Field(None, max_length=255)
    is_active: bool = True


class CategoryCreate(CategoryBase):
    pass


class Category(CategoryBase, table=True):
    __tablename__= "categories"
    category_id: int = Field(default=None, primary_key=True, sa_column_kwargs={"autoincrement": True})
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    updated_at: datetime.datetime = Field(default_factory=datetime.datetime.now)

    parent_category: Optional["Category"] = Relationship(
        sa_relationship_kwargs={
            "remote_side": "[Category.category_id]",
            "back_populates": "subcategories"
        }
    )
    subcategories: List["Category"] = Relationship(
        sa_relationship_kwargs={
            "back_populates": "parent_category"
        }
    )



# --- Base User Model ---
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


# --- User Database Model ---
class User(UserBase, table=True):
    __tablename__ = "users"
    user_id: int = Field(default=None, primary_key=True)
    password: str = Field(max_length=255)
    role: UserType = Field(default=UserType.customer)
    registration_date: datetime.datetime = Field(default_factory=datetime.datetime.now)
    customer: Optional["Customer"] = Relationship(back_populates="user")
    distributor: Optional["Distributor"] = Relationship(back_populates="user")
    administrator: Optional["Administrator"] = Relationship(back_populates="user")
    employee: Optional["Employee"] = Relationship(back_populates="user")
    last_login: Optional[datetime.datetime] = None



# --- Customer Models ---

class Customer(CustomerBase, table=True):
    __tablename__ = "customers"
    customer_id: int = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.user_id", unique=True)
    user: Optional[User] = Relationship(back_populates="customer")



# --- Distributor Models ---
class DistributorBase(SQLModel):
    company_name: str = Field(max_length=255)
    tax_id: Optional[str] = Field(default=None, max_length=20)
    business_address: str
    distribution_zone: Optional[str] = None
    credit_limit: Decimal = Field(default=Decimal("0.00"), max_digits=10, decimal_places=2)
    contract_date: Optional[datetime.date] = None


class Distributor(DistributorBase, table=True):
    __tablename__ = "distributors"
    distributor_id: int = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.user_id", unique=True)
    user: Optional[User] = Relationship(back_populates="distributor")



# --- Administrator Models ---
class AdministratorBase(SQLModel):
    access_level: str = Field(max_length=20)
    department: Optional[str] = Field(default=None, max_length=100)
    can_create_users: bool = Field(default=False)
    can_modify_products: bool = Field(default=False)
    can_view_reports: bool = Field(default=False)
    assignment_date: Optional[datetime.date] = None


class Administrator(AdministratorBase, table=True):
    __tablename__ = "administrators"
    administrator_id: int = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.user_id", unique=True)
    user: Optional[User] = Relationship(back_populates="administrator")


# --- Employee Models ---
class EmployeeBase(SQLModel):
    position: str = Field(max_length=100)
    department: str = Field(max_length=100)
    hire_date: datetime.date
    salary: Optional[Decimal] = Field(default=None, max_digits=10, decimal_places=2)
    employee_number: Optional[str] = Field(default=None, max_length=20, unique=True)
    schedule: Optional[str] = Field(default=None, max_length=100)


class Employee(EmployeeBase, table=True):
    __tablename__ = "employees"
    employee_id: Optional[int] = Field(default=None, primary_key=True) # Hacer Optional para creación
    user_id: int = Field(foreign_key="users.user_id", unique=True, index=True)
    supervisor_id: Optional[int] = Field(default=None, foreign_key="employees.employee_id", index=True)
    user: Optional[User] = Relationship(back_populates="employee")
    supervisor: Optional["Employee"] = Relationship(
        back_populates="subordinates",
        sa_relationship_kwargs={
            "remote_side": "[Employee.employee_id]", # Especifica la columna remota
            "foreign_keys": "[Employee.supervisor_id]" # Especifica la FK a usar
            }
    )
    subordinates: List["Employee"] = Relationship(
        back_populates="supervisor",
         sa_relationship_kwargs={
             "foreign_keys": "[Employee.supervisor_id]" # Especifica la FK a usar
             }
    )


# --- User Create/Update Models ---
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)
    role: UserType


class UserUpdate(SQLModel):
    email: Optional[str] = Field(default=None, max_length=255)
    full_name: Optional[str] = Field(default=None, max_length=100)
    phone: Optional[str] = Field(default=None, max_length=20)
    is_active: Optional[bool] = None


class UpdatePassword(SQLModel):
    current_password: str
    new_password: str = Field(min_length=8, max_length=40)


class UserRegister(UserBase):
    password: str = Field(min_length=8, max_length=40)
    role: UserType = UserType.customer


class UserResponse(BaseModel):
    user_id: int
    email: str
    full_name: Optional[str] = None
    phone: Optional[str] = None
    registration_date: datetime.datetime
    last_login: Optional[datetime.datetime] = None
    is_active: bool
    role: str

    class Config:
        orm_mode = True

class PaginatedResponse(BaseModel):
    items: List[UserResponse]
    total_count: int
 


class UserUpdateMe(SQLModel):
    full_name: Optional[str] = Field(default=None, max_length=100)
    phone: Optional[str] = Field(default=None, max_length=20)


# --- User Public Model ---
class UserPublic(UserBase):
    user_id: int
    role: UserType
    registration_date: datetime.datetime
    last_login: Optional[datetime.datetime] = None

class UsersPublic(SQLModel):
    users: List[UserPublic]

# --- Brands Models ---
class BrandBase(SQLModel):
    name: str = Field(max_length=50)
    description: Optional[str] = None


class BrandCreate(BrandBase):
    pass


class Brand(BrandBase, table=True):
    __tablename__ = "brands"
    brand_id: int = Field(default=None, primary_key=True, sa_column_kwargs={"autoincrement": True})


# --- Products Models ---
class ProductBase(BaseModelWithConfig):
    product_code: str = Field(max_length=50, unique=True)
    name: str = Field(max_length=100)
    description: Optional[str] = None
    regular_price: Decimal = Field(max_digits=10, decimal_places=2)
    sale_price: Optional[Decimal] = Field(default=None, max_digits=10, decimal_places=2)
    brand_id: Optional[int] = Field(default=None, foreign_key="brands.brand_id")
    unit_of_measure: str = Field(max_length=30)
    image_url: Optional[str] = Field(default=None, max_length=255)
    image_url_details: Optional[str] = Field(default=None, max_length=255)
    status: ProductStatus = Field(default=ProductStatus.active)
    category_id: Optional[int] = Field(default=None, foreign_key="categories.category_id")
    subcategory_id: Optional[int] = Field(default=None, foreign_key="categories.category_id")
    attributes: Optional[dict] = Field(default=None, sa_column=Column(JSONB))


class ProductCreate(ProductBase):
    pass


class Product(ProductBase, table=True):
    __tablename__ = "products"
    product_id: int = Field(default=None, primary_key=True, sa_column_kwargs={"autoincrement": True})
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    updated_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    
    brand: Optional[Brand] = Relationship()
    category: Optional["Category"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[Product.category_id]"}
    )
    subcategory: Optional["Category"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[Product.subcategory_id]"}
    )


# --- Suppliers Models ---
class SupplierBase(SQLModel):
    supplier_name: str = Field(max_length=100)
    contact_person: Optional[str] = Field(default=None, max_length=100)
    phone: Optional[str] = Field(default=None, max_length=20)
    email: Optional[str] = Field(default=None, max_length=100)
    address: Optional[str] = None
    supplier_type: Optional[str] = Field(default=None, max_length=50)
    payment_terms: Optional[str] = Field(default=None, max_length=50)
    lead_time: Optional[int] = None
    quality_rating: Optional[Decimal] = None
    active_status: bool = True


class SupplierCreate(SupplierBase):
    pass


class Supplier(SupplierBase, table=True):
    __tablename__ = "suppliers"
    supplier_id: int = Field(default=None, primary_key=True, sa_column_kwargs={"autoincrement": True})
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    updated_at: datetime.datetime = Field(default_factory=datetime.datetime.now)


# --- Inventory Models ---
class InventoryBase(SQLModel):
    product_id: int = Field(foreign_key="product.product_id")
    available_quantity: int = 0
    reserved_quantity: int = 0
    minimum_stock_level: int = 0
    maximum_stock_level: Optional[int] = None
    warehouse_location: Optional[str] = Field(default=None, max_length=50)
    warehouse_id: Optional[int] = None
    last_restock_date: Optional[datetime.date] = None
    last_count_date: Optional[datetime.date] = None


class InventoryCreate(InventoryBase):
    pass


class Inventory(InventoryBase, table=True):
    __tablename__ = "inventory"
    inventory_id: int = Field(default=None, primary_key=True, sa_column_kwargs={"autoincrement": True})
    updated_at: datetime.datetime = Field(default_factory=datetime.datetime.now)


# --- Promotions Models ---
class PromotionBase(BaseModelWithConfig):
    product_id: Optional[int] = Field(default=None, foreign_key="product.product_id")
    category_id: Optional[int] = Field(default=None, foreign_key="category.category_id")
    promotion_name: str = Field(max_length=100)
    promotion_type: PromotionType
    discount_percentage: Optional[Decimal] = None
    discount_amount: Optional[Decimal] = None
    minimum_purchase: Optional[Decimal] = None
    start_date: datetime.datetime
    end_date: datetime.datetime
    status: PromotionStatus = PromotionStatus.active


class PromotionCreate(PromotionBase):
    pass


class Promotion(PromotionBase, table=True):
    __tablename__= "promotions"
    promotion_id: int = Field(default=None, primary_key=True, sa_column_kwargs={"autoincrement": True})
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    updated_at: datetime.datetime = Field(default_factory=datetime.datetime.now)


# --- Orders Models ---
class OrderBase(BaseModelWithConfig):
    user_id: int = Field(foreign_key="user.user_id")
    order_status: OrderStatus = OrderStatus.pending
    payment_method: Optional[str] = Field(default=None, max_length=50)
    order_total: Decimal
    tax_amount: Decimal = Decimal("0.00")
    shipping_cost: Decimal = Decimal("0.00")
    discount_amount: Decimal = Decimal("0.00")
    shipping_address: Optional[str] = None
    billing_address: Optional[str] = None
    delivery_date: Optional[datetime.date] = None
    tracking_number: Optional[str] = Field(default=None, max_length=50)
    notes: Optional[str] = None


class OrderCreate(OrderBase):
    pass


class Order(OrderBase, table=True):
    __tablename__ = "orders"
    order_id: int = Field(default=None, primary_key=True, sa_column_kwargs={"autoincrement": True})
    order_date: datetime.datetime = Field(default_factory=datetime.datetime.now)


# --- Order Details Models ---
class OrderDetailBase(SQLModel):
    order_id: int = Field(foreign_key="order.order_id")
    product_id: int = Field(foreign_key="product.product_id")
    quantity: int
    unit_price: Decimal
    total_price: Decimal
    discount_applied: Decimal = Decimal("0.00")


class OrderDetailCreate(OrderDetailBase):
    pass


class OrderDetail(OrderDetailBase, table=True):
    __tablename__ = "order_details"
    order_detail_id: int = Field(default=None, primary_key=True)


# --- Raw Materials Inventory Models ---
class RawMaterialInventoryBase(SQLModel):
    material_name: str = Field(max_length=100)
    material_type: str = Field(max_length=50)
    supplier_id: Optional[int] = Field(default=None, foreign_key="supplier.supplier_id")
    quantity_available: Decimal = Decimal("0.0")
    unit_of_measure: str = Field(max_length=30)
    minimum_stock_level: Decimal = Decimal("0.0")
    cost_per_unit: Decimal
    location: Optional[str] = Field(default=None, max_length=50)
    last_purchase_date: Optional[datetime.date] = None
    expiration_date: Optional[datetime.date] = None


class RawMaterialInventoryCreate(RawMaterialInventoryBase):
    pass


class RawMaterialInventory(RawMaterialInventoryBase, table=True):
    __tablename__ = "raw_material_inventories"
    material_id: int = Field(default=None, primary_key=True, sa_column_kwargs={"autoincrement": True})
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    updated_at: datetime.datetime = Field(default_factory=datetime.datetime.now)


# --- Manufacturing Machines Models ---
class ManufacturingMachineBase(BaseModelWithConfig):
    machine_name: str = Field(max_length=100)
    machine_type: str = Field(max_length=50)
    purchase_date: Optional[datetime.date] = None
    maintenance_schedule: Optional[str] = None
    last_maintenance_date: Optional[datetime.date] = None
    operational_status: ManufacturingStatus = ManufacturingStatus.operational
    production_capacity: Optional[str] = Field(default=None, max_length=100)
    notes: Optional[str] = None


class ManufacturingMachineCreate(ManufacturingMachineBase):
    pass


class ManufacturingMachine(ManufacturingMachineBase, table=True):
    __tablename__ = "manufacturing_machines"
    machine_id: int = Field(default=None, primary_key=True, sa_column_kwargs={"autoincrement": True})


# --- Production Batches Models ---
class ProductionBatchBase(BaseModelWithConfig):
    production_date: datetime.date
    product_id: int = Field(foreign_key="product.product_id")
    quantity_produced: int
    material_used: Optional[str] = None
    operator_id: Optional[int] = Field(default=None, foreign_key="user.user_id")
    machine_id: Optional[int] = Field(default=None, foreign_key="manufacturingmachine.machine_id")
    quality_check_status: QualityCheckStatus = QualityCheckStatus.pending
    production_cost: Optional[Decimal] = None
    notes: Optional[str] = None


class ProductionBatchCreate(ProductionBatchBase):
    pass


class ProductionBatch(ProductionBatchBase, table=True):
    __tablename__ = "production_batches"
    batch_id: int = Field(default=None, primary_key=True, sa_column_kwargs={"autoincrement": True})
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)


# --- Quality Control Models ---
class QualityControlBase(BaseModelWithConfig):
    batch_id: int = Field(foreign_key="productionbatch.batch_id")
    inspector_id: Optional[int] = Field(default=None, foreign_key="user.user_id")
    check_date: datetime.date
    pressure_test_result: Optional[str] = Field(default=None, max_length=50)
    dimensional_check_result: Optional[str] = Field(default=None, max_length=50)
    visual_inspection_result: Optional[str] = Field(default=None, max_length=50)
    status: QCStatus
    rejection_reason: Optional[str] = None
    notes: Optional[str] = None


class QualityControlCreate(QualityControlBase):
    pass


class QualityControl(QualityControlBase, table=True):
    __tablename__ = "quality_controls"
    quality_check_id: int = Field(default=None, primary_key=True, sa_column_kwargs={"autoincrement": True})


# --- Invoice and Payments Models ---
class InvoicePaymentBase(BaseModelWithConfig):
    order_id: int = Field(foreign_key="order.order_id")
    invoice_number: str = Field(max_length=50)
    invoice_date: datetime.date
    due_date: datetime.date
    total_amount: Decimal
    tax_amount: Decimal = Decimal("0.00")
    payment_method: Optional[str] = Field(default=None, max_length=50)
    payment_status: PaymentStatus = PaymentStatus.pending
    payment_date: Optional[datetime.date] = None
    notes: Optional[str] = None


class InvoicePaymentCreate(InvoicePaymentBase):
    pass


class InvoicePayment(InvoicePaymentBase, table=True):
    __tablename__ = "invoice_payments"
    invoice_id: int = Field(default=None, primary_key=True, sa_column_kwargs={"autoincrement": True})


# --- Shipping and Delivery Models ---
class ShippingDeliveryBase(BaseModelWithConfig):
    order_id: int = Field(foreign_key="order.order_id")
    shipping_date: Optional[datetime.date] = None
    carrier_name: Optional[str] = Field(default=None, max_length=100)
    tracking_number: Optional[str] = Field(default=None, max_length=100)
    estimated_delivery_date: Optional[datetime.date] = None
    actual_delivery_date: Optional[datetime.date] = None
    shipping_cost: Decimal = Decimal("0.00")
    shipping_status: ShippingStatus = ShippingStatus.processing
    receiver_name: Optional[str] = Field(default=None, max_length=100)
    delivery_notes: Optional[str] = None


class ShippingDeliveryCreate(ShippingDeliveryBase):
    pass


class ShippingDelivery(ShippingDeliveryBase, table=True):
    __tablename__ = "shipping_deliveries"
    shipping_id: int = Field(default=None, primary_key=True, sa_column_kwargs={"autoincrement": True})


# --- Technical Specifications Models ---
class TechnicalSpecificationBase(SQLModel):
    product_id: int = Field(foreign_key="product.product_id")
    standard_compliance: Optional[str] = Field(default=None, max_length=100)
    certification_details: Optional[str] = None
    usage_recommendations: Optional[str] = None
    installation_guidelines: Optional[str] = None
    technical_drawing_url: Optional[str] = Field(default=None, max_length=255)
    safety_information: Optional[str] = None


class TechnicalSpecificationCreate(TechnicalSpecificationBase):
    pass


class TechnicalSpecification(TechnicalSpecificationBase, table=True):
    __tablename__= "technical_specifications"
    spec_id: int = Field(default=None, primary_key=True, sa_column_kwargs={"autoincrement": True})


# --- Customer Returns Models ---
class CustomerReturnBase(BaseModelWithConfig):
    order_id: int = Field(foreign_key="order.order_id")
    product_id: int = Field(foreign_key="product.product_id")
    return_date: datetime.date
    quantity_returned: int
    return_reason: Optional[str] = None
    inspection_result: Optional[str] = None
    refund_amount: Optional[Decimal] = None
    status: ReturnStatus = ReturnStatus.pending
    notes: Optional[str] = None


class CustomerReturnCreate(CustomerReturnBase):
    pass


class CustomerReturn(CustomerReturnBase, table=True):
    __tablename__ = "customer_returns"
    return_id: int = Field(default=None, primary_key=True, sa_column_kwargs={"autoincrement": True})