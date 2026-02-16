from src.utils.masters_specialization import MastersSpecialization
from src.utils.validator import validate_name, validate_age


class Master:

    def __init__(
            self,
            name: str,
            age: int,
            specialization: MastersSpecialization,
    ) -> None:
        self.set_name(name)
        self.set_age(age)
        self.set_specialization(specialization)

    def get_specialization(self) -> MastersSpecialization:
        return self.__specialization

    def get_name(self) -> str:
        return self.__name

    def get_age(self) -> int:
        return self.__age

    def set_specialization(
            self,
            specialization: MastersSpecialization,
    ) -> None:
        if not isinstance(specialization, MastersSpecialization):
            raise TypeError(
                "Specialization must be an instance of MastersSpecialization"
            )
        self.__specialization = specialization

    def set_name(self, name: str) -> None:
        validate_name(name)
        self.__name = name

    def set_age(self, age: int) -> None:
        validate_age(age)
        self.__age = age

    def __repr__(self) -> str:
        return (
            f"Master(name='{self.__name}',"
            f"spec={self.__specialization.name})"
        )

    def __str__(self) -> str:
        return (
            f"Master {self.__name} "
            f"(Specialization: {self.__specialization.value})"
        )

    def to_dict(self) -> dict:
        return {
            "name": self.get_name(),
            "age": self.get_age(),
            "spec": self.get_specialization().value
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Master':
        return cls(
            name=data["name"],
            age=data["age"],
            specialization=MastersSpecialization(data["spec"])
        )
