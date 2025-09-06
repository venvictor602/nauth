from django.urls import path
from .views import *

urlpatterns = [
    path("", doctor_login_view, name="doctor_login"),
    path("doctor/dashboard/", doctor_dashboard, name="doctor_dashboard"),
    path("appointments/update/<int:pk>/", update_appointment, name="update_appointment"),
    path("doctor-appointment/", doctor_appointment, name="doctor_appointment"),
    path("appointments/update/<int:pk>/", update_appointment_status, name="update_appointment_status"),
]
