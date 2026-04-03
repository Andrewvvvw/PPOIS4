from django import forms

from salon_core.entities.management.booking import Booking
from salon_core.entities.management.master import Master
from salon_core.entities.services.service import Service
from salon_core.utils.masters_specialization import MastersSpecialization


class HireMasterForm(forms.Form):
    name = forms.CharField(max_length=100)
    age = forms.IntegerField(min_value=0, max_value=120)
    specialization = forms.ChoiceField(
        choices=[(spec.value, spec.value) for spec in MastersSpecialization]
    )


class FireMasterForm(forms.Form):
    staff_index = forms.ChoiceField(choices=())

    def __init__(self, *args, staff: list[Master] | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        staff = staff or []
        self.fields["staff_index"].choices = [
            (str(i), f"{master.get_name()} ({master.get_specialization().value})")
            for i, master in enumerate(staff)
        ]


class SellProductForm(forms.Form):
    name = forms.CharField(max_length=100)
    quantity = forms.IntegerField(min_value=1)


class RestockItemForm(forms.Form):
    name = forms.CharField(max_length=100)
    refill_amount = forms.IntegerField(min_value=1)


class CreateItemForm(forms.Form):
    CATEGORY_CHOICES = [
        ("cosmetics", "Cosmetics"),
        ("equipment", "Hairdressing Equipment"),
    ]

    name = forms.CharField(max_length=100)
    category = forms.ChoiceField(choices=CATEGORY_CHOICES)
    description = forms.CharField(required=False)
    initial_amount = forms.IntegerField(min_value=0)
    price = forms.FloatField(required=False, min_value=0.01)


class AddServiceForm(forms.Form):
    SERVICE_CHOICES = [
        ("hair", "Hair Service"),
        ("cosmetic", "Cosmetic Procedure"),
    ]

    name = forms.CharField(max_length=100)
    price = forms.FloatField(min_value=0)
    service_type = forms.ChoiceField(choices=SERVICE_CHOICES)
    equipment_indexes = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
        choices=(),
    )
    cosmetics_indexes = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
        choices=(),
    )

    def __init__(
        self,
        *args,
        equipment: list | None = None,
        cosmetics: list | None = None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        equipment = equipment or []
        cosmetics = cosmetics or []
        self.fields["equipment_indexes"].choices = [
            (str(i), item.get_name()) for i, item in enumerate(equipment)
        ]
        self.fields["cosmetics_indexes"].choices = [
            (str(i), item.get_name()) for i, item in enumerate(cosmetics)
        ]

    def clean(self):
        cleaned_data = super().clean()
        service_type = cleaned_data.get("service_type")
        equipment_indexes = cleaned_data.get("equipment_indexes") or []
        cosmetics_indexes = cleaned_data.get("cosmetics_indexes") or []

        if service_type == "hair" and cosmetics_indexes:
            raise forms.ValidationError(
                "Hair Service cannot require cosmetics resources."
            )

        if service_type == "cosmetic" and equipment_indexes:
            raise forms.ValidationError(
                "Cosmetic Procedure cannot require equipment resources."
            )

        return cleaned_data


class RemoveServiceForm(forms.Form):
    service_index = forms.ChoiceField(choices=())

    def __init__(self, *args, services: list[Service] | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        services = services or []
        self.fields["service_index"].choices = [
            (str(i), f"{service.get_name()} ({service.get_price()} BYN)")
            for i, service in enumerate(services)
        ]


class CreateBookingForm(forms.Form):
    client_name = forms.CharField(max_length=100)
    client_age = forms.IntegerField(min_value=0, max_value=120)
    master_index = forms.ChoiceField(choices=())
    service_index = forms.ChoiceField(choices=())

    def __init__(
        self,
        *args,
        staff: list[Master] | None = None,
        services: list[Service] | None = None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        staff = staff or []
        services = services or []
        self.fields["master_index"].choices = [
            (str(i), f"{master.get_name()} ({master.get_specialization().value})")
            for i, master in enumerate(staff)
        ]
        self.fields["service_index"].choices = [
            (str(i), f"{service.get_name()} ({service.get_price()} BYN)")
            for i, service in enumerate(services)
        ]


class BookingActionForm(forms.Form):
    booking_index = forms.ChoiceField(choices=())

    def __init__(self, *args, bookings: list[Booking] | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        bookings = bookings or []
        self.fields["booking_index"].choices = [
            (
                str(i),
                f"{booking.get_client().get_name()} - {booking.get_service().get_name()} "
                f"({booking.get_master().get_name()})",
            )
            for i, booking in enumerate(bookings)
        ]
