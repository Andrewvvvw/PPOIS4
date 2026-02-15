from entities.inventory.hairdressing_equipment import HairdressingEquipment
from entities.management.client import Client
from entities.management.master import Master
from entities.services.service import Service
from exceptions.exceptions import BrokenEquipmentError
from utils.equipment_condition import EquipmentCondition
from utils.masters_specialization import MastersSpecialization


class HairService(Service):
    def __init__(
            self,
            name: str,
            price: float,
            hairstyle: str,
            required_equipment: list[HairdressingEquipment]
    ) -> None:
        super().__init__(name, price)
        self.set_required_equipment(required_equipment)
        self.__hairstyle = hairstyle

    def set_required_equipment(
            self,
            hairdressing_equipment: list[HairdressingEquipment]
    ) -> None:
        self.__required_equipment: list[HairdressingEquipment] = (
            hairdressing_equipment
        )

    def get_required_equipment(self) -> list[HairdressingEquipment]:
        return self.__required_equipment

    def add_equipment_item(self, equipment: HairdressingEquipment) -> None:
        self.__required_equipment.append(equipment)

    def add_equipment(self, equipment: list[HairdressingEquipment]) -> None:
        for tool in equipment:
            self.add_equipment_item(tool)

    def perform(self, client: Client) -> None:
        for tool in self.__required_equipment:
            if tool.get_condition() == EquipmentCondition.BROKEN:
                raise BrokenEquipmentError(
                    f"{tool.get_name()} is broken. Cannot perform service."
                )

        client.set_hair_service_status(False)

        for tool in self.__required_equipment:
            tool.degrade()

    def can_perform_by(self, master: Master) -> bool:
        return master.get_specialization() in (
            MastersSpecialization.HAIR_STYLING,
            MastersSpecialization.HAIR_CUTTING
        )
