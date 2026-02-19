from src.entities.inventory.inventory_item import InventoryItem
from src.entities.management.master import Master
from src.entities.services.service import Service
from src.entities.inventory.cosmetics import Cosmetics
from src.utils.masters_specialization import MastersSpecialization
from typing import Self


class CosmeticProcedure(Service):
    def __init__(
            self,
            name: str,
            price: float,
            cosmetics: list[Cosmetics]
    ) -> None:
        super().__init__(name, price)
        self._required_cosmetics = cosmetics

    def get_equipment(self) -> list[Cosmetics]:
        return self._required_cosmetics.copy()

    def set_cosmetics(self, cosmetics: list[Cosmetics]) -> None:
        self._required_cosmetics = cosmetics

    def perform(self, inventory: list[InventoryItem]) -> None:
        for cosmetic in self._required_cosmetics:
            real_cosmetic = next(
                (
                    item for item in inventory
                    if item.get_name() == cosmetic.get_name()
                ),
                None
            )
            if real_cosmetic:
                real_cosmetic.reduce_amount(1)

    def can_perform_by(self, master: Master) -> bool:
        return master.get_specialization() == MastersSpecialization.COSMETICS

    def to_dict(self) -> dict:
        return {
            "type": "CosmeticProcedure",
            "name": self.get_name(),
            "price": self.get_price(),
            "resource_names": [r.get_name() for r in self.get_equipment()]
        }

    @classmethod
    def from_dict(cls, data: dict, resources: list) -> Self:
        return cls(
            name=data["name"],
            price=data["price"],
            cosmetics=resources
        )
