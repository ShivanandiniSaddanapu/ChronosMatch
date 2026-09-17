from dataclasses import dataclass
from enum import Enum
from time import time_ns


class OrderSide(Enum):
    BUY = "BUY"
    SELL = "SELL"


@dataclass(slots=True)
class Order:
    order_id: int
    symbol: str
    side: OrderSide
    price: float
    quantity: int
    timestamp: int

    def __post_init__(self):
        if self.price <= 0:
            raise ValueError("Price must be greater than zero")

        if self.quantity <= 0:
            raise ValueError("Quantity must be greater than zero")

    @classmethod
    def create(
        cls,
        order_id: int,
        symbol: str,
        side: OrderSide,
        price: float,
        quantity: int,
    ) -> "Order":
        return cls(
            order_id=order_id,
            symbol=symbol,
            side=side,
            price=price,
            quantity=quantity,
            timestamp=time_ns(),
        )