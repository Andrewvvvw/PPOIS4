from entities.inventory.inventory_item import InventoryItem
from src.exceptions.exceptions import PriceError


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
