import sys
from typing import Callable

from src.entities.management.booking import Booking
from src.entities.salon import Salon
from src.utils.booking_status import BookingStatus
from src.utils.validator import validate_name, validate_age
from src.entities.management.master import Master
from src.utils.masters_specialization import MastersSpecialization
from src.entities.inventory.cosmetics import Cosmetics
from src.entities.inventory.hairdressing_equipment import HairdressingEquipment
from src.entities.services.hair_service import HairService
from src.entities.services.cosmetic_procedure import CosmeticProcedure
from src.entities.management.client import Client


class SalonCLI:
    def __init__(self, salon: Salon) -> None:
        self.__salon = salon
        self.__is_running = True

    def run(self) -> None:
        print(
            f"\nWelcome to '{self.__salon.get_name()}'"
            f" Salon Management System!"
        )

        while self.__is_running:
            self.__show_main_menu()
            choice = input("Select an option: ").strip()
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
        """Gathers data to create and hire a new Master."""

        name = input("Enter master's name: ")
        age = int(input("Enter master's age: "))

        print("\nAvailable Specializations:")
        specs = list(MastersSpecialization)
        for i, spec in enumerate(specs, 1):
            print(f"{i}. {spec.value}")

        spec_choice = int(input("Select specialization (number): "))
        selected_spec = specs[spec_choice - 1]

        new_master = Master(name, age, selected_spec)
        self.__salon.hire_staff(new_master)
        print(f"Master {name} has been successfully hired!")

    def __handle_fire_staff(self) -> None:
        """Logic to remove a master from the staff list."""
        staff = self.__salon.get_staff()
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
        if 1 <= choice <= len(staff):
            target_master = staff[choice - 1]
            self.__salon.fire_staff(target_master)
            print(f"Master {target_master.get_name()} has been fired.")
        else:
            raise ValueError("Invalid staff member selection.")

    def __show_staff(self) -> None:
        """Displays all masters in the salon."""
        staff = self.__salon.get_staff()
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

            choice = input("Select an action: ").strip()

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

            choice = input("Action: ").strip()
            if choice == "1":
                self.__view_inventory()
            elif choice == "2":
                self.__safe_execute(self.__handle_sale)
            elif choice == "3":
                self.__safe_execute(self.__handle_restock)
            elif choice == "0":
                break

    def __view_inventory(self) -> None:
        """Shows inventory with specific details for cosmetics and equipment."""

        all_items = self.__salon.get_inventory()
        if not all_items:
            print("\nInventory is empty.")
            return

        print("\n--- SALON INVENTORY REPORT ---")
        for item in all_items:
            name = item.get_name()
            amount = item.get_amount()

            if isinstance(item, Cosmetics):
                price = item.get_price()
                print(
                    f"[Cosmetic] {name} | "
                    f"Stock: {amount} | "
                    f"Price: {price}BYN"
                )

            elif isinstance(item, HairdressingEquipment):
                print(f"[Equipment] {name} | Stock: {amount}")

    def __handle_sale(self) -> None:
        """Gathers input and calls the salon's sell_product method."""
        name = input("Enter product name: ")
        qty = int(input("Enter quantity to sell: "))
        self.__salon.sell_product(name, qty)
        print(f"Current Salon Balance: {self.__salon.check_balance()}BYN")

    def __handle_restock(self) -> None:
        """Adds quantity to existing items or creates a new InventoryItem."""
        name = input("Enter item name: ")
        existing_item = self.__salon.find_product(name)

        if existing_item:

            print(
                f"Item '{name}' found. "
                f"Current amount: {existing_item.get_amount()}"
            )
            refill = int(input("How many units to add? "))
            new_total = existing_item.get_amount() + refill
            existing_item.set_amount(new_total)
            print(
                f"Successfully restocked. "
                f"New total: {existing_item.get_amount()}"
            )

        else:
            print(f"Item '{name}' not found. Let's create a new one.")
            self.__create_new_inventory_item(name)

    def __create_new_inventory_item(self, name: str) -> None:
        """Helper to instantiate and add a new item to salon."""

        print("Select category: 1. Cosmetics, 2. Hairdressing Equipment")
        cat = input("Choice: ").strip()
        desc = input("Description: ")
        amount = int(input("Initial amount: "))

        if cat == "1":
            price = float(input("Price for sale: "))
            new_item = Cosmetics(name, price, desc, amount)
        elif cat == "2":
            new_item = HairdressingEquipment(name, desc, amount)
        else:
            raise ValueError("Invalid category selected.")

        self.__salon.add_to_inventory(new_item)
        print(f"New item '{name}' added to salon inventory.")

    def __service_menu(self) -> None:
        """Submenu for managing salon services."""
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
        """Displays services with their associated inventory requirements."""

        services = self.__salon.get_services()
        if not services:
            print("\nNo services available.")
            return

        print("\n--- SALON SERVICES LIST ---")
        for i, service in enumerate(services, 1):
            base_info = (
                f"{i}. {service.get_name()} | "
                f"Price: {service.get_price()}BYN"
            )

            resources = [e.get_name() for e in service.get_equipment()]
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
        """Gathers data to create a service with linked inventory items."""

        name = input("Service name: ")
        price = float(input("Service price: "))
        print("\nService Type: 1. Hair Service, 2. Cosmetic Procedure")
        s_type = input("Choice: ").strip()

        all_inventory = self.__salon.get_inventory()

        if s_type == "1":
            equipment_list = [
                i for i in all_inventory
                    if isinstance(i, HairdressingEquipment)
            ]
            if not equipment_list:
                print(
                    "Warning: No equipment found in inventory."
                    " Add equipment first."
                )

            selected_equipment = self.__select_items_from_list(
                equipment_list,
                "equipment"
            )
            new_service = HairService(name, price, selected_equipment)

        elif s_type == "2":
            cosmetics_list = [
                i for i in all_inventory
                    if isinstance(i, Cosmetics)
            ]
            if not cosmetics_list:
                print(
                    "Warning: No cosmetics found in inventory. "
                    "Add cosmetics first."
                )

            selected_cosmetics = self.__select_items_from_list(
                cosmetics_list,
                "cosmetics"
            )

            new_service = CosmeticProcedure(name, price, selected_cosmetics)
        else:
            raise ValueError("Invalid service type.")

        self.__salon.add_service(new_service)
        print(f"Service '{name}' added with linked resources!")

    @staticmethod
    def __select_items_from_list(items: list, item_label: str) -> list:
        """Helper to select multiple items from a list by index."""
        if not items:
            return []

        print(f"\nAvailable {item_label}:")
        for i, item in enumerate(items, 1):
            print(f"{i}. {item.get_name()}")

        print(
            f"Enter numbers of {item_label} to link "
            f"(comma separated, e.g., 1,3):"
        )
        choices = input("Selection: ").split(',')

        selected = []
        for c in choices:
            idx = int(c.strip()) - 1
            if 0 <= idx < len(items):
                selected.append(items[idx])
        return selected

    def __handle_remove_service(self) -> None:
        """Removes a service from the salon's list by its index."""
        services = self.__salon.get_services()
        if not services:
            print("Nothing to remove.")
            return

        self.__show_services()

        def action():
            choice_str = input("Select service to remove (number): ")
            choice = int(choice_str)
            if 1 <= choice <= len(services):
                target = services[choice - 1]
                self.__salon.remove_service(target)
                print(f"Service '{target.get_name()}' removed.")
            else:
                raise ValueError("Invalid service selection.")

        self.__safe_execute(action)

    def __booking_menu(self) -> None:
        """Submenu for booking and service execution."""
        while True:
            print("\n--- BOOKING & SERVICES ---")
            print("1. Create New Booking")
            print("2. Execute Service (Hair/Cosmetic)")
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
        """Collects data and creates a booking entry."""

        client_name: str = input("Enter client name: ")
        validate_name(client_name)
        client_age: int = int(input("Enter client age: "))
        validate_age(client_age)
        client = Client(client_name, client_age)

        staff = self.__salon.get_staff()
        if not staff: raise ValueError("No masters available.")
        print("\nSelect Master:")
        for i, m in enumerate(staff, 1):
            print(f"{i}. {m.get_name()} ({m.get_specialization().value})")
        m_idx = int(input("Choice: ")) - 1
        if m_idx < 0 or m_idx >= len(staff):
            raise ValueError("Invalid master selection.")
        master = staff[m_idx]

        services = self.__salon.get_services()
        if not services: raise ValueError("No services available.")
        print("\nSelect Service:")
        for i, s in enumerate(services, 1):
            print(f"{i}. {s.get_name()} ({s.get_price()}BYN)")
        s_idx = int(input("Choice: ")) - 1
        if s_idx < 0 or s_idx >= len(services):
            raise ValueError("Invalid service selection.")
        service = services[s_idx]

        self.__salon.make_booking(client, master, service)
        print(f"Successfully booked {service.get_name()} for {client_name}.")

    def __handle_execute_service(self) -> None:
        """Executes the service associated with a booking."""
        all_bookings = self.__salon.get_bookings()
        if not all_bookings:
            print("No bookings found.")
            return
        confirmed_bookings: list[Booking] = [
            b for b in all_bookings
            if b.get_status() == BookingStatus.CONFIRMED
        ]

        if not confirmed_bookings:
            print("\nNo confirmed bookings found.")
            return

        print("\nSelect Booking to Execute:")
        for i, b in enumerate(confirmed_bookings, 1):
            print(
                f"{i}. {b.get_client().get_name()} - "
                f"{b.get_service().get_name()}"
            )

        idx = int(input("Choice: ")) - 1
        if idx < 0 or idx >= len(confirmed_bookings):
            raise ValueError("Invalid booking selection.")
        target_booking = confirmed_bookings[idx]

        self.__salon.complete_booking(target_booking)
        service = target_booking.get_service()
        print(f"Service '{service.get_name()}' completed!")

        print("--- Inventory Items Used ---")
        equipment = [
            e.get_name() for e in service.get_equipment()
        ]
        print(
            f"Equipment used: "
            f"{', '.join(equipment) if equipment else 'None'}"
        )

        earned = service.get_price()
        current_balance = self.__salon.check_balance()
        print(f"Money earned: {earned}BYN")
        print(f"Current Salon Balance: {current_balance}BYN")

    def __handle_cancel_booking(self) -> None:
        """Sets booking status to CANCELLED."""

        active_bookings = [
            b for b in self.__salon.get_all_bookings()
            if b.get_status() == BookingStatus.CONFIRMED
        ]

        if not active_bookings:
            print("\nNo confirmed bookings to cancel.")
            return

        print("\nSelect Booking to Cancel:")
        for i, b in enumerate(active_bookings, 1):
            print(
                f"{i}. {b.get_client().get_name()} - "
                f"{b.get_service().get_name()}"
            )

        idx = int(input("Choice: ")) - 1
        if 0 <= idx < len(active_bookings):
            target_booking = active_bookings[idx]
            target_booking.set_status(BookingStatus.CANCELLED)
            print(
                f"Booking for {target_booking.get_client().get_name()}"
                f" has been CANCELLED."
            )
        else:
            raise ValueError("Invalid selection.")

    def __finance_menu(self) -> None:
        """Submenu for financial reports and history."""
        while True:
            print("\n--- FINANCE & HISTORY ---")
            print(f"Current Balance: {self.__salon.check_balance()}BYN")
            print("1. View Services History")
            print("0. Back to Main Menu")

            choice = input("Select an action: ").strip()
            if choice == "1":
                self.__show_history()
            elif choice == "0":
                break

    def __show_history(self) -> None:
        """Shows only bookings with status DONE OR CANCELLED."""
        from utils.booking_status import BookingStatus

        all_bookings = self.__salon.get_all_bookings()
        bookings = [
            b
            for b in all_bookings
            if b.get_status() == BookingStatus.DONE or
               b.get_status() == BookingStatus.CANCELLED
        ]

        if not bookings:
            print("\nNo services in history.")
            return

        print("\n--- SERVICES HISTORY ---")
        for b in bookings:
            print(f"Client: {b.get_client().get_name()} | "
                  f"Service: {b.get_service().get_name()} | "
                  f"Master: {b.get_master().get_name()} | "
                  f"Price: {b.get_service().get_price()}BYN | "
                  f"Status: {b.get_status().value}"
                  )

    @staticmethod
    def __safe_execute(action: Callable[[], None]) -> None:
        """
        Wrapper to catch and display business logic errors without crashing.
        """
        try:
            action()
        except Exception as e:
            print(f"\n[SALON ERROR]: {e}")

    def __exit_app(self) -> None:
        print("Exiting... Have a nice day!")
        self.__is_running = False
        sys.exit(0)
