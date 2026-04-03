from pathlib import Path
from uuid import uuid4

from django.test import Client, TestCase, override_settings
from django.urls import reverse

from salon_core.application.repositories.json_repository import JsonSalonRepository
from salon_core.application.service import SalonAppService
from salon_core.entities.inventory.cosmetics import Cosmetics
from salon_core.entities.inventory.hairdressing_equipment import HairdressingEquipment
from salon_core.entities.management.master import Master
from salon_core.entities.salon import Salon
from salon_core.entities.services.cosmetic_procedure import CosmeticProcedure
from salon_core.entities.services.hair_service import HairService
from salon_core.utils.booking_status import BookingStatus
from salon_core.utils.masters_specialization import MastersSpecialization


class SalonWebViewsTestCase(TestCase):
    def setUp(self) -> None:
        local_tmp_dir = Path(__file__).resolve().parent / ".tmp"
        local_tmp_dir.mkdir(exist_ok=True)
        self._data_path = local_tmp_dir / f"salon_test_{uuid4().hex}.json"

        self._settings_override = override_settings(SALON_DATA_PATH=self._data_path)
        self._settings_override.enable()

        self._seed_data()
        self.client = Client()

    def tearDown(self) -> None:
        self._settings_override.disable()
        if self._data_path.exists():
            self._data_path.unlink()

    def _seed_data(self) -> None:
        salon = Salon("BEST SALON")

        master_hair = Master("Alex", 28, MastersSpecialization.HAIR_CUTTING)
        master_cosmetics = Master("Liza", 26, MastersSpecialization.COSMETICS)
        salon.hire_staff(master_hair)
        salon.hire_staff(master_cosmetics)

        serum = Cosmetics("Serum", 20.0, "Hydrating", 10)
        scissors = HairdressingEquipment("Scissors", "Steel", 5)
        salon.add_to_inventory(serum)
        salon.add_to_inventory(scissors)

        hair_service = HairService("Haircut", 15.0, [scissors])
        cosmetic_service = CosmeticProcedure("Facial", 30.0, [serum])
        salon.add_service(hair_service)
        salon.add_service(cosmetic_service)

        repository = JsonSalonRepository(str(self._data_path), default_salon_name="BEST SALON")
        repository.save(salon)

    def _app_service(self) -> SalonAppService:
        repository = JsonSalonRepository(str(self._data_path), default_salon_name="BEST SALON")
        return SalonAppService(repository)

    def test_get_pages(self) -> None:
        for name in [
            "dashboard",
            "staff",
            "inventory",
            "services",
            "bookings",
            "finance",
        ]:
            response = self.client.get(reverse(name))
            assert response.status_code == 200

    def test_post_staff_hire_and_fire(self) -> None:
        hire_response = self.client.post(
            reverse("staff"),
            {
                "action": "hire",
                "name": "New Master",
                "age": 23,
                "specialization": "Hair styling master",
            },
        )
        assert hire_response.status_code == 302
        assert len(self._app_service().list_staff()) == 3

        fire_response = self.client.post(
            reverse("staff"),
            {
                "action": "fire",
                "staff_index": "2",
            },
        )
        assert fire_response.status_code == 302
        assert len(self._app_service().list_staff()) == 2

    def test_post_inventory_operations(self) -> None:
        sell_response = self.client.post(
            reverse("inventory"),
            {
                "action": "sell",
                "name": "Serum",
                "quantity": 2,
            },
        )
        assert sell_response.status_code == 302

        restock_response = self.client.post(
            reverse("inventory"),
            {
                "action": "restock",
                "name": "Serum",
                "refill_amount": 3,
            },
        )
        assert restock_response.status_code == 302

        create_response = self.client.post(
            reverse("inventory"),
            {
                "action": "create",
                "name": "Comb",
                "category": "equipment",
                "description": "For styling",
                "initial_amount": 2,
                "price": "",
            },
        )
        assert create_response.status_code == 302

        app_service = self._app_service()
        inventory = app_service.list_inventory()
        serum = next(item for item in inventory if item.get_name() == "Serum")

        assert serum.get_amount() == 11
        assert app_service.get_balance() == 40.0
        assert any(item.get_name() == "Comb" for item in inventory)

    def test_post_service_operations(self) -> None:
        add_response = self.client.post(
            reverse("services"),
            {
                "action": "add",
                "name": "Quick Cut",
                "price": 18.0,
                "service_type": "hair",
                "equipment_indexes": ["0"],
                "cosmetics_indexes": [],
            },
        )
        assert add_response.status_code == 302

        app_service = self._app_service()
        services = app_service.list_services()
        assert len(services) == 3

        remove_response = self.client.post(
            reverse("services"),
            {
                "action": "remove",
                "service_index": "2",
            },
        )
        assert remove_response.status_code == 302
        assert len(self._app_service().list_services()) == 2

    def test_reject_service_with_wrong_resource_type(self) -> None:
        invalid_add_response = self.client.post(
            reverse("services"),
            {
                "action": "add",
                "name": "Invalid Hair Service",
                "price": 22.0,
                "service_type": "hair",
                "equipment_indexes": [],
                "cosmetics_indexes": ["0"],
            },
        )
        assert invalid_add_response.status_code == 200
        assert len(self._app_service().list_services()) == 2

    def test_post_booking_operations(self) -> None:
        create_response = self.client.post(
            reverse("bookings"),
            {
                "action": "create",
                "client_name": "Client One",
                "client_age": 20,
                "master_index": "0",
                "service_index": "0",
            },
        )
        assert create_response.status_code == 302
        assert len(self._app_service().list_confirmed_bookings()) == 1

        execute_response = self.client.post(
            reverse("bookings"),
            {
                "action": "execute",
                "booking_index": "0",
            },
        )
        assert execute_response.status_code == 302

        create_second_response = self.client.post(
            reverse("bookings"),
            {
                "action": "create",
                "client_name": "Client Two",
                "client_age": 22,
                "master_index": "1",
                "service_index": "1",
            },
        )
        assert create_second_response.status_code == 302

        cancel_response = self.client.post(
            reverse("bookings"),
            {
                "action": "cancel",
                "booking_index": "0",
            },
        )
        assert cancel_response.status_code == 302

        history = self._app_service().get_booking_history()
        statuses = {booking.get_status() for booking in history}
        assert BookingStatus.DONE in statuses
        assert BookingStatus.CANCELLED in statuses
