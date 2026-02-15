from src.utils.validator import validate_name, validate_age


class Client:
    def __init__(self, name: str, age: int) -> None:
        self.set_name(name)
        self.set_age(age)
        self.__needs_cosmetic_procedure = True
        self.__needs_hair_services = True

    def set_name(self, name: str) -> None:
        validate_name(name)
        self.__name = name

    def set_age(self, age: int) -> None:
        validate_age(age)
        self.__age = age

    def get_name(self) -> str:
        return self.__name

    def get_age(self) -> int:
        return self.__age

    def get_cosmetic_status(self) -> bool:
        return self.__needs_cosmetic_procedure

    def get_hair_service_status(self) -> bool:
        return self.__needs_hair_services

    def set_cosmetic_status(self, cosmetic_status: bool) -> None:
        self.__needs_cosmetic_procedure = cosmetic_status

    def set_hair_service_status(self, haircut_status: bool) -> None:
        self.__needs_hair_services = haircut_status
