from django.urls import path
from .views import *

urlpatterns = [
    path("", doctor_login_view, name="doctor_login"),
    path("doctor/dashboard/", doctor_dashboard, name="doctor_dashboard"),
    path("appointments/update/<int:pk>/", update_appointment, name="update_appointment"),
    path("doctor-appointment/", doctor_appointment, name="doctor_appointment"),
    path("appointments/update/<int:pk>/", update_appointment_status, name="update_appointment_status"),
    path("prescriptions/", doctor_prescription_list, name="doctor_prescription_list"),
    path("prescriptions/<int:pk>/", doctor_prescription_detail, name="doctor_prescription_detail"),
    path("prescriptions/add/", doctor_add_prescription, name="doctor_add_prescription"),
]
