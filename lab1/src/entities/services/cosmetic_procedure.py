from entities.management.client import Client
from entities.management.master import Master
from entities.services.service import Service
from entities.inventory.cosmetics import Cosmetics
from utils.masters_specialization import MastersSpecialization


class CosmeticProcedure(Service):
    def __init__(
            self,
            name: str,
            price: float,
            cosmetics: list[Cosmetics]
    ) -> None:
        super().__init__(name, price)
        self._required_cosmetics = cosmetics

    def get_cosmetics(self) -> list[Cosmetics]:
        return self._required_cosmetics.copy()

    def set_cosmetics(self, cosmetics: list[Cosmetics]) -> None:
        self._required_cosmetics = cosmetics

    def perform(self, client: Client) -> None:
        client.set_cosmetic_status(False)

    def can_perform_by(self, master: Master) -> bool:
        return master.get_specialization() == MastersSpecialization.COSMETICS
