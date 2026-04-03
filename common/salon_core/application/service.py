from typing import Callable

from salon_core.application.errors.base import AppServiceError
from salon_core.application.repositories.base import SalonRepository
from salon_core.entities.inventory.cosmetics import Cosmetics
from salon_core.entities.inventory.hairdressing_equipment import HairdressingEquipment
from salon_core.entities.inventory.inventory_item import InventoryItem
from salon_core.entities.management.booking import Booking
from salon_core.entities.management.client import Client
from salon_core.entities.management.master import Master
from salon_core.entities.salon import Salon
from salon_core.entities.services.cosmetic_procedure import CosmeticProcedure
from salon_core.entities.services.hair_service import HairService
from salon_core.entities.services.service import Service
from salon_core.exceptions.exceptions import (
    BookingStatusError,
    IncorrectAgeError,
    IncorrectNameError,
    InventoryItemError,
    ItemAmountError,
    ItemNotForSaleError,
    MasterSpecializationError,
    PriceError,
    ServiceError,
    StaffError,
)
from salon_core.utils.booking_status import BookingStatus
from salon_core.utils.masters_specialization import MastersSpecialization


class SalonAppService:
    _CONTROLLED_EXCEPTIONS = (
        ValueError,
        TypeError,
        PriceError,
        IncorrectAgeError,
        IncorrectNameError,
        StaffError,
        ServiceError,
        MasterSpecializationError,
        BookingStatusError,
        InventoryItemError,
        ItemNotForSaleError,
        ItemAmountError,
    )

    def __init__(self, repository: SalonRepository) -> None:
        self._repository = repository

    @staticmethod
    def _to_app_error(error: Exception) -> AppServiceError:
        if isinstance(error, AppServiceError):
            return error
        return AppServiceError(str(error))

    def _read(self, action: Callable[[Salon], object]) -> object:
        try:
            salon = self._repository.load()
            return action(salon)
        except self._CONTROLLED_EXCEPTIONS as error:
            raise self._to_app_error(error) from error

    def _mutate(self, action: Callable[[Salon], object]) -> object:
        try:
            salon = self._repository.load()
            result = action(salon)
            self._repository.save(salon)
            return result
        except self._CONTROLLED_EXCEPTIONS as error:
            raise self._to_app_error(error) from error

    @staticmethod
    def _get_by_index(items: list, index: int, label: str):
        if not 0 <= index < len(items):
            raise ValueError(f"Invalid {label} selection.")
        return items[index]

    @staticmethod
    def _parse_specialization(spec) -> MastersSpecialization:
        if isinstance(spec, MastersSpecialization):
            return spec
        if isinstance(spec, str):
            if spec in MastersSpecialization.__members__:
                return MastersSpecialization[spec]
            return MastersSpecialization(spec)
        raise TypeError("Invalid specialization value")

    @staticmethod
    def _parse_category(category: str) -> str:
        normalized = category.strip().lower()
        if normalized in {"1", "cosmetics", "cosmetic"}:
            return "cosmetics"
        if normalized in {"2", "equipment", "hairdressing_equipment"}:
            return "equipment"
        raise ValueError("Invalid category selected.")

    @staticmethod
    def _parse_service_type(service_type: str) -> str:
        normalized = service_type.strip().lower()
        if normalized in {"1", "hair", "hairservice", "hair_service"}:
            return "hair"
        if normalized in {
            "2",
            "cosmetic",
            "cosmeticprocedure",
            "cosmetic_procedure",
        }:
            return "cosmetic"
        raise ValueError("Invalid service type.")

    @staticmethod
    def _pick_by_indexes(items: list, indexes: list[int]) -> list:
        selected = []
        for index in indexes:
            if 0 <= index < len(items):
                selected.append(items[index])
        return selected

    def get_salon_name(self) -> str:
        return self._read(lambda salon: salon.get_name())

    def list_staff(self) -> list[Master]:
        return self._read(lambda salon: salon.get_staff())

    def hire_master(self, name: str, age: int, specialization) -> None:
        parsed_spec = self._parse_specialization(specialization)

        def action(salon: Salon) -> None:
            salon.hire_staff(Master(name, age, parsed_spec))

        self._mutate(action)

    def fire_master(self, staff_index: int) -> None:
        def action(salon: Salon) -> None:
            staff = salon.get_staff()
            target = self._get_by_index(staff, staff_index, "staff member")
            salon.fire_staff(target)

        self._mutate(action)

    def list_inventory(self) -> list[InventoryItem]:
        return self._read(lambda salon: salon.get_inventory())

    def sell_product(self, product_name: str, quantity: int) -> None:
        self._mutate(lambda salon: salon.sell_product(product_name, quantity))

    def restock_or_create_item(
        self,
        name: str,
        refill_amount: int | None = None,
        category: str | None = None,
        description: str | None = None,
        initial_amount: int | None = None,
        price: float | None = None,
    ) -> None:
        def action(salon: Salon) -> None:
            existing_item = salon.find_product(name)
            if existing_item is not None:
                if refill_amount is None:
                    raise ValueError("Refill amount is required for restock")
                existing_item.set_amount(existing_item.get_amount() + refill_amount)
                return

            if category is None:
                raise ValueError("Category is required for creating new item")

            parsed_category = self._parse_category(category)
            if initial_amount is None:
                raise ValueError("Initial amount is required for new item")

            desc = description or ""
            if parsed_category == "cosmetics":
                if price is None:
                    raise ValueError("Price is required for cosmetics")
                salon.add_to_inventory(Cosmetics(name, price, desc, initial_amount))
            else:
                salon.add_to_inventory(HairdressingEquipment(name, desc, initial_amount))

        self._mutate(action)

    def list_services(self) -> list[Service]:
        return self._read(lambda salon: salon.get_services())

    def add_service(
        self,
        name: str,
        price: float,
        service_type: str,
        resource_indexes: list[int],
    ) -> None:
        parsed_service_type = self._parse_service_type(service_type)

        def action(salon: Salon) -> None:
            inventory = salon.get_inventory()
            if parsed_service_type == "hair":
                equipment = [
                    item for item in inventory if isinstance(item, HairdressingEquipment)
                ]
                selected = self._pick_by_indexes(equipment, resource_indexes)
                service = HairService(name, price, selected)
            else:
                cosmetics = [
                    item for item in inventory if isinstance(item, Cosmetics)
                ]
                selected = self._pick_by_indexes(cosmetics, resource_indexes)
                service = CosmeticProcedure(name, price, selected)
            salon.add_service(service)

        self._mutate(action)

    def remove_service(self, service_index: int) -> None:
        def action(salon: Salon) -> None:
            services = salon.get_services()
            target = self._get_by_index(services, service_index, "service")
            salon.remove_service(target)

        self._mutate(action)

    def list_bookings(self) -> list[Booking]:
        return self._read(lambda salon: salon.get_all_bookings())

    def list_confirmed_bookings(self) -> list[Booking]:
        return self._read(
            lambda salon: [
                booking
                for booking in salon.get_bookings()
                if booking.get_status() == BookingStatus.CONFIRMED
            ]
        )

    def create_booking(
        self,
        client_name: str,
        client_age: int,
        master_index: int,
        service_index: int,
    ) -> None:
        def action(salon: Salon) -> None:
            staff = salon.get_staff()
            master = self._get_by_index(staff, master_index, "master")

            services = salon.get_services()
            service = self._get_by_index(services, service_index, "service")

            client = Client(client_name, client_age)
            salon.make_booking(client, master, service)

        self._mutate(action)

    def execute_booking(self, confirmed_booking_index: int) -> None:
        def action(salon: Salon) -> None:
            confirmed_bookings = [
                booking
                for booking in salon.get_bookings()
                if booking.get_status() == BookingStatus.CONFIRMED
            ]
            target = self._get_by_index(
                confirmed_bookings,
                confirmed_booking_index,
                "booking",
            )
            salon.complete_booking(target)

        self._mutate(action)

    def cancel_booking(self, confirmed_booking_index: int) -> None:
        def action(salon: Salon) -> None:
            confirmed_bookings = [
                booking
                for booking in salon.get_all_bookings()
                if booking.get_status() == BookingStatus.CONFIRMED
            ]
            target = self._get_by_index(
                confirmed_bookings,
                confirmed_booking_index,
                "booking",
            )
            target.set_status(BookingStatus.CANCELLED)

        self._mutate(action)

    def get_balance(self) -> float:
        return self._read(lambda salon: salon.check_balance())

    def get_booking_history(self) -> list[Booking]:
        return self._read(
            lambda salon: [
                booking
                for booking in salon.get_all_bookings()
                if booking.get_status() in (BookingStatus.DONE, BookingStatus.CANCELLED)
            ]
        )

    def get_dashboard_stats(self) -> dict:
        def action(salon: Salon) -> dict:
            all_bookings = salon.get_all_bookings()
            confirmed = [
                booking
                for booking in all_bookings
                if booking.get_status() == BookingStatus.CONFIRMED
            ]
            done = [
                booking
                for booking in all_bookings
                if booking.get_status() == BookingStatus.DONE
            ]
            cancelled = [
                booking
                for booking in all_bookings
                if booking.get_status() == BookingStatus.CANCELLED
            ]
            return {
                "salon_name": salon.get_name(),
                "balance": salon.check_balance(),
                "staff_count": len(salon.get_staff()),
                "inventory_count": len(salon.get_inventory()),
                "services_count": len(salon.get_services()),
                "bookings_total": len(all_bookings),
                "bookings_confirmed": len(confirmed),
                "bookings_done": len(done),
                "bookings_cancelled": len(cancelled),
            }

        return self._read(action)
