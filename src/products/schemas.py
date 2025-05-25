# schemas.py
from typing import Optional, List
from decimal import Decimal
from datetime import datetime
from enum import Enum

from fastapi import Form
from pydantic import BaseModel, ConfigDict, Field

class GenderEnum(str, Enum):
    man = "man"
    woman = "woman"
    unisex = "unisex"

# ---------- Category ----------
class CategoryBase(BaseModel):
    name: str
    image: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryRead(CategoryBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# ---------- Product Image ----------
class ProductImageBase(BaseModel):
    image_url: str

class ProductImageCreate(ProductImageBase):
    pass

class ProductImageRead(ProductImageBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# ---------- Product Specification ----------
class ProductSpecificationCreate(BaseModel):
    key: str
    value: str


class ProductSpecificationBase(ProductSpecificationCreate):
    key: str
    value: str
    product_id: int


class ProductSpecificationRead(ProductSpecificationBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# ---------- Product ----------
class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: Decimal
    gender: GenderEnum = GenderEnum.unisex
    category_id: Optional[int] = None

class ProductCreateForm:
    def __init__(
        self,
        name: str = Form(...),
        description: str = Form(...),
        price: float = Form(...),
        gender: GenderEnum = Form(...),
        specifications: Optional[str] = Form(None),
        category_id: int = Form(...),
    ):
        self.name = name
        self.description = description
        self.price = price
        self.gender = gender
        self.specifications = specifications
        self.category_id = category_id


class ProductRead(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime
    specifications: List[ProductSpecificationRead] = Field(default_factory=list)
    images: List[ProductImageRead] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)

class ProductFilter(BaseModel):
    category_id: Optional[int] = None
    gender: Optional[GenderEnum] = None
    min_price: Optional[float] = Field(None, ge=0)  # Minimum price, must be >= 0
    max_price: Optional[float] = Field(None, ge=0)  # Maximum price, must be >= 0
    search: Optional[str] = None
    offset: Optional[int] = Field(default=0, ge=0)
    limit: Optional[int] = Field(default=20, ge=1, le=100)

    model_config = ConfigDict(from_attributes=True)
