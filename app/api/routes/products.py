from typing import List, Optional
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from app.api.deps import get_db
from app.crud.product import get_detailed_product, get_products, get_suggested_products, get_quick_search_products
from app.models import Product
from app.schemas import DetailedProductView, ProductFilterRequest, ProductBasicListResponse, ProductListResponse, ProductListResponsePaginated, ProductListView, ProductFilterValues, ProductQuickSearchView, QuickProductSearchResponse

router = APIRouter()

@router.post("/", response_model=ProductListResponse)
def read_products(
    payload: ProductFilterRequest,
    db: Session = Depends(get_db),
):
    """
    Retrieve products with filters and sorting.

    - **skip**: Number of products to skip (pagination)
    - **limit**: Maximum number of products to return (pagination)
    - **search**: Search in name, code and description
    - **category_ids**: Filter by category or subcategory IDs
    - **brand_ids**: Filter by brand IDs
    - **min_price**: Minimum price filter
    - **max_price**: Maximum price filter
    - **sort_by**: Sort by "price" or "name"
    - **sort_order**: Sort order "asc" or "desc"
    - **attributes**: Dictionary of attributes and their allowed values
    """
    products, total, filter_values = get_products(
        session=db,
        skip=payload.skip,
        limit=payload.limit,
        search=payload.search,
        brand_ids=payload.brand_ids,
        category_ids=payload.category_ids,
        min_price=payload.min_price,
        max_price=payload.max_price,
        sort_by=payload.sort_by,
        sort_order=payload.sort_order,
        attributes=payload.attributes
    )
    return ProductListResponse(
        data=[ProductListView(**product) for product in products],
        total=total,
        filter_values=ProductFilterValues(**filter_values)
    )

@router.post("/paginated", response_model=ProductListResponse)
def read_products_paginated(
    payload: ProductFilterRequest,
    db: Session = Depends(get_db),
):
    """
    Retrieve products with filters and sorting.

    - **skip**: Number of products to skip (pagination)
    - **limit**: Maximum number of products to return (pagination)
    - **search**: Search in name, code and description
    - **category_ids**: Filter by category or subcategory IDs
    - **brand_ids**: Filter by brand IDs
    - **min_price**: Minimum price filter
    - **max_price**: Maximum price filter
    - **sort_by**: Sort by "price" or "name"
    - **sort_order**: Sort order "asc" or "desc"
    - **attributes**: Dictionary of attributes and their allowed values
    """
    products, total, filter_values = get_products(
        session=db,
        skip=payload.skip,
        limit=payload.limit,
        search=payload.search,
        brand_ids=payload.brand_ids,
        category_ids=payload.category_ids,
        min_price=payload.min_price,
        max_price=payload.max_price,
        sort_by=payload.sort_by,
        sort_order=payload.sort_order,
        attributes=payload.attributes
    )
    return ProductListResponsePaginated(
        data=[ProductListView(**product) for product in products],
        total=total,
    )

@router.get("/{product_id}", response_model=DetailedProductView)
async def get_product_detail(
    product_id: int,
    db: Session = Depends(get_db),
) -> DetailedProductView:
    """
    Get detailed information about a specific product, including:
    - Base product information
    - Inventory status
    - Technical specifications
    - Active promotions
    - Material type and brand details
    """
    product = await get_detailed_product(db=db, product_id=product_id)
    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )
    return product

@router.get("/{product_id}/suggested", response_model=ProductBasicListResponse)
async def get_suggested_products_route(
    product_id: int,
    limit: int = Query(default=4, ge=1, le=10),
    db: Session = Depends(get_db),
) -> ProductListResponse:
    """
    Get suggested products based on the current product's:
    - Category/subcategory
    - Brand
    - Price range
    - Active status
    
    Returns a list of suggested products that are similar to the current product.
    """
    # First get the current product details
    current_product = await get_detailed_product(db=db, product_id=product_id)
    if not current_product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )
    
    # Get suggested products
    suggested_products, total = get_suggested_products(
        session=db,
        current_product=current_product,
        limit=limit
    )
    
    return ProductBasicListResponse(
       data = [ProductListView(**product) for product in suggested_products],
       
    )

@router.get("/search/quick", response_model=QuickProductSearchResponse)
async def quick_product_search(
    search: str = Query(..., min_length=1, description="Search term to find products"),
    limit: int = Query(default=5, ge=1, le=10, description="Maximum number of results to return"),
    db: Session = Depends(get_db),
) -> QuickProductSearchResponse:
    """
    Quick search for products in a search bar dropdown.
    Returns basic product information including name, price, image, and description.
    """
    products = get_quick_search_products(
        session=db,
        search=search,
        limit=limit
    )
    
    return QuickProductSearchResponse(
        data=[ProductQuickSearchView(**product) for product in products]
    )
