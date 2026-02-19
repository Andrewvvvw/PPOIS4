from src.entities.inventory.inventory_item import InventoryItem
import random
from typing import Self

DESTROYING_CHANCE = 0.1

class HairdressingEquipment(InventoryItem):
    def __init__(self, name: str, description: str, amount: int) -> None:
        super().__init__(name, description, amount)

    def use_equipment(self) -> None:
        if random.random() < DESTROYING_CHANCE:
            print(f"Equipment '{self.get_name()}' is destroyed")
            self.reduce_amount(1)

    def to_dict(self) -> dict:
        return {
            "type": "Equipment",
            "name": self.get_name(),
            "desc": self.get_description(),
            "amount": self.get_amount()
        }

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        return cls(
            name=data["name"],
            description=data["desc"],
            amount=data["amount"]
        )