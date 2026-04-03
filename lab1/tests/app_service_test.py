from pathlib import Path
from uuid import uuid4

import pytest

from salon_core.application.errors import AppServiceError
from salon_core.application.repositories.json_repository import JsonSalonRepository
from salon_core.application.service import SalonAppService
from salon_core.entities.inventory.cosmetics import Cosmetics
from salon_core.entities.inventory.hairdressing_equipment import HairdressingEquipment
from salon_core.entities.services.cosmetic_procedure import CosmeticProcedure
from salon_core.entities.services.hair_service import HairService
from salon_core.utils.booking_status import BookingStatus


def _build_service(data_path: Path) -> SalonAppService:
    repository = JsonSalonRepository(
        file_path=str(data_path),
        default_salon_name="Test Salon",
    )
    return SalonAppService(repository)


def _new_temp_data_path() -> Path:
    temp_dir = Path(__file__).resolve().parent / ".tmp"
    temp_dir.mkdir(exist_ok=True)
    return temp_dir / f"salon_{uuid4().hex}.json"


def test_staff_inventory_and_sales_flow() -> None:
    data_path = _new_temp_data_path()
    app_service = _build_service(data_path)

    try:
        app_service.hire_master("Kate", 30, "Cosmetics master")
        app_service.restock_or_create_item(
            name="Serum",
            category="cosmetics",
            description="Hydrating",
            initial_amount=5,
            price=20.0,
        )
        app_service.sell_product("Serum", 2)

        inventory = app_service.list_inventory()
        serum = next(item for item in inventory if item.get_name() == "Serum")

        assert len(app_service.list_staff()) == 1
        assert serum.get_amount() == 3
        assert app_service.get_balance() == 40.0
    finally:
        if data_path.exists():
            data_path.unlink()


def test_create_and_execute_booking_flow() -> None:
    data_path = _new_temp_data_path()
    app_service = _build_service(data_path)

    try:
        app_service.hire_master("John", 25, "Hair cutting master")
        app_service.restock_or_create_item(
            name="Scissors",
            category="equipment",
            description="For haircut",
            initial_amount=3,
        )
        app_service.add_service(
            name="Haircut",
            price=30.0,
            service_type="hair",
            resource_indexes=[0],
        )

        app_service.create_booking("Client A", 20, 0, 0)
        assert len(app_service.list_confirmed_bookings()) == 1

        app_service.execute_booking(0)

        history = app_service.get_booking_history()
        assert len(history) == 1
        assert history[0].get_status() == BookingStatus.DONE
        assert app_service.get_balance() == 30.0
    finally:
        if data_path.exists():
            data_path.unlink()


def test_cancel_booking_flow() -> None:
    data_path = _new_temp_data_path()
    app_service = _build_service(data_path)

    try:
        app_service.hire_master("Jane", 27, "Cosmetics master")
        app_service.restock_or_create_item(
            name="Mask",
            category="cosmetics",
            description="Face mask",
            initial_amount=4,
            price=10.0,
        )
        app_service.add_service(
            name="Facial",
            price=35.0,
            service_type="cosmetic",
            resource_indexes=[0],
        )

        app_service.create_booking("Client B", 22, 0, 0)
        app_service.cancel_booking(0)

        history = app_service.get_booking_history()
        assert len(history) == 1
        assert history[0].get_status() == BookingStatus.CANCELLED
    finally:
        if data_path.exists():
            data_path.unlink()


def test_errors_are_wrapped_with_app_service_error() -> None:
    data_path = _new_temp_data_path()
    app_service = _build_service(data_path)

    try:
        with pytest.raises(AppServiceError):
            app_service.sell_product("Unknown", 1)
    finally:
        if data_path.exists():
            data_path.unlink()


def test_hair_service_rejects_cosmetics_resources() -> None:
    wrong_resource = Cosmetics("Serum", 10.0, "Hydrating", 3)

    with pytest.raises(TypeError):
        HairService("Haircut", 20.0, [wrong_resource])  # type: ignore[list-item]


def test_cosmetic_procedure_rejects_equipment_resources() -> None:
    wrong_resource = HairdressingEquipment("Scissors", "Steel", 2)

    with pytest.raises(TypeError):
        CosmeticProcedure("Facial", 25.0, [wrong_resource])  # type: ignore[list-item]
