from src.entities.inventory.hairdressing_equipment import HairdressingEquipment
from src.entities.management.master import Master
from src.entities.services.service import Service
from src.utils.masters_specialization import MastersSpecialization


class HairService(Service):
    def __init__(
            self,
            name: str,
            price: float,
            required_equipment: list[HairdressingEquipment]
    ) -> None:
        super().__init__(name, price)
        self.set_required_equipment(required_equipment)

    def set_required_equipment(
            self,
            hairdressing_equipment: list[HairdressingEquipment]
    ) -> None:
        self.__required_equipment: list[HairdressingEquipment] = (
            hairdressing_equipment
        )

    def get_equipment(self) -> list[HairdressingEquipment]:
        return self.__required_equipment.copy()

    def add_equipment_item(self, equipment: HairdressingEquipment) -> None:
        self.__required_equipment.append(equipment)

    def add_equipment(self, equipment: list[HairdressingEquipment]) -> None:
        for tool in equipment:
            self.add_equipment_item(tool)

    def perform(self) -> None:
        for equipment in self.__required_equipment:
            equipment.use_equipment()

    def can_perform_by(self, master: Master) -> bool:
        return master.get_specialization() in (
            MastersSpecialization.HAIR_STYLING,
            MastersSpecialization.HAIR_CUTTING
        )

    def to_dict(self) -> dict:
        return {
            "type": "HairService",
            "name": self.get_name(),
            "price": self.get_price(),
            "resource_names": [r.get_name() for r in self.get_equipment()]
        }

    @classmethod
    def from_dict(cls, data: dict, resources: list) -> 'HairService':
        return cls(
            name=data["name"],
            price=data["price"],
            required_equipment=resources
        )
