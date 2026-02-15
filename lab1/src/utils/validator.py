from exceptions.exceptions import IncorrectAgeError, IncorrectNameError


def validate_age(age: int) -> None:
    if not isinstance(age, int):
        raise TypeError("Age must be an integer")
    if not (0 <= age <= 120):
        raise IncorrectAgeError("Age must be between 0 and 120")


def validate_name(name: str) -> None:
    if not isinstance(name, str):
        raise TypeError("Name must be a string")
    if not name.strip():
        raise IncorrectNameError("Name cannot be empty")
