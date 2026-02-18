import pytest
from src.entities.services.cosmetic_procedure import CosmeticProcedure
from src.entities.management.client import Client
from src.entities.management.master import Master
from src.entities.inventory.cosmetics import Cosmetics
from src.utils.masters_specialization import MastersSpecialization


class TestCosmeticProcedure:
    def test_init_valid_parameters(self) -> None:
        cosmetics = [Cosmetics("Cream", 10.0, "Face cream", 5)]
        procedure = CosmeticProcedure("Facial", 50.0, cosmetics)

        assert procedure.get_name() == "Facial"
        assert procedure.get_price() == 50.0
        assert procedure.get_equipment() == cosmetics

    def test_init_empty_cosmetics_list(self) -> None:
        cosmetics = []
        procedure = CosmeticProcedure("Basic Treatment", 30.0, cosmetics)

        assert procedure.get_name() == "Basic Treatment"
        assert procedure.get_price() == 30.0
        assert procedure.get_equipment() == []

    def test_init_single_cosmetic(self) -> None:
        cosmetics = [Cosmetics("Serum", 15.0, "Face serum", 3)]
        procedure = CosmeticProcedure("Treatment", 40.0, cosmetics)

        assert procedure.get_name() == "Treatment"
        assert procedure.get_price() == 40.0
        assert len(procedure.get_equipment()) == 1
        assert procedure.get_equipment()[0].get_name() == "Serum"

    def test_init_multiple_cosmetics(self) -> None:
        cosmetics = [
            Cosmetics("Cream", 10.0, "Face cream", 5),
            Cosmetics("Serum", 15.0, "Face serum", 3),
            Cosmetics("Mask", 8.0, "Face mask", 2)
        ]
        procedure = CosmeticProcedure("Full Facial", 80.0, cosmetics)

        assert procedure.get_name() == "Full Facial"
        assert procedure.get_price() == 80.0
        assert len(procedure.get_equipment()) == 3

    def test_get_equipment_returns_copy(self) -> None:
        cosmetics = [Cosmetics("Cream", 10.0, "Face cream", 5)]
        procedure = CosmeticProcedure("Facial", 50.0, cosmetics)

        equipment1 = procedure.get_equipment()
        equipment2 = procedure.get_equipment()

        assert equipment1 is not equipment2
        assert equipment1 == equipment2

    def test_set_cosmetics_valid(self) -> None:
        cosmetics1 = [Cosmetics("Cream", 10.0, "Face cream", 5)]
        cosmetics2 = [Cosmetics("Serum", 15.0, "Face serum", 3)]
        procedure = CosmeticProcedure("Facial", 50.0, cosmetics1)

        procedure.set_cosmetics(cosmetics2)
        assert procedure.get_equipment() == cosmetics2
        assert len(procedure.get_equipment()) == 1

    def test_set_cosmetics_empty(self) -> None:
        cosmetics = [Cosmetics("Cream", 10.0, "Face cream", 5)]
        procedure = CosmeticProcedure("Facial", 50.0, cosmetics)

        procedure.set_cosmetics([])
        assert procedure.get_equipment() == []

    def test_set_cosmetics_multiple(self) -> None:
        cosmetics1 = [Cosmetics("Cream", 10.0, "Face cream", 5)]
        cosmetics2 = [
            Cosmetics("Serum", 15.0, "Face serum", 3),
            Cosmetics("Mask", 8.0, "Face mask", 2)
        ]
        procedure = CosmeticProcedure("Facial", 50.0, cosmetics1)

        procedure.set_cosmetics(cosmetics2)
        assert len(procedure.get_equipment()) == 2
        assert procedure.get_equipment()[0].get_name() == "Serum"
        assert procedure.get_equipment()[1].get_name() == "Mask"

    def test_perform_with_multiple_cosmetics(self) -> None:
        cosmetics = [
            Cosmetics("Cream", 10.0, "Face cream", 3),
            Cosmetics("Serum", 15.0, "Face serum", 2),
            Cosmetics("Mask", 8.0, "Face mask", 4)
        ]
        procedure = CosmeticProcedure("Full Treatment", 80.0, cosmetics)

        initial_amounts = [c.get_amount() for c in cosmetics]

        procedure.perform()

        for i, cosmetic in enumerate(cosmetics):
            assert cosmetic.get_amount() == initial_amounts[i] - 1

    def test_can_perform_by_cosmetics_master(self) -> None:
        cosmetics = [Cosmetics("Cream", 10.0, "Face cream", 5)]
        procedure = CosmeticProcedure("Facial", 50.0, cosmetics)
        master = Master("Jane Smith", 30, MastersSpecialization.COSMETICS)

        assert procedure.can_perform_by(master) is True

    def test_can_perform_by_hair_cutting_master(self) -> None:
        cosmetics = [Cosmetics("Cream", 10.0, "Face cream", 5)]
        procedure = CosmeticProcedure("Facial", 50.0, cosmetics)
        master = Master("Bob Johnson", 35, MastersSpecialization.HAIR_CUTTING)

        assert procedure.can_perform_by(master) is False

    def test_can_perform_by_hair_styling_master(self) -> None:
        cosmetics = [Cosmetics("Cream", 10.0, "Face cream", 5)]
        procedure = CosmeticProcedure("Facial", 50.0, cosmetics)
        master = Master("Alice Brown", 28, MastersSpecialization.HAIR_STYLING)

        assert procedure.can_perform_by(master) is False

    def test_to_dict(self) -> None:
        cosmetics = [
            Cosmetics("Cream", 10.0, "Face cream", 5),
            Cosmetics("Serum", 15.0, "Face serum", 3)
        ]
        procedure = CosmeticProcedure("Full Facial", 80.0, cosmetics)

        result = procedure.to_dict()
        expected = {
            "type": "CosmeticProcedure",
            "name": "Full Facial",
            "price": 80.0,
            "resource_names": ["Cream", "Serum"]
        }
        assert result == expected

    def test_to_dict_empty_cosmetics(self) -> None:
        cosmetics = []
        procedure = CosmeticProcedure("Basic Treatment", 30.0, cosmetics)

        result = procedure.to_dict()
        expected = {
            "type": "CosmeticProcedure",
            "name": "Basic Treatment",
            "price": 30.0,
            "resource_names": []
        }
        assert result == expected

    def test_to_dict_single_cosmetic(self) -> None:
        cosmetics = [Cosmetics("Cream", 10.0, "Face cream", 5)]
        procedure = CosmeticProcedure("Facial", 50.0, cosmetics)

        result = procedure.to_dict()
        expected = {
            "type": "CosmeticProcedure",
            "name": "Facial",
            "price": 50.0,
            "resource_names": ["Cream"]
        }
        assert result == expected

    def test_from_dict(self) -> None:
        data = {
            "name": "Facial",
            "price": 50.0
        }
        cosmetics = [Cosmetics("Cream", 10.0, "Face cream", 5)]

        procedure = CosmeticProcedure.from_dict(data, cosmetics)

        assert procedure.get_name() == "Facial"
        assert procedure.get_price() == 50.0
        assert procedure.get_equipment() == cosmetics

    def test_from_dict_different_data(self) -> None:
        data = {
            "name": "Full Treatment",
            "price": 80.0
        }
        cosmetics = [
            Cosmetics("Serum", 15.0, "Face serum", 3),
            Cosmetics("Mask", 8.0, "Face mask", 2)
        ]

        procedure = CosmeticProcedure.from_dict(data, cosmetics)

        assert procedure.get_name() == "Full Treatment"
        assert procedure.get_price() == 80.0
        assert procedure.get_equipment() == cosmetics

    def test_from_dict_empty_cosmetics(self) -> None:
        data = {
            "name": "Basic Treatment",
            "price": 30.0
        }
        cosmetics = []

        procedure = CosmeticProcedure.from_dict(data, cosmetics)

        assert procedure.get_name() == "Basic Treatment"
        assert procedure.get_price() == 30.0
        assert procedure.get_equipment() == []

    def test_inherited_methods(self) -> None:
        cosmetics = [Cosmetics("Cream", 10.0, "Face cream", 5)]
        procedure = CosmeticProcedure("Facial", 50.0, cosmetics)

        assert procedure.get_name() == "Facial"
        assert procedure.get_price() == 50.0

        procedure.set_name("New Facial")
        assert procedure.get_name() == "New Facial"

        procedure.set_price(60.0)
        assert procedure.get_price() == 60.0

    def test_full_workflow(self) -> None:
        cosmetics = [
            Cosmetics("Cream", 10.0, "Face cream", 3),
            Cosmetics("Serum", 15.0, "Face serum", 2)
        ]
        procedure = CosmeticProcedure("Luxury Facial", 100.0, cosmetics)
        master = Master("Jane Doe", 35, MastersSpecialization.COSMETICS)

        assert procedure.can_perform_by(master) is True

        initial_amounts = [c.get_amount() for c in cosmetics]
        procedure.perform()

        for i, cosmetic in enumerate(cosmetics):
            assert cosmetic.get_amount() == initial_amounts[i] - 1

    def test_cosmetic_list_isolation(self) -> None:
        cosmetics = [Cosmetics("Cream", 10.0, "Face cream", 5)]
        procedure = CosmeticProcedure("Facial", 50.0, cosmetics)

        equipment1 = procedure.get_equipment()

        equipment1.append("invalid")
        equipment3 = procedure.get_equipment()

        assert len(equipment3) == 1
        assert "invalid" not in equipment3

    def test_multiple_perform_calls(self) -> None:
        cosmetics = [Cosmetics("Cream", 10.0, "Face cream", 3)]
        procedure = CosmeticProcedure("Facial", 50.0, cosmetics)

        procedure.perform()
        first_amount = cosmetics[0].get_amount()

        procedure.perform()
        second_amount = cosmetics[0].get_amount()

        assert first_amount - 1 == second_amount