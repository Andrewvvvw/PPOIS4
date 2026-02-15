from utils.validator import validate_name


class InventoryItem:
    def __init__(self, name: str, description: str, amount: int) -> None:
        self.set_name(name)
        self.set_description(description)
        self.set_amount(amount)

    def get_name(self) -> str:
        return self._name

    def get_description(self) -> str:
        return self._description

    def get_amount(self) -> int:
        return self._amount

    def set_name(self, name: str) -> None:
        validate_name(name)
        self._name = name

    def set_description(self, description: str) -> None:
        self._description = description

    def set_amount(self, amount: int) -> None:
        if amount < 0:
            raise ValueError("Amount cannot be negative")
        self._amount = amount

    def reduce_amount(self, amount: int) -> None:
        if amount <= 0:
            raise ValueError("Amount must be positive")
        self._amount -= amount
