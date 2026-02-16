from src.entities.inventory.cosmetics import Cosmetics
from src.entities.management.master import Master
from src.entities.management.reception import Reception
from src.entities.inventory.inventory_item import InventoryItem
from src.entities.services.service import Service
from src.entities.management.client import Client
from src.entities.management.booking import Booking
from src.exceptions.exceptions import (
    StaffError,
    ServiceError,
    MasterSpecializationError,
    BookingStatusError,
    InventoryItemError,
    ItemNotForSaleError,
    ItemAmountError
)
from src.utils.booking_status import BookingStatus


class Salon:

    def __init__(self, name: str) -> None:
        self.__name: str = name
        self.__staff: list[Master] = []
        self.__reception: Reception = Reception()
        self.__inventory: list[InventoryItem] = []
        self.__services: list[Service] = []

    def get_name(self) -> str:
        return self.__name

    def get_staff(self) -> list[Master]:
        return self.__staff.copy()

    def hire_staff(self, master: Master) -> None:
        if master in self.__staff:
            raise StaffError(f"Master {master.get_name()} already hired")
        self.__staff.append(master)

    def fire_staff(self, master: Master) -> None:
        if master in self.__staff:
            self.__staff.remove(master)
        else:
            raise StaffError(f"Master {master.get_name()} is not in staff")

    def add_service(self, service: Service) -> None:
        self.__services.append(service)

    def remove_service(self, target: Service) -> None:
        if target in self.__services:
            self.__services.remove(target)
        else:
            raise ServiceError(f"Target {target.get_name()} not found")

    def get_services(self) -> list[Service]:
        return self.__services.copy()

    def get_reception(self) -> Reception:
        return self.__reception

    def get_inventory(self) -> list[InventoryItem]:
        return self.__inventory.copy()

    def add_to_inventory(self, item: InventoryItem) -> None:
        self.__inventory.append(item)

    def check_balance(self) -> float:
        return self.__reception.get_balance()

    def get_bookings(self) -> list[Booking]:
        return self.__reception.get_bookings()

    def _check_resources_for_service(self, service: Service) -> bool:
        for equipment in service.get_equipment():
            inventory_item = self.find_product(equipment.get_name())
            if not inventory_item or inventory_item.get_amount() <= 0:
                raise InventoryItemError(
                    f"There's no '{equipment.get_name()}' "
                    "in salon inventory"
                )
        return True

    @staticmethod
    def _check_master_specialization(
            master: Master,
            service: Service
    ) -> bool:
        return service.can_perform_by(master)

    def make_booking(
            self,
            client: Client,
            master: Master,
            service: Service,
    ) -> Booking:
        """
        Операция записи на услугу.
        Связывает сущности и делегирует сохранение ресепшену.
        """
        if master not in self.__staff:
            raise StaffError(
                f"Master {master.get_name()} doesn't work here"
            )

        if service not in self.__services:
            raise ServiceError(
                f"Service {service.get_name()} isn't available"
            )

        self._check_resources_for_service(service)

        if not self._check_master_specialization(master, service):
            raise MasterSpecializationError(
                f"Master {master.get_name()} can't do this service"
            )

        new_booking = Booking(
            client=client,
            service=service,
            master=master,
            status=BookingStatus.CONFIRMED
        )

        self.__reception.add_booking(new_booking)
        return new_booking

    def get_all_bookings(self) -> list[Booking]:
        """
        Возвращает список всех бронирований в салоне.
        """
        return self.__reception.get_bookings()

    def complete_booking(self, booking: Booking) -> None:
        """
        Операция проведения косметических процедур/стрижки и укладки
        :param booking: Booking
        :return: None
        """
        if booking.get_status() == BookingStatus.DONE:
            raise BookingStatusError("Booking is already completed")

        service = booking.get_service()
        service.perform(booking.get_client())

        self.__reception.process_payment(service.get_price())
        booking.set_status(BookingStatus.DONE)

    def find_product(self, product_name: str) -> InventoryItem | None:
        for product in self.__inventory:
            if product.get_name() == product_name:
                return product
        return None

    def sell_product(self, product_name: str, quantity: int) -> None:
        """
        Операция продажи косметических средств.
        """
        product = self.find_product(product_name)
        if product is None:
            raise InventoryItemError(
                f"Product {product_name} isn't available in our salon"
            )

        if not isinstance(product, Cosmetics):
            raise ItemNotForSaleError(
                f"Product {product_name} isn't for sale"
            )

        if quantity <= 0:
            raise ValueError(f"Quantity of product must be positive")

        if product.get_amount() < quantity:
            raise ItemAmountError(f"Not enough product {product_name}. Sorry")

        product.reduce_amount(quantity)

        total_price = quantity * product.get_price()
        self.__reception.process_payment(total_price)

        print(f"Sold {product.get_name()} with {quantity} item(s)")

    def find_service_by_name(self, service_name: str) -> Service | None:
        for service in self.__services:
            if service.get_name() == service_name:
                return service
        return None
