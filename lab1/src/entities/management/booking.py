from entities.management.client import Client
from entities.services.service import Service
from utils.booking_status import BookingStatus
from entities.management.master import Master


class Booking:

    def __init__(
            self,
            client: Client,
            service: Service,
            master: Master,
            status: BookingStatus,
    ) -> None:
        self.set_client(client)
        self.set_service(service)
        self.set_master(master)
        self.set_status(status)

    def get_client(self) -> Client:
        return self.__client

    def get_service(self) -> Service:
        return self.__service

    def get_master(self) -> Master:
        return self.__master

    def get_status(self) -> BookingStatus:
        return self.__status

    def set_master(self, master: Master) -> None:
        self.__master = master

    def set_status(self, status: BookingStatus) -> None:
        self.__status = status

    def set_client(self, client: Client) -> None:
        self.__client = client

    def set_service(self, service: Service) -> None:
        self.__service = service

    def __str__(self) -> str:
        return (
            f"Booking for {self.__client.get_name()}:\n"
            f"{self.__service.get_name()} "
            f"by master {self.__master.get_name()}\n"
            f"Status: {self.get_status().value}"
        )

    def __repr__(self) -> str:
        return (
            f"Booking(client='{self.__client.get_name()}', "
            f"service='{self.__service.get_name()}', "
            f"master='{self.__master.get_name()}', "
            f"status='{self.get_status().value}')"
        )
