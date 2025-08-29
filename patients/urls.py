from django.urls import path
from .views import *

urlpatterns = [
    path("", patient_login_view, name="patient_login"),
    path("dashboard/", patient_dashboard, name="patient_dashboard"),
    path("prescription/", prescription, name="prescription"),
    path("prescriptions/<int:pk>/", prescription_detail, name="prescription_detail"),
    path("appointment/", appointment, name="appointment"),
    path("invoice", invoice_list, name="invoice_list"),
    path("<int:pk>/", invoice_detail, name="invoice_detail"),
    
]
