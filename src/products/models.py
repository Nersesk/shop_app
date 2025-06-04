from decimal import Decimal
from typing import Optional

from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum, UniqueConstraint, Numeric
from sqlalchemy.orm import relationship, Mapped, mapped_column, Relationship
from datetime import datetime
from ..models import Base
import enum
class GenderEnum(str, enum.Enum):
    MAN = "man"
    WOMAN = "woman"
    UNISEX = "unisex"

class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(default=datetime.now())
    updated_at: Mapped[datetime] = mapped_column(default=datetime.now(),
                                                 onupdate=datetime.now())

class Category(Base):
    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    name: Mapped[str] = mapped_column(unique=True)
    image: Mapped[Optional[str]] = mapped_column(String(500))

    products: Mapped[list["Product"]] = relationship('Product', back_populates='category')

class ProductImage(Base):
    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    image_url: Mapped[str] = mapped_column(nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("product.id", ondelete="CASCADE"))


class Product(Base, TimestampMixin):
    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(1000))
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    category_id: Mapped[int| None] = mapped_column(ForeignKey('category.id', ondelete="SET NULL"),
                                             )

    gender: Mapped[GenderEnum] = mapped_column(Enum(GenderEnum), nullable=False, default=GenderEnum.UNISEX)
    category: Mapped["Category"] = relationship('Category', back_populates='products')
    specifications: Mapped[list["ProductSpecification"]] = relationship("ProductSpecification", back_populates="product")
    images: Mapped[list["ProductImage"]] = relationship("ProductImage", backref="product")



class ProductSpecification(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("product.id", ondelete="CASCADE"))
    key: Mapped[str] = mapped_column(String(255), nullable=False)
    value: Mapped[str] = mapped_column(String(255), nullable=False)

    product: Mapped["Product"] = relationship("Product", back_populates="specifications")

