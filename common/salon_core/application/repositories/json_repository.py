from pathlib import Path

from salon_core.application.repositories.base import SalonRepository
from salon_core.entities.salon import Salon
from salon_core.utils.data_manager import SalonDataManager


class JsonSalonRepository(SalonRepository):
    def __init__(
        self,
        file_path: str,
        default_salon_name: str = "New Salon",
    ) -> None:
        self._path = Path(file_path)
        self._default_salon_name = default_salon_name
        self._data_manager = SalonDataManager(str(self._path))

    def load(self) -> Salon:
        if not self._path.exists():
            return Salon(self._default_salon_name)
        return self._data_manager.load()

    def save(self, salon: Salon) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._data_manager.save(salon)
