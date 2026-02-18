import pytest
from src.entities.management.client import Client
from src.exceptions.exceptions import IncorrectNameError, IncorrectAgeError


class TestClient:
    def test_init_valid_parameters(self) -> None:
        client = Client("John Doe", 25)
        assert client.get_name() == "John Doe"
        assert client.get_age() == 25

    def test_init_with_different_valid_parameters(self) -> None:
        client = Client("Alice Smith", 30)
        assert client.get_name() == "Alice Smith"
        assert client.get_age() == 30

    def test_get_name(self) -> None:
        client = Client("John Doe", 25)
        assert client.get_name() == "John Doe"

    def test_get_age(self) -> None:
        client = Client("John Doe", 25)
        assert client.get_age() == 25

    def test_set_name_valid(self) -> None:
        client = Client("John Doe", 25)
        client.set_name("Jane Smith")
        assert client.get_name() == "Jane Smith"

    def test_set_name_empty(self) -> None:
        client = Client("John Doe", 25)
        with pytest.raises(IncorrectNameError) as exc_info:
            client.set_name("")
        assert "Name cannot be empty" in str(exc_info.value)

    def test_set_name_whitespace(self) -> None:
        client = Client("John Doe", 25)
        with pytest.raises(IncorrectNameError) as exc_info:
            client.set_name("   ")
        assert "Name cannot be empty" in str(exc_info.value)

    def test_set_name_non_string(self) -> None:
        client = Client("John Doe", 25)
        with pytest.raises(TypeError) as exc_info:
            client.set_name(123)
        assert "Name must be a string" in str(exc_info.value)

    def test_set_age_valid(self) -> None:
        client = Client("John Doe", 25)
        client.set_age(30)
        assert client.get_age() == 30

    def test_set_age_negative(self) -> None:
        client = Client("John Doe", 25)
        with pytest.raises(IncorrectAgeError) as exc_info:
            client.set_age(-5)
        assert "Age must be between 0 and 120" in str(exc_info.value)

    def test_set_age_too_young(self) -> None:
        client = Client("John Doe", 25)
        with pytest.raises(IncorrectAgeError) as exc_info:
            client.set_age(-1)
        assert "Age must be between 0 and 120" in str(exc_info.value)

    def test_set_age_too_old(self) -> None:
        client = Client("John Doe", 25)
        with pytest.raises(IncorrectAgeError) as exc_info:
            client.set_age(121)
        assert "Age must be between 0 and 120" in str(exc_info.value)

    def test_set_age_non_integer(self) -> None:
        client = Client("John Doe", 25)
        with pytest.raises(TypeError) as exc_info:
            client.set_age(25.5)
        assert "Age must be an integer" in str(exc_info.value)

    def test_set_age_boundary_min(self) -> None:
        client = Client("John Doe", 25)
        client.set_age(0)
        assert client.get_age() == 0

    def test_set_age_boundary_max(self) -> None:
        client = Client("John Doe", 25)
        client.set_age(120)
        assert client.get_age() == 120

    def test_to_dict(self) -> None:
        client = Client("John Doe", 25)
        result = client.to_dict()
        expected = {"name": "John Doe", "age": 25}
        assert result == expected

    def test_to_dict_different_client(self) -> None:
        client = Client("Alice Smith", 30)
        result = client.to_dict()
        expected = {"name": "Alice Smith", "age": 30}
        assert result == expected

    def test_from_dict(self) -> None:
        data = {"name": "John Doe", "age": 25}
        client = Client.from_dict(data)
        assert client.get_name() == "John Doe"
        assert client.get_age() == 25

    def test_from_dict_different_data(self) -> None:
        data = {"name": "Alice Smith", "age": 30}
        client = Client.from_dict(data)
        assert client.get_name() == "Alice Smith"
        assert client.get_age() == 30

    def test_from_dict_missing_name(self) -> None:
        data = {"age": 25}
        with pytest.raises(KeyError):
            Client.from_dict(data)

    def test_from_dict_missing_age(self) -> None:
        data = {"name": "John Doe"}
        with pytest.raises(KeyError):
            Client.from_dict(data)

    def test_from_dict_empty_data(self) -> None:
        data = {}
        with pytest.raises(KeyError):
            Client.from_dict(data)

    def test_multiple_operations(self) -> None:
        client = Client("John Doe", 25)

        client.set_name("Jane Smith")
        client.set_age(30)

        assert client.get_name() == "Jane Smith"
        assert client.get_age() == 30

    def test_edge_case_names(self) -> None:
        client1 = Client("A", 25)
        assert client1.get_name() == "A"

        client2 = Client("Very Long Name With Spaces", 30)
        assert client2.get_name() == "Very Long Name With Spaces"

    def test_edge_case_ages(self) -> None:
        client1 = Client("Baby", 0)
        assert client1.get_age() == 0

        client2 = Client("Senior", 120)
        assert client2.get_age() == 120