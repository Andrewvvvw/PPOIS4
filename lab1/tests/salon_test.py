import pytest
from src.entities.salon import Salon
from src.entities.management.master import Master
from src.entities.management.client import Client
from src.entities.inventory.cosmetics import Cosmetics
from src.entities.inventory.hairdressing_equipment import HairdressingEquipment
from src.entities.services.hair_service import HairService
from src.exceptions.exceptions import (
    StaffError,
    ServiceError,
    InventoryItemError,
    ItemNotForSaleError,
    ItemAmountError
)
from src.utils.booking_status import BookingStatus
from src.utils.masters_specialization import MastersSpecialization


class TestSalon:
    def test_init_default_values(self) -> None:
        salon = Salon("Beauty Salon")
        assert salon.get_name() == "Beauty Salon"
        assert salon.get_staff() == []
        assert salon.get_services() == []
        assert salon.get_inventory() == []
        assert salon.check_balance() == 0.0

    def test_get_name(self) -> None:
        salon = Salon("Test Salon")
        assert salon.get_name() == "Test Salon"

    def test_get_staff_empty(self) -> None:
        salon = Salon("Test Salon")
        assert salon.get_staff() == []

    def test_get_staff_with_data(self) -> None:
        salon = Salon("Test Salon")
        master = Master("John Doe", 30, MastersSpecialization.HAIR_CUTTING)
        salon.hire_staff(master)

        staff = salon.get_staff()
        assert len(staff) == 1
        assert staff[0] == master
        assert staff is not salon.get_staff()

    def test_get_services_empty(self) -> None:
        salon = Salon("Test Salon")
        assert salon.get_services() == []

    def test_get_services_with_data(self) -> None:
        salon = Salon("Test Salon")
        equipment = [
            HairdressingEquipment("Scissors", "Professional scissors", 2)
        ]
        service = HairService("Haircut", 50.0, equipment)
        salon.add_service(service)

        services = salon.get_services()
        assert len(services) == 1
        assert services[0] == service
        assert services is not salon.get_services()

    def test_get_inventory_empty(self) -> None:
        salon = Salon("Test Salon")
        assert salon.get_inventory() == []

    def test_get_inventory_with_data(self) -> None:
        salon = Salon("Test Salon")
        item = Cosmetics("Cream", 10.0, "Face cream", 5)
        salon.add_to_inventory(item)

        inventory = salon.get_inventory()
        assert len(inventory) == 1
        assert inventory[0] == item
        assert inventory is not salon.get_inventory()

    def test_get_reception(self) -> None:
        salon = Salon("Test Salon")
        reception = salon.get_reception()
        assert reception is not None
        assert salon.check_balance() == 0.0

    def test_check_balance(self) -> None:
        salon = Salon("Test Salon")
        assert salon.check_balance() == 0.0

        salon.get_reception().process_payment(100.0)
        assert salon.check_balance() == 100.0

    def test_hire_staff_valid(self) -> None:
        salon = Salon("Test Salon")
        master = Master("John Doe", 30, MastersSpecialization.HAIR_CUTTING)

        salon.hire_staff(master)
        staff = salon.get_staff()
        assert len(staff) == 1
        assert staff[0] == master

    def test_hire_staff_already_hired(self) -> None:
        salon = Salon("Test Salon")
        master = Master("John Doe", 30, MastersSpecialization.HAIR_CUTTING)
        salon.hire_staff(master)

        with pytest.raises(StaffError) as exc_info:
            salon.hire_staff(master)
        assert "already hired" in str(exc_info.value)

    def test_hire_staff_multiple(self) -> None:
        salon = Salon("Test Salon")
        master1 = Master("John Doe", 30, MastersSpecialization.HAIR_CUTTING)
        master2 = Master("Jane Smith", 25, MastersSpecialization.COSMETICS)

        salon.hire_staff(master1)
        salon.hire_staff(master2)

        staff = salon.get_staff()
        assert len(staff) == 2
        assert master1 in staff
        assert master2 in staff

    def test_fire_staff_valid(self) -> None:
        salon = Salon("Test Salon")
        master = Master("John Doe", 30, MastersSpecialization.HAIR_CUTTING)
        salon.hire_staff(master)

        salon.fire_staff(master)
        assert len(salon.get_staff()) == 0

    def test_fire_staff_not_hired(self) -> None:
        salon = Salon("Test Salon")
        master = Master("John Doe", 30, MastersSpecialization.HAIR_CUTTING)

        with pytest.raises(StaffError) as exc_info:
            salon.fire_staff(master)
        assert "is not in staff" in str(exc_info.value)

    def test_fire_staff_multiple(self) -> None:
        salon = Salon("Test Salon")
        master1 = Master("John Doe", 30, MastersSpecialization.HAIR_CUTTING)
        master2 = Master("Jane Smith", 25, MastersSpecialization.COSMETICS)

        salon.hire_staff(master1)
        salon.hire_staff(master2)

        salon.fire_staff(master1)
        staff = salon.get_staff()
        assert len(staff) == 1
        assert master2 in staff
        assert master1 not in staff

    def test_add_service_valid(self) -> None:
        salon = Salon("Test Salon")
        equipment = [
            HairdressingEquipment("Scissors", "Professional scissors", 2)
        ]
        service = HairService("Haircut", 50.0, equipment)

        salon.add_service(service)
        services = salon.get_services()
        assert len(services) == 1
        assert services[0] == service

    def test_add_service_multiple(self) -> None:
        salon = Salon("Test Salon")
        equipment1 = [
            HairdressingEquipment("Scissors", "Professional scissors", 2)
        ]
        equipment2 = [HairdressingEquipment("Comb", "Professional comb", 1)]
        service1 = HairService("Haircut", 50.0, equipment1)
        service2 = HairService("Styling", 75.0, equipment2)

        salon.add_service(service1)
        salon.add_service(service2)

        services = salon.get_services()
        assert len(services) == 2
        assert service1 in services
        assert service2 in services

    def test_remove_service_valid(self) -> None:
        salon = Salon("Test Salon")
        equipment = [
            HairdressingEquipment("Scissors", "Professional scissors", 2)
        ]
        service = HairService("Haircut", 50.0, equipment)
        salon.add_service(service)

        salon.remove_service(service)
        assert len(salon.get_services()) == 0

    def test_remove_service_not_found(self) -> None:
        salon = Salon("Test Salon")
        equipment = [
            HairdressingEquipment("Scissors", "Professional scissors", 2)
        ]
        service = HairService("Haircut", 50.0, equipment)

        with pytest.raises(ServiceError) as exc_info:
            salon.remove_service(service)
        assert "not found" in str(exc_info.value)

    def test_add_to_inventory_valid(self) -> None:
        salon = Salon("Test Salon")
        item = Cosmetics("Cream", 10.0, "Face cream", 5)

        salon.add_to_inventory(item)
        inventory = salon.get_inventory()
        assert len(inventory) == 1
        assert inventory[0] == item

    def test_add_to_inventory_multiple(self) -> None:
        salon = Salon("Test Salon")
        item1 = Cosmetics("Cream", 10.0, "Face cream", 5)
        item2 = HairdressingEquipment("Scissors", "Professional scissors", 2)

        salon.add_to_inventory(item1)
        salon.add_to_inventory(item2)

        inventory = salon.get_inventory()
        assert len(inventory) == 2
        assert item1 in inventory
        assert item2 in inventory

    def test_get_bookings_empty(self) -> None:
        salon = Salon("Test Salon")
        assert salon.get_bookings() == []

    def test_find_product_found(self) -> None:
        salon = Salon("Test Salon")
        item = Cosmetics("Cream", 10.0, "Face cream", 5)
        salon.add_to_inventory(item)

        found = salon.find_product("Cream")
        assert found == item

    def test_find_product_not_found(self) -> None:
        salon = Salon("Test Salon")

        found = salon.find_product("Nonexistent")
        assert found is None

    def test_find_service_by_name_found(self) -> None:
        salon = Salon("Test Salon")
        equipment = [
            HairdressingEquipment("Scissors", "Professional scissors", 2)
        ]
        service = HairService("Haircut", 50.0, equipment)
        salon.add_service(service)

        found = salon.find_service_by_name("Haircut")
        assert found == service

    def test_find_service_by_name_not_found(self) -> None:
        salon = Salon("Test Salon")

        found = salon.find_service_by_name("Nonexistent")
        assert found is None

    def test_make_booking_master_not_hired(self) -> None:
        salon = Salon("Test Salon")
        client = Client("John Doe", 25)
        master = Master("Jane Smith", 30, MastersSpecialization.HAIR_CUTTING)
        equipment = [
            HairdressingEquipment("Scissors", "Professional scissors", 2)
        ]
        service = HairService("Haircut", 50.0, equipment)
        salon.add_service(service)

        with pytest.raises(StaffError) as exc_info:
            salon.make_booking(client, master, service)
        assert "doesn't work here" in str(exc_info.value)

    def test_make_booking_service_not_available(self) -> None:
        salon = Salon("Test Salon")
        client = Client("John Doe", 25)
        master = Master("Jane Smith", 30, MastersSpecialization.HAIR_CUTTING)
        equipment = [
            HairdressingEquipment("Scissors", "Professional scissors", 2)
        ]
        service = HairService("Haircut", 50.0, equipment)
        salon.hire_staff(master)

        with pytest.raises(ServiceError) as exc_info:
            salon.make_booking(client, master, service)
        assert "isn't available" in str(exc_info.value)

    def test_make_booking_insufficient_resources(self) -> None:
        salon = Salon("Test Salon")
        client = Client("John Doe", 25)
        master = Master("Jane Smith", 30, MastersSpecialization.HAIR_CUTTING)
        equipment = [
            HairdressingEquipment("Scissors", "Professional scissors", 2)
        ]
        service = HairService("Haircut", 50.0, equipment)
        salon.hire_staff(master)
        salon.add_service(service)

        with pytest.raises(InventoryItemError) as exc_info:
            salon.make_booking(client, master, service)
        assert "no 'Scissors' in salon inventory" in str(exc_info.value)

    def test_sell_product_valid(self) -> None:
        salon = Salon("Test Salon")
        item = Cosmetics("Cream", 10.0, "Face cream", 5)
        salon.add_to_inventory(item)

        initial_balance = salon.check_balance()
        salon.sell_product("Cream", 2)

        assert item.get_amount() == 3
        assert salon.check_balance() == initial_balance + 20.0

    def test_sell_product_not_found(self) -> None:
        salon = Salon("Test Salon")

        with pytest.raises(InventoryItemError) as exc_info:
            salon.sell_product("Nonexistent", 1)
        assert "isn't available" in str(exc_info.value)

    def test_sell_product_not_cosmetics(self) -> None:
        salon = Salon("Test Salon")
        item = HairdressingEquipment("Scissors", "Professional scissors", 2)
        salon.add_to_inventory(item)

        with pytest.raises(ItemNotForSaleError) as exc_info:
            salon.sell_product("Scissors", 1)
        assert "isn't for sale" in str(exc_info.value)

    def test_sell_product_negative_quantity(self) -> None:
        salon = Salon("Test Salon")
        item = Cosmetics("Cream", 10.0, "Face cream", 5)
        salon.add_to_inventory(item)

        with pytest.raises(ValueError) as exc_info:
            salon.sell_product("Cream", -1)
        assert "must be positive" in str(exc_info.value)

    def test_sell_product_zero_quantity(self) -> None:
        salon = Salon("Test Salon")
        item = Cosmetics("Cream", 10.0, "Face cream", 5)
        salon.add_to_inventory(item)

        with pytest.raises(ValueError) as exc_info:
            salon.sell_product("Cream", 0)
        assert "must be positive" in str(exc_info.value)

    def test_sell_product_insufficient_stock(self) -> None:
        salon = Salon("Test Salon")
        item = Cosmetics("Cream", 10.0, "Face cream", 2)
        salon.add_to_inventory(item)

        with pytest.raises(ItemAmountError) as exc_info:
            salon.sell_product("Cream", 5)
        assert "Not enough product" in str(exc_info.value)

    def test_check_master_specialization_valid(self) -> None:
        salon = Salon("Test Salon")
        master = Master("Jane Smith", 30, MastersSpecialization.HAIR_CUTTING)
        equipment = [
            HairdressingEquipment("Scissors", "Professional scissors", 2)
        ]
        service = HairService("Haircut", 50.0, equipment)

        result = salon._check_master_specialization(master, service)
        assert result is True

    def test_check_master_specialization_invalid(self) -> None:
        salon = Salon("Test Salon")
        master = Master("Jane Smith", 30, MastersSpecialization.COSMETICS)
        equipment = [
            HairdressingEquipment("Scissors", "Professional scissors", 2)
        ]
        service = HairService("Haircut", 50.0, equipment)

        result = salon._check_master_specialization(master, service)
        assert result is False

    def test_full_workflow(self) -> None:
        salon = Salon("Beauty Salon")

        master = Master("Jane Smith", 30, MastersSpecialization.HAIR_CUTTING)
        salon.hire_staff(master)

        item = HairdressingEquipment("Scissors", "Professional scissors", 2)
        salon.add_to_inventory(item)

        equipment = [
            HairdressingEquipment("Scissors", "Professional scissors", 2)
        ]
        service = HairService("Haircut", 50.0, equipment)
        salon.add_service(service)

        client = Client("John Doe", 25)
        booking = salon.make_booking(client, master, service)

        assert len(salon.get_staff()) == 1
        assert len(salon.get_inventory()) == 1
        assert len(salon.get_services()) == 1
        assert len(salon.get_bookings()) == 1

        salon.complete_booking(booking)

        assert booking.get_status() == BookingStatus.DONE
        assert salon.check_balance() == 50.0