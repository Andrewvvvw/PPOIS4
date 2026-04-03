import sys
from typing import Callable

from salon_core.application.errors import AppServiceError
from salon_core.application.service import SalonAppService
from salon_core.entities.inventory.cosmetics import Cosmetics
from salon_core.entities.inventory.hairdressing_equipment import HairdressingEquipment
from salon_core.entities.inventory.inventory_item import InventoryItem
from salon_core.entities.management.booking import Booking
from salon_core.entities.management.master import Master
from salon_core.entities.services.cosmetic_procedure import CosmeticProcedure
from salon_core.entities.services.hair_service import HairService
from salon_core.entities.services.service import Service
from salon_core.utils.booking_status import BookingStatus
from salon_core.utils.masters_specialization import MastersSpecialization
from salon_core.utils.validator import validate_age, validate_name


class SalonCLI:
    def __init__(self, app_service: SalonAppService) -> None:
        self.__app_service = app_service
        self.__is_running: bool = True

    def run(self) -> None:
        print(
            f"\nWelcome to '{self.__app_service.get_salon_name()}'"
            f" Salon Management System!"
        )

        while self.__is_running:
            self.__show_main_menu()
            choice: str = input("Select an option: ").strip()
            self.__handle_main_menu(choice)

    @staticmethod
    def __show_main_menu() -> None:
        print("\n--- MAIN MENU ---")
        print("1. Staff Management")
        print("2. Inventory & Sales")
        print("3. Booking Management")
        print("4. Service Management")
        print("5. Finance & History")
        print("0. Exit")

    def __handle_main_menu(self, choice: str) -> None:
        if choice == "1":
            self.__staff_menu()
        elif choice == "2":
            self.__inventory_menu()
        elif choice == "3":
            self.__booking_menu()
        elif choice == "4":
            self.__service_menu()
        elif choice == "5":
            self.__finance_menu()
        elif choice == "0":
            self.__exit_app()
        else:
            print("Invalid input. Please try again.")

    def __handle_hire_staff(self) -> None:
        name: str = input("Enter master's name: ")
        age = int(input("Enter master's age: "))

        print("\nAvailable Specializations:")
        specs: list[MastersSpecialization] = list(MastersSpecialization)
        for i, spec in enumerate(specs, 1):
            print(f"{i}. {spec.value}")

        spec_choice = int(input("Select specialization (number): "))
        selected_spec: MastersSpecialization = specs[spec_choice - 1]

        self.__app_service.hire_master(name, age, selected_spec)
        print(f"Master {name} has been successfully hired!")

    def __handle_fire_staff(self) -> None:
        staff: list[Master] = self.__app_service.list_staff()
        if not staff:
            print("Nobody to fire. The staff list is empty.")
            return

        print("\nCurrent Staff:")
        for i, master in enumerate(staff, 1):
            print(
                f"{i}. {master.get_name()} "
                f"({master.get_specialization().value})"
            )

        choice = int(input("Select master to fire (number): "))
        self.__app_service.fire_master(choice - 1)
        print(f"Master {staff[choice - 1].get_name()} has been fired.")

    def __show_staff(self) -> None:
        staff: list[Master] = self.__app_service.list_staff()
        if not staff:
            print("No masters hired yet.")
            return

        print("\nOur Team:")
        for master in staff:
            print(f"- {master}")

    def __staff_menu(self) -> None:
        while True:
            print("\n--- STAFF MANAGEMENT ---")
            print("1. Show Staff List")
            print("2. Hire New Master")
            print("3. Fire Master")
            print("0. Back to Main Menu")

            choice: str = input("Select an action: ").strip()

            if choice == "1":
                self.__show_staff()
            elif choice == "2":
                self.__safe_execute(self.__handle_hire_staff)
            elif choice == "3":
                self.__safe_execute(self.__handle_fire_staff)
            elif choice == "0":
                break
            else:
                print("Invalid input. Please try again.")

    def __inventory_menu(self) -> None:
        while True:
            print("\n--- INVENTORY ---")
            print("1. View Products")
            print("2. Sell Product")
            print("3. Restock / Add New Item")
            print("0. Back to Main Menu")

            choice: str = input("Action: ").strip()
            if choice == "1":
                self.__view_inventory()
            elif choice == "2":
                self.__safe_execute(self.__handle_sale)
            elif choice == "3":
                self.__safe_execute(self.__handle_restock)
            elif choice == "0":
                break

    def __view_inventory(self) -> None:
        all_items: list[InventoryItem] = self.__app_service.list_inventory()
        if not all_items:
            print("\nInventory is empty.")
            return

        print("\n--- SALON INVENTORY REPORT ---")
        for item in all_items:
            name: str = item.get_name()
            amount: int = item.get_amount()

            if isinstance(item, Cosmetics):
                price: float = item.get_price()
                print(
                    f"[Cosmetic] {name} | "
                    f"Stock: {amount} | "
                    f"Price: {price}BYN"
                )
            elif isinstance(item, HairdressingEquipment):
                print(f"[Equipment] {name} | Stock: {amount}")

    def __handle_sale(self) -> None:
        name: str = input("Enter product name: ")
        qty = int(input("Enter quantity to sell: "))
        self.__app_service.sell_product(name, qty)
        print(f"Current Salon Balance: {self.__app_service.get_balance()}BYN")

    def __handle_restock(self) -> None:
        name: str = input("Enter item name: ")
        existing_item: InventoryItem | None = next(
            (
                item
                for item in self.__app_service.list_inventory()
                if item.get_name() == name
            ),
            None,
        )

        if existing_item is not None:
            print(
                f"Item '{name}' found. "
                f"Current amount: {existing_item.get_amount()}"
            )
            refill = int(input("How many units to add? "))
            self.__app_service.restock_or_create_item(
                name=name,
                refill_amount=refill,
            )
            updated = next(
                (
                    item
                    for item in self.__app_service.list_inventory()
                    if item.get_name() == name
                ),
                None,
            )
            total = updated.get_amount() if updated is not None else "unknown"
            print(f"Successfully restocked. New total: {total}")
            return

        print(f"Item '{name}' not found. Let's create a new one.")
        self.__create_new_inventory_item(name)

    def __create_new_inventory_item(self, name: str) -> None:
        print("Select category: 1. Cosmetics, 2. Hairdressing Equipment")
        cat: str = input("Choice: ").strip()
        desc: str = input("Description: ")
        amount = int(input("Initial amount: "))

        price = None
        if cat == "1":
            price = float(input("Price for sale: "))

        self.__app_service.restock_or_create_item(
            name=name,
            category=cat,
            description=desc,
            initial_amount=amount,
            price=price,
        )
        print(f"New item '{name}' added to salon inventory.")

    def __service_menu(self) -> None:
        while True:
            print("\n--- SERVICE MANAGEMENT ---")
            print("1. Show Available Services")
            print("2. Add New Service")
            print("3. Remove Service")
            print("0. Back to Main Menu")

            choice = input("Select an action: ").strip()

            if choice == "1":
                self.__show_services()
            elif choice == "2":
                self.__safe_execute(self.__handle_add_service)
            elif choice == "3":
                self.__safe_execute(self.__handle_remove_service)
            elif choice == "0":
                break
            else:
                print("Invalid input.")

    def __show_services(self) -> None:
        services: list[Service] = self.__app_service.list_services()
        if not services:
            print("\nNo services available.")
            return

        print("\n--- SALON SERVICES LIST ---")
        for i, service in enumerate(services, 1):
            base_info = (
                f"{i}. {service.get_name()} | "
                f"Price: {service.get_price()}BYN"
            )

            resources: list[str] = [
                item.get_name() for item in service.get_equipment()
            ]
            if isinstance(service, HairService):
                resource_label = "Equipment"
            elif isinstance(service, CosmeticProcedure):
                resource_label = "Cosmetics"
            else:
                resource_label = "Resources"

            resource_str = ", ".join(resources) if resources else "None linked"
            print(f"{base_info}")
            print(f"   Required {resource_label}: {resource_str}")

    def __handle_add_service(self) -> None:
        name = input("Service name: ")
        price = float(input("Service price: "))
        print("\nService Type: 1. Hair Service, 2. Cosmetic Procedure")
        s_type = input("Choice: ").strip()

        all_inventory: list[InventoryItem] = self.__app_service.list_inventory()

        if s_type == "1":
            equipment_list: list[HairdressingEquipment] = [
                item for item in all_inventory if isinstance(item, HairdressingEquipment)
            ]
            if not equipment_list:
                print("Warning: No equipment found in inventory. Add equipment first.")
            selected_indexes: list[int] = self.__select_items_from_list(
                equipment_list,
                "equipment",
            )
            self.__app_service.add_service(name, price, "hair", selected_indexes)

        elif s_type == "2":
            cosmetics_list: list[Cosmetics] = [
                item for item in all_inventory if isinstance(item, Cosmetics)
            ]
            if not cosmetics_list:
                print("Warning: No cosmetics found in inventory. Add cosmetics first.")

            selected_indexes: list[int] = self.__select_items_from_list(
                cosmetics_list,
                "cosmetics",
            )
            self.__app_service.add_service(name, price, "cosmetic", selected_indexes)
        else:
            raise ValueError("Invalid service type.")

        print(f"Service '{name}' added with linked resources!")

    @staticmethod
    def __select_items_from_list(items: list, item_label: str) -> list[int]:
        if not items:
            return []

        print(f"\nAvailable {item_label}:")
        for i, item in enumerate(items, 1):
            print(f"{i}. {item.get_name()}")

        print(
            f"Enter numbers of {item_label} to link "
            f"(comma separated, e.g., 1,3):"
        )
        choices = input("Selection: ").split(",")

        selected = []
        for choice in choices:
            idx = int(choice.strip()) - 1
            if 0 <= idx < len(items):
                selected.append(idx)
        return selected

    def __handle_remove_service(self) -> None:
        services: list[Service] = self.__app_service.list_services()
        if not services:
            print("Nothing to remove.")
            return

        self.__show_services()

        choice_str = input("Select service to remove (number): ")
        choice = int(choice_str)
        self.__app_service.remove_service(choice - 1)
        print(f"Service '{services[choice - 1].get_name()}' removed.")

    def __booking_menu(self) -> None:
        while True:
            print("\n--- BOOKING & SERVICES ---")
            print("1. Create New Booking")
            print("2. Execute Booking (Hair/Cosmetic)")
            print("3. Cancel Booking")
            print("0. Back to Main Menu")

            choice = input("Select an action: ").strip()

            if choice == "1":
                self.__safe_execute(self.__handle_create_booking)
            elif choice == "2":
                self.__safe_execute(self.__handle_execute_service)
            elif choice == "3":
                self.__safe_execute(self.__handle_cancel_booking)
            elif choice == "0":
                break
            else:
                print("Invalid input.")

    def __handle_create_booking(self) -> None:
        client_name: str = input("Enter client name: ")
        validate_name(client_name)
        client_age: int = int(input("Enter client age: "))
        validate_age(client_age)

        staff: list[Master] = self.__app_service.list_staff()
        if not staff:
            raise ValueError("No masters available.")
        print("\nSelect Master:")
        for i, master in enumerate(staff, 1):
            print(f"{i}. {master.get_name()} ({master.get_specialization().value})")
        m_idx = int(input("Choice: ")) - 1

        services: list[Service] = self.__app_service.list_services()
        if not services:
            raise ValueError("No services available.")
        print("\nSelect Service:")
        for i, service in enumerate(services, 1):
            print(f"{i}. {service.get_name()} ({service.get_price()}BYN)")
        s_idx = int(input("Choice: ")) - 1

        self.__app_service.create_booking(client_name, client_age, m_idx, s_idx)
        print(f"Successfully booked {services[s_idx].get_name()} for {client_name}.")

    def __handle_execute_service(self) -> None:
        confirmed_bookings: list[Booking] = self.__app_service.list_confirmed_bookings()

        if not confirmed_bookings:
            print("\nNo confirmed bookings found.")
            return

        print("\nSelect Booking to Execute:")
        for i, booking in enumerate(confirmed_bookings, 1):
            print(
                f"{i}. {booking.get_client().get_name()} - "
                f"{booking.get_service().get_name()}"
            )

        idx = int(input("Choice: ")) - 1
        target_booking: Booking = confirmed_bookings[idx]

        self.__app_service.execute_booking(idx)
        service: Service = target_booking.get_service()
        print(f"Service '{service.get_name()}' completed!")

        print("--- Inventory Items Used ---")
        equipment: list[str] = [
            item.get_name() for item in service.get_equipment()
        ]
        print(
            f"Equipment used: "
            f"{', '.join(equipment) if equipment else 'None'}"
        )

        earned: float = service.get_price()
        current_balance: float = self.__app_service.get_balance()
        print(f"Money earned: {earned}BYN")
        print(f"Current Salon Balance: {current_balance}BYN")

    def __handle_cancel_booking(self) -> None:
        active_bookings: list[Booking] = self.__app_service.list_confirmed_bookings()

        if not active_bookings:
            print("\nNo confirmed bookings to cancel.")
            return

        print("\nSelect Booking to Cancel:")
        for i, booking in enumerate(active_bookings, 1):
            print(
                f"{i}. {booking.get_client().get_name()} - "
                f"{booking.get_service().get_name()}"
            )

        idx = int(input("Choice: ")) - 1
        target_booking: Booking = active_bookings[idx]
        self.__app_service.cancel_booking(idx)
        print(
            f"Booking for {target_booking.get_client().get_name()}"
            f" has been CANCELLED."
        )

    def __finance_menu(self) -> None:
        while True:
            print("\n--- FINANCE & HISTORY ---")
            print(f"Current Balance: {self.__app_service.get_balance()}BYN")
            print("1. View Bookings History")
            print("0. Back to Main Menu")

            choice = input("Select an action: ").strip()
            if choice == "1":
                self.__show_history()
            elif choice == "0":
                break

    def __show_history(self) -> None:
        bookings: list[Booking] = self.__app_service.get_booking_history()

        if not bookings:
            print("\nNo bookings in history.")
            return

        print("\n--- BOOKINGS HISTORY ---")
        for booking in bookings:
            print(
                f"Client: {booking.get_client().get_name()} | "
                f"Service: {booking.get_service().get_name()} | "
                f"Master: {booking.get_master().get_name()} | "
                f"Price: {booking.get_service().get_price()}BYN | "
                f"Status: {booking.get_status().value}"
            )

    @staticmethod
    def __safe_execute(action: Callable[[], None]) -> None:
        try:
            action()
        except (AppServiceError, Exception) as error:
            print(f"\n[SALON ERROR]: {error}")

    def __exit_app(self) -> None:
        print("Exiting... Have a nice day!")
        self.__is_running = False
        sys.exit(0)
