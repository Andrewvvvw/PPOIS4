import pytest
from unittest.mock import patch
from src.entities.inventory.hairdressing_equipment import HairdressingEquipment, DESTROYING_CHANCE
from src.exceptions.exceptions import IncorrectNameError


class TestHairdressingEquipment:
    def test_init_valid_parameters(self) -> None:
        equipment = HairdressingEquipment(
            "Hairdryer",
            "Professional hairdryer",
            5
        )
        assert equipment.get_name() == "Hairdryer"
        assert equipment.get_description() == "Professional hairdryer"
        assert equipment.get_amount() == 5

    def test_init_invalid_name_empty(self) -> None:
        with pytest.raises(IncorrectNameError) as exc_info:
            HairdressingEquipment("", "Professional hairdryer", 5)
        assert "Name cannot be empty" in str(exc_info.value)

    def test_init_invalid_name_whitespace(self) -> None:
        with pytest.raises(IncorrectNameError) as exc_info:
            HairdressingEquipment("   ", "Professional hairdryer", 5)
        assert "Name cannot be empty" in str(exc_info.value)

    def test_init_invalid_name_non_string(self) -> None:
        with pytest.raises(TypeError) as exc_info:
            HairdressingEquipment(123, "Professional hairdryer", 5)
        assert "Name must be a string" in str(exc_info.value)

    def test_init_invalid_amount_negative(self) -> None:
        with pytest.raises(ValueError) as exc_info:
            HairdressingEquipment("Hairdryer", "Professional hairdryer", -5)
        assert "Amount cannot be negative" in str(exc_info.value)

    def test_destroying_chance_constant(self) -> None:
        assert DESTROYING_CHANCE == 0.1
        assert isinstance(DESTROYING_CHANCE, float)

    @patch('random.random')
    @patch('builtins.print')
    def test_use_equipment_destroyed(self, mock_print, mock_random) -> None:
        mock_random.return_value = 0.05  # Less than DESTROYING_CHANCE
        equipment = HairdressingEquipment(
            "Hairdryer",
            "Professional hairdryer",
            3
        )

        initial_amount = equipment.get_amount()
        equipment.use_equipment()

        assert equipment.get_amount() == initial_amount - 1
        mock_print.assert_called_once_with("Equipment 'Hairdryer' is destroyed")

    @patch('random.random')
    @patch('builtins.print')
    def test_use_equipment_not_destroyed(self, mock_print, mock_random) -> None:
        mock_random.return_value = 0.15  # Greater than DESTROYING_CHANCE
        equipment = HairdressingEquipment(
            "Hairdryer",
            "Professional hairdryer",
            3
        )

        initial_amount = equipment.get_amount()
        equipment.use_equipment()

        assert equipment.get_amount() == initial_amount
        mock_print.assert_not_called()

    def test_to_dict(self) -> None:
        equipment = HairdressingEquipment(
            "Hairdryer",
            "Professional hairdryer",
            3
        )
        result = equipment.to_dict()
        expected = {
            "type": "Equipment",
            "name": "Hairdryer",
            "desc": "Professional hairdryer",
            "amount": 3
        }
        assert result == expected

    def test_from_dict(self) -> None:
        data = {
            "name": "Hairdryer",
            "desc": "Professional hairdryer",
            "amount": 3
        }
        equipment = HairdressingEquipment.from_dict(data)
        assert equipment.get_name() == "Hairdryer"
        assert equipment.get_description() == "Professional hairdryer"
        assert equipment.get_amount() == 3

    def test_from_dict_missing_keys(self) -> None:
        data = {
            "name": "Hairdryer",
            "desc": "Professional hairdryer"
        }
        with pytest.raises(KeyError):
            HairdressingEquipment.from_dict(data)

    def test_inherited_get_amount(self) -> None:
        equipment = HairdressingEquipment(
            "Hairdryer",
            "Professional hairdryer",
            5
        )
        assert equipment.get_amount() == 5

    def test_inherited_set_amount_valid(self) -> None:
        equipment = HairdressingEquipment(
            "Hairdryer",
            "Professional hairdryer",
            5
        )
        equipment.set_amount(10)
        assert equipment.get_amount() == 10

    def test_inherited_set_amount_invalid(self) -> None:
        equipment = HairdressingEquipment(
            "Hairdryer",
            "Professional hairdryer",
            5
        )
        with pytest.raises(ValueError) as exc_info:
            equipment.set_amount(-5)
        assert "Amount cannot be negative" in str(exc_info.value)

    def test_inherited_reduce_amount_valid(self) -> None:
        equipment = HairdressingEquipment(
            "Hairdryer",
            "Professional hairdryer",
            10
        )
        equipment.reduce_amount(3)
        assert equipment.get_amount() == 7

    def test_inherited_reduce_amount_invalid_zero(self) -> None:
        equipment = HairdressingEquipment(
            "Hairdryer",
            "Professional hairdryer",
            10
        )
        with pytest.raises(ValueError) as exc_info:
            equipment.reduce_amount(0)
        assert "Amount must be positive" in str(exc_info.value)

    def test_inherited_reduce_amount_invalid_negative(self) -> None:
        equipment = HairdressingEquipment(
            "Hairdryer",
            "Professional hairdryer",
            10
        )
        with pytest.raises(ValueError) as exc_info:
            equipment.reduce_amount(-3)
        assert "Amount must be positive" in str(exc_info.value)

    def test_inherited_get_name(self) -> None:
        equipment = HairdressingEquipment(
            "Hairdryer",
            "Professional hairdryer",
            10
        )
        assert equipment.get_name() == "Hairdryer"

    def test_inherited_get_description(self) -> None:
        equipment = HairdressingEquipment(
            "Hairdryer",
            "Professional hairdryer",
            10
        )
        assert equipment.get_description() == "Professional hairdryer"

    def test_inherited_set_name_valid(self) -> None:
        equipment = HairdressingEquipment(
            "Hairdryer",
            "Professional hairdryer",
            10
        )
        equipment.set_name("New Hairdryer")
        assert equipment.get_name() == "New Hairdryer"

    def test_inherited_set_name_invalid_empty(self) -> None:
        equipment = HairdressingEquipment(
            "Hairdryer",
            "Professional hairdryer",
            10
        )
        with pytest.raises(IncorrectNameError) as exc_info:
            equipment.set_name("")
        assert "Name cannot be empty" in str(exc_info.value)

    def test_inherited_set_name_invalid_whitespace(self) -> None:
        equipment = HairdressingEquipment(
            "Hairdryer",
            "Professional hairdryer",
            10
        )
        with pytest.raises(IncorrectNameError) as exc_info:
            equipment.set_name("   ")
        assert "Name cannot be empty" in str(exc_info.value)

    def test_inherited_set_name_invalid_non_string(self) -> None:
        equipment = HairdressingEquipment(
            "Hairdryer",
            "Professional hairdryer",
            10
        )
        with pytest.raises(TypeError) as exc_info:
            equipment.set_name(123)
        assert "Name must be a string" in str(exc_info.value)

    def test_inherited_set_description(self) -> None:
        equipment = HairdressingEquipment(
            "Hairdryer",
            "Professional hairdryer",
            10
        )
        equipment.set_description("New description")
        assert equipment.get_description() == "New description"

    @patch('random.random')
    def test_use_equipment_multiple_calls(self, mock_random) -> None:
        mock_random.return_value = 0.05
        equipment = HairdressingEquipment(
            "Hairdryer",
            "Professional hairdryer",
            5
        )
        initial_amount = equipment.get_amount()
        equipment.use_equipment()
        assert equipment.get_amount() == initial_amount - 1

        equipment.use_equipment()
        assert equipment.get_amount() == initial_amount - 2
