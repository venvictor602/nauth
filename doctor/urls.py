from django.urls import path
from .views import *

urlpatterns = [
    path("", doctor_login_view, name="doctor_login"),
    path("doctor/dashboard/", doctor_dashboard, name="doctor_dashboard"),
    path("appointments/update/<int:pk>/", update_appointment, name="update_appointment"),
]
