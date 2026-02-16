import pytest
from src.entities.management.booking import Booking
from src.entities.management.client import Client
from src.entities.management.master import Master
from src.entities.services.hair_service import HairService
from src.entities.inventory.hairdressing_equipment import HairdressingEquipment
from src.utils.booking_status import BookingStatus
from src.utils.masters_specialization import MastersSpecialization


class TestBooking:
    def test_init_valid_parameters(self) -> None:
        client = Client("John Doe", 25)
        master = Master("Jane Smith", 30, MastersSpecialization.HAIR_CUTTING)
        equipment = [
            HairdressingEquipment("Scissors", "Professional scissors", 2)
        ]
        service = HairService("Haircut", 50.0, equipment)
        status = BookingStatus.CONFIRMED

        booking = Booking(client, service, master, status)

        assert booking.get_client() == client
        assert booking.get_service() == service
        assert booking.get_master() == master
        assert booking.get_status() == status

    def test_get_client(self) -> None:
        client = Client("John Doe", 25)
        master = Master("Jane Smith", 30, MastersSpecialization.HAIR_CUTTING)
        equipment = [
            HairdressingEquipment("Scissors", "Professional scissors", 2)
        ]
        service = HairService("Haircut", 50.0, equipment)
        booking = Booking(client, service, master, BookingStatus.CONFIRMED)

        assert booking.get_client() == client
        assert booking.get_client().get_name() == "John Doe"
        assert booking.get_client().get_age() == 25

    def test_get_service(self) -> None:
        client = Client("John Doe", 25)
        master = Master("Jane Smith", 30, MastersSpecialization.HAIR_CUTTING)
        equipment = [
            HairdressingEquipment("Scissors", "Professional scissors", 2)
        ]
        service = HairService("Haircut", 50.0, equipment)
        booking = Booking(client, service, master, BookingStatus.CONFIRMED)

        assert booking.get_service() == service
        assert booking.get_service().get_name() == "Haircut"
        assert booking.get_service().get_price() == 50.0

    def test_get_master(self) -> None:
        client = Client("John Doe", 25)
        master = Master("Jane Smith", 30, MastersSpecialization.HAIR_CUTTING)
        equipment = [
            HairdressingEquipment("Scissors", "Professional scissors", 2)
        ]
        service = HairService("Haircut", 50.0, equipment)
        booking = Booking(client, service, master, BookingStatus.CONFIRMED)

        assert booking.get_master() == master
        assert booking.get_master().get_name() == "Jane Smith"
        assert booking.get_master().get_age() == 30
        assert (
                booking.get_master().get_specialization()
                == MastersSpecialization.HAIR_CUTTING
        )

    def test_get_status(self) -> None:
        client = Client("John Doe", 25)
        master = Master("Jane Smith", 30, MastersSpecialization.HAIR_CUTTING)
        equipment = [
            HairdressingEquipment("Scissors", "Professional scissors", 2)
        ]
        service = HairService("Haircut", 50.0, equipment)
        booking = Booking(client, service, master, BookingStatus.DONE)

        assert booking.get_status() == BookingStatus.DONE
        assert booking.get_status().value == "Done"

    def test_set_master(self) -> None:
        client = Client("John Doe", 25)
        master1 = Master("Jane Smith", 30, MastersSpecialization.HAIR_CUTTING)
        master2 = Master("Bob Johnson", 35, MastersSpecialization.COSMETICS)
        equipment = [
            HairdressingEquipment("Scissors", "Professional scissors", 2)
        ]
        service = HairService("Haircut", 50.0, equipment)
        booking = Booking(client, service, master1, BookingStatus.CONFIRMED)

        booking.set_master(master2)
        assert booking.get_master() == master2
        assert booking.get_master().get_name() == "Bob Johnson"

    def test_set_status(self) -> None:
        client = Client("John Doe", 25)
        master = Master("Jane Smith", 30, MastersSpecialization.HAIR_CUTTING)
        equipment = [
            HairdressingEquipment("Scissors", "Professional scissors", 2)
        ]
        service = HairService("Haircut", 50.0, equipment)
        booking = Booking(client, service, master, BookingStatus.CONFIRMED)

        booking.set_status(BookingStatus.CANCELLED)
        assert booking.get_status() == BookingStatus.CANCELLED
        assert booking.get_status().value == "Cancelled"

    def test_set_client(self) -> None:
        client1 = Client("John Doe", 25)
        client2 = Client("Alice Brown", 28)
        master = Master("Jane Smith", 30, MastersSpecialization.HAIR_CUTTING)
        equipment = [
            HairdressingEquipment("Scissors", "Professional scissors", 2)
        ]
        service = HairService("Haircut", 50.0, equipment)
        booking = Booking(client1, service, master, BookingStatus.CONFIRMED)

        booking.set_client(client2)
        assert booking.get_client() == client2
        assert booking.get_client().get_name() == "Alice Brown"

    def test_set_service(self) -> None:
        client = Client("John Doe", 25)
        master = Master("Jane Smith", 30, MastersSpecialization.HAIR_CUTTING)
        equipment1 = [
            HairdressingEquipment("Scissors", "Professional scissors", 2)
        ]
        equipment2 = [HairdressingEquipment("Comb", "Professional comb", 1)]
        service1 = HairService("Haircut", 50.0, equipment1)
        service2 = HairService("Styling", 75.0, equipment2)
        booking = Booking(client, service1, master, BookingStatus.CONFIRMED)

        booking.set_service(service2)
        assert booking.get_service() == service2
        assert booking.get_service().get_name() == "Styling"

    def test_str_method(self) -> None:
        client = Client("John Doe", 25)
        master = Master("Jane Smith", 30, MastersSpecialization.HAIR_CUTTING)
        equipment = [
            HairdressingEquipment("Scissors", "Professional scissors", 2)
        ]
        service = HairService("Haircut", 50.0, equipment)
        booking = Booking(client, service, master, BookingStatus.CONFIRMED)

        expected = (
            "Booking for John Doe:\n"
            "Haircut by master Jane Smith\n"
            "Status: Confirmed"
        )
        assert str(booking) == expected

    def test_str_method_different_status(self) -> None:
        client = Client("Alice", 30)
        master = Master("Bob", 25, MastersSpecialization.COSMETICS)
        equipment = [HairdressingEquipment("Brush", "Professional brush", 1)]
        service = HairService("Facial", 80.0, equipment)
        booking = Booking(client, service, master, BookingStatus.DONE)

        expected = (
            "Booking for Alice:\n"
            "Facial by master Bob\n"
            "Status: Done"
        )
        assert str(booking) == expected

    def test_repr_method(self) -> None:
        client = Client("John Doe", 25)
        master = Master("Jane Smith", 30, MastersSpecialization.HAIR_CUTTING)
        equipment = [
            HairdressingEquipment("Scissors", "Professional scissors", 2)
        ]
        service = HairService("Haircut", 50.0, equipment)
        booking = Booking(client, service, master, BookingStatus.CONFIRMED)

        expected = (
            "Booking(client='John Doe', "
            "service='Haircut', "
            "master='Jane Smith', "
            "status='Confirmed')"
        )
        assert repr(booking) == expected

    def test_booking_with_all_statuses(self) -> None:
        client = Client("John", 25)
        master = Master("Jane", 30, MastersSpecialization.HAIR_CUTTING)
        equipment = [
            HairdressingEquipment("Scissors", "Professional scissors", 2)
        ]
        service = HairService("Service", 50.0, equipment)

        for status in BookingStatus:
            booking = Booking(client, service, master, status)
            assert booking.get_status() == status

    def test_multiple_set_operations(self) -> None:
        client1 = Client("John", 25)
        client2 = Client("Alice", 30)
        master1 = Master("Jane", 30, MastersSpecialization.HAIR_CUTTING)
        master2 = Master("Bob", 25, MastersSpecialization.COSMETICS)
        equipment1 = [
            HairdressingEquipment("Scissors", "Professional scissors", 2)
        ]
        equipment2 = [HairdressingEquipment("Brush", "Professional brush", 1)]
        service1 = HairService("Haircut", 50.0, equipment1)
        service2 = HairService("Facial", 80.0, equipment2)

        booking = Booking(client1, service1, master1, BookingStatus.CONFIRMED)

        booking.set_client(client2)
        booking.set_master(master2)
        booking.set_service(service2)
        booking.set_status(BookingStatus.DONE)

        assert booking.get_client() == client2
        assert booking.get_master() == master2
        assert booking.get_service() == service2
        assert booking.get_status() == BookingStatus.DONE