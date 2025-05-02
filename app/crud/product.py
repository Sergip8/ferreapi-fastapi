import datetime
from typing import List, Optional, Dict, Any, Tuple
from decimal import Decimal
from sqlmodel import Session, select, or_, col, and_
from sqlalchemy.orm import aliased
from app.models import (
    Inventory, 
    Product, 
    Brand, 
    Promotion, 
    TechnicalSpecification, 
    Category,
    ProductStatus
)
from app.schemas import DetailedProductView

def get_products_paginated(
    *,
    session: Session,
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    category_ids: Optional[List[int]] = None,
    brand_ids: Optional[List[int]] = None,
    min_price: Optional[Decimal] = None,
    max_price: Optional[Decimal] = None,
    sort_by: Optional[str] = None,
    sort_order: Optional[str] = "asc",
    attributes: Optional[Dict[str, List[str]]] = None
) -> tuple[List[Dict[str, Any]], int, Dict[str, Any]]:
    """Get products with filters and sorting"""

    ParentCategory = aliased(Category)

    query = (
        select(
            Product,
            Brand.name.label("brand_name"),
            Category.category_name.label("category_name"),
            ParentCategory.category_name.label("parent_category_name")
          
        )
        .join(Brand, Product.brand_id == Brand.brand_id, isouter=True)
        .join(Category, Product.subcategory_id == Category.category_id, isouter=True)
        .join(ParentCategory, Product.category_id == ParentCategory.category_id, isouter=True)
    )

    if search:
        query = query.where(
            or_(
                Product.name.ilike(f"%{search}%"),
                Product.product_code.ilike(f"%{search}%"),
                Product.description.ilike(f"%{search}%")
            )
        )

    if category_ids:
        query = query.where(or_(
            Product.category_id.in_(category_ids),
            Product.subcategory_id.in_(category_ids)
        ))

    if brand_ids:
        query = query.where(Product.brand_id.in_(brand_ids))

    if min_price is not None:
        query = query.where(Product.regular_price >= min_price)

    if max_price is not None:
        query = query.where(Product.regular_price <= max_price)

    if attributes:
        for attr_key, attr_values in attributes.items():
            if attr_values:
                query = query.where(
                    Product.attributes[attr_key].astext.in_(attr_values)
                )

    if sort_by == "price":
        order = Product.regular_price.desc() if sort_order == "desc" else Product.regular_price
        query = query.order_by(order)
    elif sort_by == "name":
        order = Product.name.desc() if sort_order == "desc" else Product.name
        query = query.order_by(order)

    all_results = session.exec(query).all()
    total = len(all_results)
    query = query.offset(skip).limit(limit)
    results = session.exec(query).all()

    products = []
    for result in results:
        product_dict = result[0].dict()
        product_dict.update({
            "brand_name": result[1],
            "category_name": result[2],
            "parent_category_name": result[3]
        })
        products.append(product_dict)

    return products, total

def get_products(
    *,
    session: Session,
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    category_ids: Optional[List[int]] = None,
    brand_ids: Optional[List[int]] = None,
    min_price: Optional[Decimal] = None,
    max_price: Optional[Decimal] = None,
    sort_by: Optional[str] = None,
    sort_order: Optional[str] = "asc",
    attributes: Optional[Dict[str, List[str]]] = None
) -> tuple[List[Dict[str, Any]], int, Dict[str, Any]]:
    """Get products with filters and sorting"""

    ParentCategory = aliased(Category)

    query = (
        select(
            Product,
            Brand.name.label("brand_name"),
            Category.category_name.label("category_name"),
            ParentCategory.category_name.label("parent_category_name")
          
        )
        .join(Brand, Product.brand_id == Brand.brand_id, isouter=True)
        .join(Category, Product.subcategory_id == Category.category_id, isouter=True)
        .join(ParentCategory, Product.category_id == ParentCategory.category_id, isouter=True)
    )

    if search:
        query = query.where(
            or_(
                Product.name.ilike(f"%{search}%"),
                Product.product_code.ilike(f"%{search}%"),
                Product.description.ilike(f"%{search}%")
            )
        )

    if category_ids:
        query = query.where(or_(
            Product.category_id.in_(category_ids),
            Product.subcategory_id.in_(category_ids)
        ))

    if brand_ids:
        query = query.where(Product.brand_id.in_(brand_ids))

    if min_price is not None:
        query = query.where(Product.regular_price >= min_price)

    if max_price is not None:
        query = query.where(Product.regular_price <= max_price)

    if attributes:
        for attr_key, attr_values in attributes.items():
            if attr_values:
                query = query.where(
                    Product.attributes[attr_key].astext.in_(attr_values)
                )

    if sort_by == "price":
        order = Product.regular_price.desc() if sort_order == "desc" else Product.regular_price
        query = query.order_by(order)
    elif sort_by == "name":
        order = Product.name.desc() if sort_order == "desc" else Product.name
        query = query.order_by(order)

    all_results = session.exec(query).all()
    total = len(all_results)

    price_range = {
        "min": min((r[0].regular_price for r in all_results), default=Decimal("0")),
        "max": max((r[0].regular_price for r in all_results), default=Decimal("0"))
    }

    # Brands
    brand_counts = {}
    for r in all_results:
        if r[0].brand_id and r[1]:
            if r[0].brand_id not in brand_counts:
                brand_counts[r[0].brand_id] = {"id": r[0].brand_id, "name": r[1], "count": 0}
            brand_counts[r[0].brand_id]["count"] += 1
    brands = list(brand_counts.values())

    # Categories
    category_counts = {}
    for r in all_results:
        if r[0].category_id and r[2]:
            if r[0].category_id not in category_counts:
                category_counts[r[0].category_id] = {
                    "id": r[0].category_id,
                    "name": r[2],
                    "parent_name": r[3],
                    "count": 0
                }
            category_counts[r[0].category_id]["count"] += 1
    categories = list(category_counts.values())

    # Attributes
    attribute_counts = {}
    for r in all_results:
        if r[0].attributes:
            for attr, value in r[0].attributes.items():
                if attr not in attribute_counts:
                    attribute_counts[attr] = {"name": attr, "values": {}}
                if value:
                    if isinstance(value, list):
                        for val in value:
                            str_val = str(val)
                            if str_val:
                                attribute_counts[attr]["values"][str_val] = attribute_counts[attr]["values"].get(str_val, 0) + 1
                    else:
                        str_val = str(value)
                        attribute_counts[attr]["values"][str_val] = attribute_counts[attr]["values"].get(str_val, 0) + 1

    for attr in attribute_counts:
        attribute_counts[attr]["values"] = [
            {"value": val, "count": count}
            for val, count in attribute_counts[attr]["values"].items()
        ]
        attribute_counts[attr]["values"].sort(key=lambda x: x["value"])

    attributes_result = list(attribute_counts.values())
    attributes_result.sort(key=lambda x: x["name"])

    filter_values = {
        "brands": brands,
        "categories": categories,
        "attributes": attributes_result,
        "price_range": price_range
    }

    query = query.offset(skip).limit(limit)
    results = session.exec(query).all()

    products = []
    for result in results:
        product_dict = result[0].dict()
        product_dict.update({
            "brand_name": result[1],
            "category_name": result[2],
            "parent_category_name": result[3]
        })
        products.append(product_dict)

    return products, total, filter_values

async def get_detailed_product(db: Session, product_id: int) -> Optional[DetailedProductView]:
    """Get detailed product information including related data"""
    # Get the base product with related names
    ParentCategory = aliased(Category)
    query = (
        select(
            Product,
            Brand.name.label("brand_name"),
            Category.category_name.label("category_name"),
            ParentCategory.category_name.label("parent_category_name")
        )

        .join(Brand, Product.brand_id == Brand.brand_id, isouter=True)
        .join(Category, Product.category_id == Category.category_id, isouter=True)
         .join(ParentCategory, Product.subcategory_id == ParentCategory.category_id, isouter=True)
        .where(Product.product_id == product_id)
    )
    
    result = db.exec(query).first()
    if not result:
        return None
    
    product = result[0]
    
    # Get inventory information
    inventory = db.exec(
        select(Inventory).where(Inventory.product_id == product_id)
    ).first()
    
    # Get technical specifications
    tech_specs = db.exec(
        select(TechnicalSpecification).where(TechnicalSpecification.product_id == product_id)
    ).first()
    
    # Get active promotions
    current_date = datetime.datetime.now()
    active_promotions = db.exec(
        select(Promotion)
        .where(
            Promotion.product_id == product_id,
            Promotion.start_date <= current_date,
            Promotion.end_date >= current_date,
            Promotion.status == "active"
        )
    ).all()
    
    # Create detailed view with names
    product_dict = product.dict()
    product, brand_name, category_name, parent_category_name = result
    product_dict.update({
    "brand_name": brand_name,
    "category_name": category_name,
    "parent_category_name": parent_category_name
})
    
    detailed_view = DetailedProductView(
        **product_dict,
        inventory=inventory,
        technical_specs=tech_specs,
        active_promotions=active_promotions,
        stock_status="In Stock" if (inventory and inventory.available_quantity > 0) else "Out of Stock"
    )
    
    return detailed_view

def get_suggested_products(
    *,
    session: Session,
    current_product: DetailedProductView,
    limit: int = 4
) -> Tuple[List[Dict[str, Any]], int]:
    """Get suggested products based on the current product's attributes"""
    
    # Calculate price range (20% above and below current price)
    price_range = Decimal("0.2")  # 20% range
    min_price = current_product.regular_price * (1 - price_range)
    max_price = current_product.regular_price * (1 + price_range)
    
    # Build the query
    ParentCategory = aliased(Category)
    query = (
        select(
            Product,
            Brand.name.label("brand_name"),
            Category.category_name.label("category_name"),
            ParentCategory.category_name.label("parent_category_name")
        )
        .join(Brand, Product.brand_id == Brand.brand_id, isouter=True)
        .join(Category, Product.subcategory_id == Category.category_id, isouter=True)
        .join(ParentCategory, Product.category_id == ParentCategory.category_id, isouter=True)
        .where(
            and_(
                # Exclude current product
                Product.product_id != current_product.product_id,
                # Only active products
                Product.status == ProductStatus.active,
                # Price within range
                Product.regular_price >= min_price,
                Product.regular_price <= max_price,
                # Same category or subcategory
                or_(
                    Product.category_id == current_product.category_id,
                    Product.subcategory_id == current_product.subcategory_id
                )
            )
        )
    )
    
    # If product has a brand, prioritize same brand products
    if current_product.brand_id:
        query = query.order_by(
            (Product.brand_id == current_product.brand_id).desc(),
            Product.regular_price
        )
    else:
        query = query.order_by(Product.regular_price)
    
    # Execute query
    results = session.exec(query.limit(limit)).all()
    
    # Format results
    products = []
    for result in results:
        product_dict = result[0].dict()
        product_dict.update({
            "brand_name": result[1],
            "category_name": result[2],
            "parent_category_name": result[3]
        })
        products.append(product_dict)
    
    return products, len(products)

def get_quick_search_products(
    *,
    session: Session,
    search: str,
    limit: int = 5
) -> List[Dict[str, Any]]:
    """
    Quick search for products that only returns essential fields for search bar dropdown.
    Returns a list of products with minimal fields (id, name, price, image, description).
    """
    query = (
        select(
            Product.product_id,
            Product.name,
            Product.description,
            Product.regular_price,
            Product.sale_price,
            Product.image_url,
            Product.product_code
        )
        .where(
            and_(
                Product.status == ProductStatus.active,
                or_(
                    Product.name.ilike(f"%{search}%"),
                    Product.product_code.ilike(f"%{search}%"),
                    Product.description.ilike(f"%{search}%")
                )
            )
        )
        .order_by(Product.name)
        .limit(limit)
    )
    
    results = session.exec(query).all()
    
    # Convert results to list of dictionaries
    products = []
    for result in results:
        product_dict = {
            "product_id": result[0],
            "name": result[1],
            "description": result[2],
            "regular_price": result[3],
            "sale_price": result[4],
            "image_url": result[5],
            "product_code": result[6]
        }
        products.append(product_dict)
    
    return products
