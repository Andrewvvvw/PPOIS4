from entities.inventory.inventory_item import InventoryItem
from utils.equipment_condition import EquipmentCondition


class HairdressingEquipment(InventoryItem):
    def __init__(self, name: str, description: str, amount: int) -> None:
        super().__init__(name, description, amount)
        self._condition: EquipmentCondition = EquipmentCondition.NEW

    def get_condition(self) -> EquipmentCondition:
        return self._condition

    def set_condition(self, condition: EquipmentCondition) -> None:
        if not isinstance(condition, EquipmentCondition):
            raise TypeError(
                "Condition must be of type EquipmentCondition"
            )
        self._condition = condition

    def is_useful(self) -> bool:
        return not self._condition == EquipmentCondition.BROKEN

    def repair(self) -> None:
        self.set_condition(EquipmentCondition.NEW)

    def needs_repair(self) -> bool:
        return self._condition == EquipmentCondition.BROKEN

    def degrade(self) -> None:
        if self._condition == EquipmentCondition.NEW:
            self.set_condition(EquipmentCondition.OK)
        elif self._condition == EquipmentCondition.OK:
            self.set_condition(EquipmentCondition.BROKEN)
            print(f"Equipment {self._name} is broken now")
