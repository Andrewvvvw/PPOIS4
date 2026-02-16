from src.entities.management.booking import Booking


class Reception:
    def __init__(self) -> None:
        self.__bookings: list[Booking] = []
        self.__balance: float = 0

    def get_bookings(self) -> list[Booking]:
        return self.__bookings.copy()

    def get_balance(self) -> float:
        return self.__balance

    def set_balance(self, balance: float) -> None:
        self.__balance = balance

    def add_booking(self, booking: Booking) -> None:
        if not isinstance(booking, Booking):
            raise TypeError("Expected a Booking instance")
        self.__bookings.append(booking)

    def add_bookings(self, bookings: list[Booking]) -> None:
        for booking in bookings:
            self.add_booking(booking)

    def clear_bookings(self) -> None:
        self.__bookings = []

    def process_payment(self, amount: float) -> None:
        """
        Операция оплаты услуги/покупки косметики
        :param amount: float
        :return: None
        """
        if amount <= 0:
            raise ValueError('Amount to deposit must be positive')
        self.__balance += amount
