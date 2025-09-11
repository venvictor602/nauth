# pharmacy/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path("login/", views.pharmacy_login, name="pharmacy_login"),

    # Core pharmacy features
    path("", views.pharmacy_dashboard, name="pharmacy_dashboard"),
    path("prescription/<int:pk>/", views.prescription_detail, name="pharmacy_prescription_detail"),
    path("dispense/<int:item_id>/", views.dispense_item, name="dispense_item"),
]
