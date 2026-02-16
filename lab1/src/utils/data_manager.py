import json
import os
from src.entities.salon import Salon
from src.entities.management.master import Master
from src.entities.inventory.cosmetics import Cosmetics
from src.entities.inventory.hairdressing_equipment import HairdressingEquipment
from src.entities.services.hair_service import HairService
from src.entities.services.cosmetic_procedure import CosmeticProcedure
from src.entities.management.booking import Booking


class SalonDataManager:
    def __init__(self, file_path: str = "salon.json") -> None:
        self.__file_path = file_path

    def save(self, salon: Salon) -> None:
        data = {
            "name": salon.get_name(),
            "balance": salon.check_balance(),
            "staff": [m.to_dict() for m in salon.get_staff()],
            "inventory": [i.to_dict() for i in salon.get_inventory()],
            "services": [s.to_dict() for s in salon.get_services()],
            "bookings": [b.to_dict() for b in salon.get_all_bookings()]
        }
        with open(self.__file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def load(self) -> Salon:
        if not os.path.exists(self.__file_path):
            return Salon("New Salon")

        with open(self.__file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        salon = Salon(data["name"])
        salon.get_reception().set_balance(data.get("balance", 0.0))

        for m_data in data.get("staff", []):
            salon.hire_staff(Master.from_dict(m_data))

        for i_data in data.get("inventory", []):
            if i_data["type"] == "Cosmetics":
                salon.add_to_inventory(Cosmetics.from_dict(i_data))
            else:
                salon.add_to_inventory(
                    HairdressingEquipment.from_dict(i_data)
                )

        for s_data in data.get("services", []):
            resources = [
                salon.find_product(n) for n in s_data["resource_names"]
            ]
            resources = [r for r in resources if r]  # filter None

            if s_data["type"] == "HairService":
                salon.add_service(HairService.from_dict(s_data, resources))
            else:
                salon.add_service(
                    CosmeticProcedure.from_dict(s_data, resources)
                )

        for b_data in data.get("bookings", []):
            service = salon.find_service_by_name(b_data["service_name"])

            master = next(
                (
                    m for m in salon.get_staff()
                    if m.get_name() == b_data["master_name"] and
                       m.get_specialization().value == b_data["master_spec"]
                ),
                None
            )

            if master and service:
                salon.get_reception().add_booking(
                    Booking.from_dict(b_data, master, service)
                )

        return salon
