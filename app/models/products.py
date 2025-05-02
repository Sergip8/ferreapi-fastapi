from datetime import datetime
from typing import Optional, List, Dict, Any
from decimal import Decimal
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import SQLModel, Field, Relationship
from .base import BaseModelWithConfig
from .enums import ProductStatus

class ProductBase(BaseModelWithConfig):
    product_code: str = Field(max_length=50, unique=True)
    name: str = Field(max_length=100)
    description: Optional[str] = None
    regular_price: Decimal = Field(max_digits=10, decimal_places=2)
    sale_price: Optional[Decimal] = Field(default=None, max_digits=10, decimal_places=2)
    brand_id: Optional[int] = Field(default=None, foreign_key="brands.brand_id")
    unit_of_measure: str = Field(max_length=30)
    image_url: Optional[str] = Field(default=None, max_length=255)
    status: ProductStatus = Field(default=ProductStatus.active)
    category_id: Optional[int] = Field(default=None, foreign_key="categories.category_id")
    subcategory_id: Optional[int] = Field(default=None, foreign_key="categories.category_id")
    attributes: Optional[dict] = Field(default=None, sa_column=Column(JSONB))

class ProductCreate(ProductBase):
    pass

class Product(ProductBase, table=True):
    __tablename__ = "products"
    product_id: int = Field(default=None, primary_key=True, sa_column_kwargs={"autoincrement": True})
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    brand: Optional["Brand"] = Relationship()
    category: Optional["Category"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[Product.category_id]"}
    )
    subcategory: Optional["Category"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[Product.subcategory_id]"}
    )

class ProductQuickSearchView(SQLModel):
    product_id: int
    product_code: str 
    name: str 
    description: str
    regular_price: Optional[Decimal]
    sale_price: Optional[Decimal]
    image_url: str

class ProductListView(ProductBase):
    product_id: int
    material_type_name: Optional[str] = None
    brand_name: Optional[str] = None
    category_name: Optional[str] = None
    parent_category_name: Optional[str] = None

class ProductFilterRequest(SQLModel):
    skip: int = 0
    limit: int = 100
    search: Optional[str] = None
    category_ids: Optional[List[int]] = None
    brand_ids: Optional[List[int]] = None
    min_price: Optional[Decimal] = None
    max_price: Optional[Decimal] = None
    sort_by: Optional[str] = None  # Should be "price" or "name"
    sort_order: Optional[str] = "asc"  # "asc" or "desc"
    attributes: Optional[Dict[str, List[str]]] = None

class ProductFilterValues(SQLModel):
    brands: list[dict[str, Any]] 
    categories: list[dict[str, Any]]  
    attributes: list[dict[str, Any]] 
    price_range: dict[str, Decimal]

class ProductListResponsePaginated(SQLModel):
    data: list[ProductListView]
    total: int

class ProductListResponse(ProductListResponsePaginated):
    filter_values: Optional[ProductFilterValues] = None

class ProductBasicListResponse(SQLModel):
    data: list[ProductListView]

class QuickProductSearchResponse(SQLModel):
    data: list[ProductQuickSearchView]

class DetailedProductView(ProductBase):
    product_id: int
    created_at: datetime
    updated_at: datetime
    material_type_name: Optional[str] = None
    brand_name: Optional[str] = None
    category_name: Optional[str] = None
    parent_category_name: Optional[str] = None
    
    # Related information
    inventory: Optional["InventoryBase"] = None
    technical_specs: Optional["TechnicalSpecificationBase"] = None
    active_promotions: Optional[list["PromotionBase"]] = None
    brand: Optional["BrandBase"] = None
    stock_status: str = "No stock information"
    
    @property
    def is_on_sale(self) -> bool:
        return bool(self.active_promotions and len(self.active_promotions) > 0)
    
    @property
    def current_price(self) -> Decimal:
        if not self.is_on_sale or not self.active_promotions:
            return self.regular_price
            
        # Get the highest discount from active promotions
        highest_discount = Decimal("0.00")
        for promo in self.active_promotions:
            if promo.promotion_type == PromotionType.percentage and promo.discount_percentage:
                discount = self.regular_price * (promo.discount_percentage / Decimal("100.00"))
                highest_discount = max(highest_discount, discount)
            elif promo.promotion_type == PromotionType.fixed_amount and promo.discount_amount:
                highest_discount = max(highest_discount, promo.discount_amount)
        
        return max(self.regular_price - highest_discount, Decimal("0.00")) 