from typing import Optional, Any, Dict, List
from decimal import Decimal
import datetime
from sqlmodel import SQLModel
from .models import (
    ProductBase, 
    InventoryBase,
    TechnicalSpecificationBase,
    PromotionBase,
    BrandBase,
    PromotionType
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
    # created_at: datetime.datetime
    # updated_at: datetime.datetime
    material_type_name: Optional[str] = None
    brand_name: Optional[str] = None
    category_name: Optional[str] = None
    parent_category_name: Optional[str] = None

class PaginatedUsersRequest(SQLModel):
    search: Optional[str] = None
    sort: str = "user_id"
    order: str = "ASC"
    page: int = 1
    size: int = 10
    role: Optional[str] = None

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
    created_at: datetime.datetime
    updated_at: datetime.datetime
    material_type_name: Optional[str] = None
    brand_name: Optional[str] = None
    category_name: Optional[str] = None
    parent_category_name: Optional[str] = None
    
    # Related information
    inventory: Optional[InventoryBase] = None
    technical_specs: Optional[TechnicalSpecificationBase] = None
    active_promotions: Optional[list[PromotionBase]] = None
    brand: Optional[BrandBase] = None
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
