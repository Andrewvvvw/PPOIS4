from django.urls import path

from salon_web import views

urlpatterns = [
    path("", views.dashboard_view, name="dashboard"),
    path("staff/", views.staff_view, name="staff"),
    path("inventory/", views.inventory_view, name="inventory"),
    path("services/", views.services_view, name="services"),
    path("bookings/", views.bookings_view, name="bookings"),
    path("finance/", views.finance_view, name="finance"),
]
