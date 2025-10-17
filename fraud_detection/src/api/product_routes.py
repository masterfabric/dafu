"""
DAFU - Data Analytics Functional Utilities
Product Management Routes
=========================
Endpoints for e-commerce product management and fraud monitoring

Author: MasterFabric
License: AGPL-3.0
"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_

from .database import get_db, User, Product, ProductStatus
from .auth import get_current_user, require_analyst

# Create router
router = APIRouter(prefix="/api/v1/products", tags=["Products"])


# ============================================================================
# Pydantic Models
# ============================================================================

class ProductCreate(BaseModel):
    """Product creation model"""
    sku: str = Field(..., min_length=1, max_length=100)
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    price: float = Field(..., gt=0)
    currency: str = Field(default="USD", max_length=3)
    cost: Optional[float] = Field(None, ge=0)
    category: Optional[str] = Field(None, max_length=100)
    subcategory: Optional[str] = Field(None, max_length=100)
    brand: Optional[str] = Field(None, max_length=100)
    tags: Optional[List[str]] = Field(default_factory=list)
    stock_quantity: int = Field(default=0, ge=0)
    low_stock_threshold: int = Field(default=10, ge=0)
    extra_data: Optional[dict] = Field(default_factory=dict)
    images: Optional[List[str]] = Field(default_factory=list)


class ProductUpdate(BaseModel):
    """Product update model"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    cost: Optional[float] = Field(None, ge=0)
    category: Optional[str] = Field(None, max_length=100)
    subcategory: Optional[str] = Field(None, max_length=100)
    brand: Optional[str] = Field(None, max_length=100)
    tags: Optional[List[str]] = None
    stock_quantity: Optional[int] = Field(None, ge=0)
    low_stock_threshold: Optional[int] = Field(None, ge=0)
    status: Optional[str] = None
    extra_data: Optional[dict] = None
    images: Optional[List[str]] = None


class ProductResponse(BaseModel):
    """Product response model"""
    id: int
    sku: str
    name: str
    description: Optional[str]
    price: float
    currency: str
    cost: Optional[float]
    category: Optional[str]
    subcategory: Optional[str]
    brand: Optional[str]
    tags: Optional[List[str]]
    stock_quantity: int
    low_stock_threshold: int
    fraud_risk_score: float
    high_risk: bool
    fraud_incidents: int
    chargeback_rate: float
    status: str
    extra_data: Optional[dict]
    images: Optional[List[str]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProductStats(BaseModel):
    """Product statistics model"""
    total_products: int
    by_status: dict
    by_category: dict
    high_risk_count: int
    low_stock_count: int
    total_value: float
    avg_price: float


class FraudRiskUpdate(BaseModel):
    """Fraud risk update model"""
    fraud_risk_score: float = Field(..., ge=0, le=1)
    high_risk: bool
    fraud_incidents: Optional[int] = Field(None, ge=0)
    chargeback_rate: Optional[float] = Field(None, ge=0, le=1)


# ============================================================================
# Product Endpoints
# ============================================================================

@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_data: ProductCreate,
    current_user: User = Depends(require_analyst),
    db: Session = Depends(get_db)
):
    """
    Create a new product
    
    Add a new product to the system.
    Requires analyst or admin role.
    
    - **sku**: Unique product SKU
    - **name**: Product name
    - **price**: Product price
    - **description**: Product description
    - **category**: Product category
    - **stock_quantity**: Available stock
    """
    # Check if SKU already exists
    existing_product = db.query(Product).filter(Product.sku == product_data.sku).first()
    if existing_product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product with this SKU already exists"
        )
    
    # Create product
    db_product = Product(
        sku=product_data.sku,
        name=product_data.name,
        description=product_data.description,
        price=product_data.price,
        currency=product_data.currency,
        cost=product_data.cost,
        category=product_data.category,
        subcategory=product_data.subcategory,
        brand=product_data.brand,
        tags=product_data.tags,
        stock_quantity=product_data.stock_quantity,
        low_stock_threshold=product_data.low_stock_threshold,
        extra_data=product_data.extra_data,
        images=product_data.images
    )
    
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    
    return db_product


@router.get("/", response_model=List[ProductResponse])
async def get_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    category: Optional[str] = None,
    brand: Optional[str] = None,
    status: Optional[str] = None,
    high_risk: Optional[bool] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get products
    
    Retrieve products with filtering options.
    
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return (1-1000)
    - **category**: Filter by category
    - **brand**: Filter by brand
    - **status**: Filter by status (active, inactive, suspended)
    - **high_risk**: Filter by fraud risk (true/false)
    - **search**: Search in name, SKU, or description
    """
    query = db.query(Product)
    
    # Apply filters
    if category:
        query = query.filter(Product.category == category)
    
    if brand:
        query = query.filter(Product.brand == brand)
    
    if status:
        try:
            status_enum = ProductStatus(status.lower())
            query = query.filter(Product.status == status_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Must be one of: {[s.value for s in ProductStatus]}"
            )
    
    if high_risk is not None:
        query = query.filter(Product.high_risk == high_risk)
    
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                Product.name.ilike(search_pattern),
                Product.sku.ilike(search_pattern),
                Product.description.ilike(search_pattern)
            )
        )
    
    # Order by most recent first
    query = query.order_by(desc(Product.created_at))
    
    # Apply pagination
    products = query.offset(skip).limit(limit).all()
    
    return products


@router.get("/high-risk", response_model=List[ProductResponse])
async def get_high_risk_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(require_analyst),
    db: Session = Depends(get_db)
):
    """
    Get high-risk products
    
    Retrieve products flagged as high fraud risk.
    Requires analyst or admin role.
    """
    products = (
        db.query(Product)
        .filter(Product.high_risk == True)
        .order_by(desc(Product.fraud_risk_score))
        .offset(skip)
        .limit(limit)
        .all()
    )
    
    return products


@router.get("/low-stock", response_model=List[ProductResponse])
async def get_low_stock_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get low stock products
    
    Retrieve products with stock below threshold.
    """
    products = (
        db.query(Product)
        .filter(Product.stock_quantity <= Product.low_stock_threshold)
        .order_by(Product.stock_quantity)
        .offset(skip)
        .limit(limit)
        .all()
    )
    
    return products


@router.get("/stats", response_model=ProductStats)
async def get_product_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get product statistics
    
    Get aggregated statistics for all products.
    """
    products = db.query(Product).all()
    
    total_products = len(products)
    
    # Count by status
    by_status = {}
    for status in ProductStatus:
        count = sum(1 for product in products if product.status == status)
        by_status[status.value] = count
    
    # Count by category
    by_category = {}
    for product in products:
        if product.category:
            by_category[product.category] = by_category.get(product.category, 0) + 1
    
    # Count high risk products
    high_risk_count = sum(1 for product in products if product.high_risk)
    
    # Count low stock products
    low_stock_count = sum(
        1 for product in products
        if product.stock_quantity <= product.low_stock_threshold
    )
    
    # Calculate total value and average price
    active_products = [p for p in products if p.status == ProductStatus.ACTIVE]
    total_value = sum(p.price * p.stock_quantity for p in active_products)
    avg_price = sum(p.price for p in active_products) / len(active_products) if active_products else 0.0
    
    return ProductStats(
        total_products=total_products,
        by_status=by_status,
        by_category=by_category,
        high_risk_count=high_risk_count,
        low_stock_count=low_stock_count,
        total_value=total_value,
        avg_price=avg_price
    )


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get product by ID
    
    Retrieve a specific product by its ID.
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    return product


@router.get("/sku/{sku}", response_model=ProductResponse)
async def get_product_by_sku(
    sku: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get product by SKU
    
    Retrieve a specific product by its SKU.
    """
    product = db.query(Product).filter(Product.sku == sku).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    return product


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product_data: ProductUpdate,
    current_user: User = Depends(require_analyst),
    db: Session = Depends(get_db)
):
    """
    Update product
    
    Update product information.
    Requires analyst or admin role.
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Update fields
    update_data = product_data.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        if field == "status" and value is not None:
            try:
                status_enum = ProductStatus(value.lower())
                setattr(product, field, status_enum)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid status. Must be one of: {[s.value for s in ProductStatus]}"
                )
        else:
            setattr(product, field, value)
    
    product.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(product)
    
    return product


@router.put("/{product_id}/fraud-risk", response_model=ProductResponse)
async def update_product_fraud_risk(
    product_id: int,
    risk_data: FraudRiskUpdate,
    current_user: User = Depends(require_analyst),
    db: Session = Depends(get_db)
):
    """
    Update product fraud risk
    
    Update fraud risk indicators for a product.
    Requires analyst or admin role.
    
    - **fraud_risk_score**: Risk score (0-1)
    - **high_risk**: High risk flag
    - **fraud_incidents**: Number of fraud incidents
    - **chargeback_rate**: Chargeback rate (0-1)
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Update fraud risk fields
    product.fraud_risk_score = risk_data.fraud_risk_score
    product.high_risk = risk_data.high_risk
    
    if risk_data.fraud_incidents is not None:
        product.fraud_incidents = risk_data.fraud_incidents
    
    if risk_data.chargeback_rate is not None:
        product.chargeback_rate = risk_data.chargeback_rate
    
    product.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(product)
    
    return product


@router.delete("/{product_id}")
async def delete_product(
    product_id: int,
    current_user: User = Depends(require_analyst),
    db: Session = Depends(get_db)
):
    """
    Delete product
    
    Soft delete a product by setting status to deleted.
    Requires analyst or admin role.
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Soft delete
    product.status = ProductStatus.DELETED
    product.updated_at = datetime.utcnow()
    db.commit()
    
    return {
        "message": "Product deleted successfully",
        "product_id": product_id
    }


@router.post("/{product_id}/stock")
async def update_stock(
    product_id: int,
    quantity: int,
    current_user: User = Depends(require_analyst),
    db: Session = Depends(get_db)
):
    """
    Update product stock
    
    Update stock quantity for a product.
    Requires analyst or admin role.
    
    - **quantity**: New stock quantity
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    if quantity < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Stock quantity cannot be negative"
        )
    
    old_quantity = product.stock_quantity
    product.stock_quantity = quantity
    product.updated_at = datetime.utcnow()
    db.commit()
    
    return {
        "message": "Stock updated successfully",
        "product_id": product_id,
        "old_quantity": old_quantity,
        "new_quantity": quantity
    }

