import pytest
from src.entities.inventory.cosmetics import Cosmetics
from src.exceptions.exceptions import PriceError, IncorrectNameError


class TestCosmetics:
    def test_init_valid_parameters(self):
        cosmetics = Cosmetics(
            "Shampoo",
            15.99,
            "Hair care product",
            10
        )
        assert cosmetics.get_name() == "Shampoo"
        assert cosmetics.get_price() == 15.99
        assert cosmetics.get_description() == "Hair care product"
        assert cosmetics.get_amount() == 10

    def test_init_invalid_price_negative(self):
        with pytest.raises(PriceError) as exc_info:
            Cosmetics(
                "Shampoo",
                -10.0,
                "Hair care product",
                10
            )
        assert "Price must be a positive number" in str(exc_info.value)

    def test_init_invalid_price_zero(self):
        with pytest.raises(PriceError) as exc_info:
            Cosmetics("Shampoo", 0.0, "Hair care product", 10)
        assert "Price must be a positive number" in str(exc_info.value)

    def test_init_invalid_name_empty(self):
        with pytest.raises(IncorrectNameError) as exc_info:
            Cosmetics("", 15.99, "Hair care product", 10)
        assert "Name cannot be empty" in str(exc_info.value)

    def test_init_invalid_name_whitespace(self):
        with pytest.raises(IncorrectNameError) as exc_info:
            Cosmetics("   ", 15.99, "Hair care product", 10)
        assert "Name cannot be empty" in str(exc_info.value)

    def test_init_invalid_name_non_string(self):
        with pytest.raises(TypeError) as exc_info:
            Cosmetics(123, 15.99, "Hair care product", 10)
        assert "Name must be a string" in str(exc_info.value)

    def test_init_invalid_amount_negative(self):
        with pytest.raises(ValueError) as exc_info:
            Cosmetics("Shampoo", 15.99, "Hair care product", -5)
        assert "Amount cannot be negative" in str(exc_info.value)

    def test_get_price(self):
        cosmetics = Cosmetics(
            "Conditioner",
            12.50,
            "Hair conditioner",
            5
        )
        assert cosmetics.get_price() == 12.50

    def test_set_price_valid(self):
        cosmetics = Cosmetics(
            "Shampoo",
            15.99,
            "Hair care product",
            10
        )
        cosmetics.set_price(20.99)
        assert cosmetics.get_price() == 20.99

    def test_set_price_invalid_negative(self):
        cosmetics = Cosmetics(
            "Shampoo",
            15.99,
            "Hair care product",
            10
        )
        with pytest.raises(PriceError) as exc_info:
            cosmetics.set_price(-5.0)
        assert "Price must be a positive number" in str(exc_info.value)

    def test_set_price_invalid_zero(self):
        cosmetics = Cosmetics(
            "Shampoo",
            15.99,
            "Hair care product",
            10
        )
        with pytest.raises(PriceError) as exc_info:
            cosmetics.set_price(0.0)
        assert "Price must be a positive number" in str(exc_info.value)

    def test_set_price_valid_float_edge(self):
        cosmetics = Cosmetics(
            "Shampoo",
            15.99,
            "Hair care product",
            10
        )
        cosmetics.set_price(0.01)
        assert cosmetics.get_price() == 0.01

    def test_to_dict(self):
        cosmetics = Cosmetics(
            "Shampoo",
            15.99,
            "Hair care product",
            10
        )
        result = cosmetics.to_dict()
        expected = {
            "type": "Cosmetics",
            "name": "Shampoo",
            "desc": "Hair care product",
            "amount": 10,
            "price": 15.99
        }
        assert result == expected

    def test_from_dict(self):
        data = {
            "name": "Conditioner",
            "price": 12.50,
            "desc": "Hair conditioner",
            "amount": 5
        }
        cosmetics = Cosmetics.from_dict(data)
        assert cosmetics.get_name() == "Conditioner"
        assert cosmetics.get_price() == 12.50
        assert cosmetics.get_description() == "Hair conditioner"
        assert cosmetics.get_amount() == 5

    def test_from_dict_missing_keys(self):
        data = {
            "name": "Conditioner",
            "price": 12.50
        }
        with pytest.raises(KeyError):
            Cosmetics.from_dict(data)

    def test_inherited_get_amount(self):
        cosmetics = Cosmetics(
            "Shampoo",
            15.99,
            "Hair care product",
            10
        )
        assert cosmetics.get_amount() == 10

    def test_inherited_set_amount_valid(self):
        cosmetics = Cosmetics(
            "Shampoo",
            15.99,
            "Hair care product",
            10
        )
        cosmetics.set_amount(15)
        assert cosmetics.get_amount() == 15

    def test_inherited_set_amount_invalid(self):
        cosmetics = Cosmetics("Shampoo", 15.99, "Hair care product", 10)
        with pytest.raises(ValueError) as exc_info:
            cosmetics.set_amount(-5)
        assert "Amount cannot be negative" in str(exc_info.value)

    def test_inherited_reduce_amount_valid(self):
        cosmetics = Cosmetics("Shampoo", 15.99, "Hair care product", 10)
        cosmetics.reduce_amount(3)
        assert cosmetics.get_amount() == 7

    def test_inherited_reduce_amount_invalid_zero(self):
        cosmetics = Cosmetics("Shampoo", 15.99, "Hair care product", 10)
        with pytest.raises(ValueError) as exc_info:
            cosmetics.reduce_amount(0)
        assert "Amount must be positive" in str(exc_info.value)

    def test_inherited_reduce_amount_invalid_negative(self):
        cosmetics = Cosmetics("Shampoo", 15.99, "Hair care product", 10)
        with pytest.raises(ValueError) as exc_info:
            cosmetics.reduce_amount(-3)
        assert "Amount must be positive" in str(exc_info.value)

    def test_inherited_get_name(self):
        cosmetics = Cosmetics("Shampoo", 15.99, "Hair care product", 10)
        assert cosmetics.get_name() == "Shampoo"

    def test_inherited_get_description(self):
        cosmetics = Cosmetics("Shampoo", 15.99, "Hair care product", 10)
        assert cosmetics.get_description() == "Hair care product"

    def test_inherited_set_name_valid(self):
        cosmetics = Cosmetics("Shampoo", 15.99, "Hair care product", 10)
        cosmetics.set_name("New Shampoo")
        assert cosmetics.get_name() == "New Shampoo"

    def test_inherited_set_name_invalid_empty(self):
        cosmetics = Cosmetics("Shampoo", 15.99, "Hair care product", 10)
        with pytest.raises(IncorrectNameError) as exc_info:
            cosmetics.set_name("")
        assert "Name cannot be empty" in str(exc_info.value)

    def test_inherited_set_name_invalid_whitespace(self):
        cosmetics = Cosmetics("Shampoo", 15.99, "Hair care product", 10)
        with pytest.raises(IncorrectNameError) as exc_info:
            cosmetics.set_name("   ")
        assert "Name cannot be empty" in str(exc_info.value)

    def test_inherited_set_name_invalid_non_string(self):
        cosmetics = Cosmetics("Shampoo", 15.99, "Hair care product", 10)
        with pytest.raises(TypeError) as exc_info:
            cosmetics.set_name(123)
        assert "Name must be a string" in str(exc_info.value)

    def test_inherited_set_description(self):
        cosmetics = Cosmetics("Shampoo", 15.99, "Hair care product", 10)
        cosmetics.set_description("New description")
        assert cosmetics.get_description() == "New description"