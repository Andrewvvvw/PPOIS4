from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect, render

from salon_core.application.errors import AppServiceError
from salon_core.application.repositories.json_repository import JsonSalonRepository
from salon_core.application.service import SalonAppService
from salon_core.entities.inventory.cosmetics import Cosmetics
from salon_core.entities.inventory.hairdressing_equipment import HairdressingEquipment
from salon_web.forms import (
    AddServiceForm,
    BookingActionForm,
    CreateBookingForm,
    CreateItemForm,
    FireMasterForm,
    HireMasterForm,
    RemoveServiceForm,
    RestockItemForm,
    SellProductForm,
)


def _get_app_service() -> SalonAppService:
    repository = JsonSalonRepository(
        file_path=str(settings.SALON_DATA_PATH),
        default_salon_name="BEST SALON",
    )
    return SalonAppService(repository)


def dashboard_view(request):
    app_service = _get_app_service()
    context = {"stats": app_service.get_dashboard_stats()}
    return render(request, "salon_web/dashboard.html", context)


def staff_view(request):
    app_service = _get_app_service()
    staff = app_service.list_staff()

    hire_form = HireMasterForm()
    fire_form = FireMasterForm(staff=staff)

    if request.method == "POST":
        action = request.POST.get("action")
        try:
            if action == "hire":
                hire_form = HireMasterForm(request.POST)
                if hire_form.is_valid():
                    app_service.hire_master(
                        hire_form.cleaned_data["name"],
                        hire_form.cleaned_data["age"],
                        hire_form.cleaned_data["specialization"],
                    )
                    messages.success(request, "Master has been hired.")
                    return redirect("staff")
            elif action == "fire":
                fire_form = FireMasterForm(request.POST, staff=staff)
                if fire_form.is_valid():
                    app_service.fire_master(int(fire_form.cleaned_data["staff_index"]))
                    messages.success(request, "Master has been fired.")
                    return redirect("staff")
        except AppServiceError as error:
            messages.error(request, str(error))

    context = {
        "staff": staff,
        "hire_form": hire_form,
        "fire_form": fire_form,
    }
    return render(request, "salon_web/staff.html", context)


def inventory_view(request):
    app_service = _get_app_service()
    inventory = app_service.list_inventory()
    inventory_rows = []
    for item in inventory:
        if isinstance(item, Cosmetics):
            item_type = "Cosmetics"
            price = item.get_price()
        else:
            item_type = "Equipment"
            price = None
        inventory_rows.append(
            {
                "name": item.get_name(),
                "description": item.get_description(),
                "amount": item.get_amount(),
                "type": item_type,
                "price": price,
            }
        )

    sell_form = SellProductForm()
    restock_form = RestockItemForm()
    create_form = CreateItemForm()

    if request.method == "POST":
        action = request.POST.get("action")
        try:
            if action == "sell":
                sell_form = SellProductForm(request.POST)
                if sell_form.is_valid():
                    app_service.sell_product(
                        sell_form.cleaned_data["name"],
                        sell_form.cleaned_data["quantity"],
                    )
                    messages.success(request, "Product sold successfully.")
                    return redirect("inventory")
            elif action == "restock":
                restock_form = RestockItemForm(request.POST)
                if restock_form.is_valid():
                    app_service.restock_or_create_item(
                        name=restock_form.cleaned_data["name"],
                        refill_amount=restock_form.cleaned_data["refill_amount"],
                    )
                    messages.success(request, "Inventory has been restocked.")
                    return redirect("inventory")
            elif action == "create":
                create_form = CreateItemForm(request.POST)
                if create_form.is_valid():
                    category = create_form.cleaned_data["category"]
                    price = create_form.cleaned_data["price"] if category == "cosmetics" else None
                    app_service.restock_or_create_item(
                        name=create_form.cleaned_data["name"],
                        category=category,
                        description=create_form.cleaned_data["description"],
                        initial_amount=create_form.cleaned_data["initial_amount"],
                        price=price,
                    )
                    messages.success(request, "Inventory item has been created.")
                    return redirect("inventory")
        except AppServiceError as error:
            messages.error(request, str(error))

    context = {
        "inventory_rows": inventory_rows,
        "balance": app_service.get_balance(),
        "sell_form": sell_form,
        "restock_form": restock_form,
        "create_form": create_form,
    }
    return render(request, "salon_web/inventory.html", context)


def services_view(request):
    app_service = _get_app_service()

    services = app_service.list_services()
    inventory = app_service.list_inventory()
    equipment = [item for item in inventory if isinstance(item, HairdressingEquipment)]
    cosmetics = [item for item in inventory if isinstance(item, Cosmetics)]

    add_form = AddServiceForm(equipment=equipment, cosmetics=cosmetics)
    remove_form = RemoveServiceForm(services=services)

    if request.method == "POST":
        action = request.POST.get("action")
        try:
            if action == "add":
                add_form = AddServiceForm(
                    request.POST,
                    equipment=equipment,
                    cosmetics=cosmetics,
                )
                if add_form.is_valid():
                    service_type = add_form.cleaned_data["service_type"]
                    if service_type == "hair":
                        selected_indexes = [
                            int(index)
                            for index in add_form.cleaned_data["equipment_indexes"]
                        ]
                    else:
                        selected_indexes = [
                            int(index)
                            for index in add_form.cleaned_data["cosmetics_indexes"]
                        ]

                    app_service.add_service(
                        name=add_form.cleaned_data["name"],
                        price=add_form.cleaned_data["price"],
                        service_type=service_type,
                        resource_indexes=selected_indexes,
                    )
                    messages.success(request, "Service has been added.")
                    return redirect("services")
            elif action == "remove":
                remove_form = RemoveServiceForm(request.POST, services=services)
                if remove_form.is_valid():
                    app_service.remove_service(int(remove_form.cleaned_data["service_index"]))
                    messages.success(request, "Service has been removed.")
                    return redirect("services")
        except AppServiceError as error:
            messages.error(request, str(error))

    context = {
        "services": services,
        "equipment": equipment,
        "cosmetics": cosmetics,
        "add_form": add_form,
        "remove_form": remove_form,
    }
    return render(request, "salon_web/services.html", context)


def bookings_view(request):
    app_service = _get_app_service()

    staff = app_service.list_staff()
    services = app_service.list_services()
    all_bookings = app_service.list_bookings()
    confirmed_bookings = app_service.list_confirmed_bookings()

    create_form = CreateBookingForm(staff=staff, services=services)
    execute_form = BookingActionForm(bookings=confirmed_bookings)
    cancel_form = BookingActionForm(bookings=confirmed_bookings)

    if request.method == "POST":
        action = request.POST.get("action")
        try:
            if action == "create":
                create_form = CreateBookingForm(request.POST, staff=staff, services=services)
                if create_form.is_valid():
                    app_service.create_booking(
                        client_name=create_form.cleaned_data["client_name"],
                        client_age=create_form.cleaned_data["client_age"],
                        master_index=int(create_form.cleaned_data["master_index"]),
                        service_index=int(create_form.cleaned_data["service_index"]),
                    )
                    messages.success(request, "Booking has been created.")
                    return redirect("bookings")
            elif action == "execute":
                execute_form = BookingActionForm(request.POST, bookings=confirmed_bookings)
                if execute_form.is_valid():
                    app_service.execute_booking(int(execute_form.cleaned_data["booking_index"]))
                    messages.success(request, "Booking has been executed.")
                    return redirect("bookings")
            elif action == "cancel":
                cancel_form = BookingActionForm(request.POST, bookings=confirmed_bookings)
                if cancel_form.is_valid():
                    app_service.cancel_booking(int(cancel_form.cleaned_data["booking_index"]))
                    messages.success(request, "Booking has been cancelled.")
                    return redirect("bookings")
        except AppServiceError as error:
            messages.error(request, str(error))

    context = {
        "all_bookings": all_bookings,
        "confirmed_bookings": confirmed_bookings,
        "create_form": create_form,
        "execute_form": execute_form,
        "cancel_form": cancel_form,
    }
    return render(request, "salon_web/bookings.html", context)


def finance_view(request):
    app_service = _get_app_service()
    context = {
        "balance": app_service.get_balance(),
        "history": app_service.get_booking_history(),
    }
    return render(request, "salon_web/finance.html", context)
