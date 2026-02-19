from src.utils.validator import validate_name, validate_age
from typing import Self


class Client:
    def __init__(self, name: str, age: int) -> None:
        self.set_name(name)
        self.set_age(age)

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

    def to_dict(self) -> dict:
        return {
            "name": self.get_name(),
            "age": self.get_age()
        }

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        return cls(name=data["name"], age=data["age"])
