from src.entities.inventory.inventory_item import InventoryItem
from src.exceptions.exceptions import PriceError
from typing import Self

class Cosmetics(InventoryItem):
    def __init__(
            self,
            name: str,
            price: float,
            description: str,
            amount: int
    ) -> None:
        super().__init__(name, description, amount)
        self.set_price(price)

    def get_price(self) -> float:
        return self._price

    def set_price(self, price: float) -> None:
        if price <= 0:
            raise PriceError("Price must be a positive number")
        self._price = price

    def to_dict(self) -> dict:
        return {
            "type": "Cosmetics",
            "name": self.get_name(),
            "desc": self.get_description(),
            "amount": self.get_amount(),
            "price": self.get_price()
        }

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        return cls(
            name=data["name"],
            price=data["price"],
            description=data["desc"],
            amount=data["amount"]
        )
