import uuid
from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, Enum, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..auth.models import User
from ..models import Base
from ..products.models import Product, TimestampMixin
import enum

class OrderStatusEnum(enum.Enum):
    PENDING = 'pending'
    SHIPPED = 'shipped'
    COMPLETED = 'completed'
    CANCELED = 'canceled'


class Order(Base, TimestampMixin):
    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    status: Mapped[OrderStatusEnum] = mapped_column(
        Enum(OrderStatusEnum),
        nullable=False,
        default=OrderStatusEnum.PENDING
    )
    total_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('user.id', ondelete="CASCADE"),
        nullable=False
    )

    user: Mapped["User"] = relationship("User", back_populates="orders")
    items: Mapped[list["OrderItem"]] = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")



class OrderItem(Base):
    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    order_id: Mapped[int] = mapped_column(ForeignKey('order.id', ondelete="CASCADE"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey('product.id', ondelete="CASCADE"), nullable=False)
    quantity: Mapped[int] = mapped_column(nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)  # copy product price at the time of order

    order: Mapped["Order"] = relationship("Order", back_populates="items")
    product: Mapped["Product"] = relationship("Product", back_populates="order_items")