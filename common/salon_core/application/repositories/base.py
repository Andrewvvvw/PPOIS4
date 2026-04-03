from abc import ABC, abstractmethod

from salon_core.entities.salon import Salon


class SalonRepository(ABC):
    @abstractmethod
    def load(self) -> Salon:
        pass

    @abstractmethod
    def save(self, salon: Salon) -> None:
        pass
