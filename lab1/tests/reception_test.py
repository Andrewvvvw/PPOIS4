import pytest
from src.entities.management.reception import Reception
from src.entities.management.booking import Booking
from src.entities.management.client import Client
from src.entities.management.master import Master
from src.entities.services.hair_service import HairService
from src.entities.inventory.hairdressing_equipment import HairdressingEquipment
from src.utils.booking_status import BookingStatus
from src.utils.masters_specialization import MastersSpecialization


class TestReception:
    def test_init_default_values(self) -> None:
        reception = Reception()
        assert reception.get_balance() == 0.0
        assert reception.get_bookings() == []

    def test_get_bookings_empty(self) -> None:
        reception = Reception()
        bookings = reception.get_bookings()
        assert bookings == []
        assert isinstance(bookings, list)

    def test_get_bookings_returns_copy(self) -> None:
        reception = Reception()
        client = Client("John Doe", 25)
        master = Master("Jane Smith", 30, MastersSpecialization.HAIR_CUTTING)
        equipment = [
            HairdressingEquipment("Scissors", "Professional scissors", 2)
        ]
        service = HairService("Haircut", 50.0, equipment)
        booking = Booking(client, service, master, BookingStatus.CONFIRMED)

        reception.add_booking(booking)
        bookings1 = reception.get_bookings()
        bookings2 = reception.get_bookings()

        assert bookings1 is not bookings2
        assert bookings1 == bookings2

    def test_get_balance_initial(self) -> None:
        reception = Reception()
        assert reception.get_balance() == 0.0

    def test_set_balance_valid(self) -> None:
        reception = Reception()
        reception.set_balance(100.0)
        assert reception.get_balance() == 100.0

    def test_set_balance_zero(self) -> None:
        reception = Reception()
        reception.set_balance(0.0)
        assert reception.get_balance() == 0.0

    def test_set_balance_negative(self) -> None:
        reception = Reception()
        reception.set_balance(-50.0)
        assert reception.get_balance() == -50.0

    def test_add_booking_valid(self) -> None:
        reception = Reception()
        client = Client("John Doe", 25)
        master = Master("Jane Smith", 30, MastersSpecialization.HAIR_CUTTING)
        equipment = [
            HairdressingEquipment("Scissors", "Professional scissors", 2)
        ]
        service = HairService("Haircut", 50.0, equipment)
        booking = Booking(client, service, master, BookingStatus.CONFIRMED)

        reception.add_booking(booking)
        bookings = reception.get_bookings()

        assert len(bookings) == 1
        assert bookings[0] == booking

    def test_add_booking_invalid_type(self) -> None:
        reception = Reception()

        with pytest.raises(TypeError) as exc_info:
            reception.add_booking("not a booking")
        assert "Expected a Booking instance" in str(exc_info.value)

        with pytest.raises(TypeError) as exc_info:
            reception.add_booking(123)
        assert "Expected a Booking instance" in str(exc_info.value)

        with pytest.raises(TypeError) as exc_info:
            reception.add_booking(None)
        assert "Expected a Booking instance" in str(exc_info.value)

    def test_add_booking_multiple(self) -> None:
        reception = Reception()
        client1 = Client("John Doe", 25)
        client2 = Client("Alice Smith", 30)
        master = Master("Jane Smith", 30, MastersSpecialization.HAIR_CUTTING)
        equipment = [
            HairdressingEquipment("Scissors", "Professional scissors", 2)
        ]
        service1 = HairService("Haircut", 50.0, equipment)
        service2 = HairService("Styling", 75.0, equipment)
        booking1 = Booking(client1, service1, master, BookingStatus.CONFIRMED)
        booking2 = Booking(client2, service2, master, BookingStatus.CONFIRMED)

        reception.add_booking(booking1)
        reception.add_booking(booking2)

        bookings = reception.get_bookings()
        assert len(bookings) == 2
        assert booking1 in bookings
        assert booking2 in bookings

    def test_add_bookings_empty_list(self) -> None:
        reception = Reception()
        reception.add_bookings([])
        assert reception.get_bookings() == []

    def test_add_bookings_single_item(self) -> None:
        reception = Reception()
        client = Client("John Doe", 25)
        master = Master("Jane Smith", 30, MastersSpecialization.HAIR_CUTTING)
        equipment = [
            HairdressingEquipment("Scissors", "Professional scissors", 2)
        ]
        service = HairService("Haircut", 50.0, equipment)
        booking = Booking(client, service, master, BookingStatus.CONFIRMED)

        reception.add_bookings([booking])

        bookings = reception.get_bookings()
        assert len(bookings) == 1
        assert bookings[0] == booking

    def test_add_bookings_multiple_items(self) -> None:
        reception = Reception()
        client1 = Client("John Doe", 25)
        client2 = Client("Alice Smith", 30)
        master = Master("Jane Smith", 30, MastersSpecialization.HAIR_CUTTING)
        equipment = [
            HairdressingEquipment("Scissors", "Professional scissors", 2)
        ]
        service1 = HairService("Haircut", 50.0, equipment)
        service2 = HairService("Styling", 75.0, equipment)
        booking1 = Booking(client1, service1, master, BookingStatus.CONFIRMED)
        booking2 = Booking(client2, service2, master, BookingStatus.CONFIRMED)

        reception.add_bookings([booking1, booking2])

        bookings = reception.get_bookings()
        assert len(bookings) == 2
        assert booking1 in bookings
        assert booking2 in bookings

    def test_add_bookings_with_invalid_item(self) -> None:
        reception = Reception()
        client = Client("John Doe", 25)
        master = Master("Jane Smith", 30, MastersSpecialization.HAIR_CUTTING)
        equipment = [
            HairdressingEquipment("Scissors", "Professional scissors", 2)
        ]
        service = HairService("Haircut", 50.0, equipment)
        booking = Booking(client, service, master, BookingStatus.CONFIRMED)

        with pytest.raises(TypeError) as exc_info:
            reception.add_bookings([booking, "invalid"])
        assert "Expected a Booking instance" in str(exc_info.value)

    def test_clear_bookings_empty(self) -> None:
        reception = Reception()
        reception.clear_bookings()
        assert reception.get_bookings() == []

    def test_clear_bookings_with_data(self) -> None:
        reception = Reception()
        client = Client("John Doe", 25)
        master = Master("Jane Smith", 30, MastersSpecialization.HAIR_CUTTING)
        equipment = [
            HairdressingEquipment("Scissors", "Professional scissors", 2)
        ]
        service = HairService("Haircut", 50.0, equipment)
        booking = Booking(client, service, master, BookingStatus.CONFIRMED)

        reception.add_booking(booking)
        assert len(reception.get_bookings()) == 1

        reception.clear_bookings()
        assert reception.get_bookings() == []

    def test_process_payment_valid(self) -> None:
        reception = Reception()
        reception.process_payment(50.0)
        assert reception.get_balance() == 50.0

    def test_process_payment_multiple_times(self) -> None:
        reception = Reception()
        reception.process_payment(25.0)
        reception.process_payment(75.0)
        assert reception.get_balance() == 100.0

    def test_process_payment_zero_amount(self) -> None:
        reception = Reception()

        with pytest.raises(ValueError) as exc_info:
            reception.process_payment(0.0)
        assert "Amount to deposit must be positive" in str(exc_info.value)

    def test_process_payment_negative_amount(self) -> None:
        reception = Reception()

        with pytest.raises(ValueError) as exc_info:
            reception.process_payment(-10.0)
        assert "Amount to deposit must be positive" in str(exc_info.value)

    def test_process_payment_small_amount(self) -> None:
        reception = Reception()
        reception.process_payment(0.01)
        assert reception.get_balance() == 0.01

    def test_process_payment_large_amount(self) -> None:
        reception = Reception()
        reception.process_payment(999999.99)
        assert reception.get_balance() == 999999.99

    def test_full_workflow(self) -> None:
        reception = Reception()
        client1 = Client("John Doe", 25)
        client2 = Client("Alice Smith", 30)
        master = Master("Jane Smith", 30, MastersSpecialization.HAIR_CUTTING)
        equipment = [
            HairdressingEquipment("Scissors", "Professional scissors", 2)
        ]
        service1 = HairService("Haircut", 50.0, equipment)
        service2 = HairService("Styling", 75.0, equipment)
        booking1 = Booking(client1, service1, master, BookingStatus.CONFIRMED)
        booking2 = Booking(client2, service2, master, BookingStatus.CONFIRMED)

        reception.add_bookings([booking1, booking2])
        assert len(reception.get_bookings()) == 2

        reception.process_payment(50.0)
        assert reception.get_balance() == 50.0

        reception.process_payment(75.0)
        assert reception.get_balance() == 125.0

        reception.clear_bookings()
        assert reception.get_bookings() == []
        assert reception.get_balance() == 125.0

    def test_balance_operations_independent(self) -> None:
        reception = Reception()

        reception.set_balance(100.0)
        assert reception.get_balance() == 100.0

        reception.process_payment(50.0)
        assert reception.get_balance() == 150.0

        reception.set_balance(0.0)
        assert reception.get_balance() == 0.0

    def test_booking_list_isolation(self) -> None:
        reception = Reception()
        client = Client("John Doe", 25)
        master = Master("Jane Smith", 30, MastersSpecialization.HAIR_CUTTING)
        equipment = [
            HairdressingEquipment("Scissors", "Professional scissors", 2)
        ]
        service = HairService("Haircut", 50.0, equipment)
        booking = Booking(client, service, master, BookingStatus.CONFIRMED)

        reception.add_booking(booking)
        bookings1 = reception.get_bookings()

        bookings1.append("invalid")
        bookings2 = reception.get_bookings()

        assert len(bookings2) == 1
        assert "invalid" not in bookings2