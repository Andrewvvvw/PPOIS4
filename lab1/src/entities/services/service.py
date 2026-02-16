from src.entities.inventory.inventory_item import InventoryItem
from src.entities.management.client import Client
from src.entities.management.master import Master
from src.utils.validator import validate_name
from abc import ABC, abstractmethod


class Service(ABC):
    def __init__(self, name: str, price: float) -> None:
        self.set_name(name)
        self.set_price(price)

    def get_name(self) -> str:
        return self._name

    def set_name(self, name: str) -> None:
        validate_name(name)
        self._name: str = name

    def get_price(self) -> float:
        return self._price

    def set_price(self, price: float) -> None:
        if price < 0:
            raise ValueError("Service price cannot be negative")
        self._price: float = price

    @abstractmethod
    def perform(self, client: Client) -> None:
        pass

    @abstractmethod
    def can_perform_by(self, master: Master) -> bool:
        pass

    @abstractmethod
    def get_equipment(self) -> list[InventoryItem]:
        pass
