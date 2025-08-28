from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Count
from .models import *
from doctor.models import *


def patient_login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            if hasattr(user, "patient_profile"):  # ✅ ensure it's a patient
                login(request, user)
                messages.success(request, "Login successful")
                return redirect("patient_dashboard")  # replace with your patient home/dashboard
            else:
                messages.error(request, "This account is not a patient account")
        else:
            messages.error(request, "Invalid username or password")

    return render(request, "login.html")







@login_required
def patient_dashboard(request):
    patient = request.user.patient_profile

    wallet = getattr(patient, "wallet", None)
    wallet_balance = wallet.balance if wallet else 0

    # --- Appointments stats ---
    total_appointments = patient.appointments.count()
    last_week = timezone.now() - timedelta(days=7)
    last_week_appointments = patient.appointments.filter(created_at__gte=last_week).count()

    prev_week = last_week - timedelta(days=7)
    prev_week_appointments = patient.appointments.filter(
        created_at__gte=prev_week, created_at__lt=last_week
    ).count()

    if prev_week_appointments > 0:
        growth_rate = round(((last_week_appointments - prev_week_appointments) / prev_week_appointments) * 100, 2)
    else:
        growth_rate = 100 if last_week_appointments > 0 else 0

    # --- Prescriptions stats ---
    total_prescriptions = patient.prescriptions.count()
    last_week_prescriptions = patient.prescriptions.filter(created_at__gte=last_week).count()

    prev_week_prescriptions = patient.prescriptions.filter(
        created_at__gte=prev_week, created_at__lt=last_week
    ).count()

    if prev_week_prescriptions > 0:
        prescription_growth = round(((last_week_prescriptions - prev_week_prescriptions) / prev_week_prescriptions) * 100, 2)
    else:
        prescription_growth = 100 if last_week_prescriptions > 0 else 0

    # --- Top 5 Doctors used ---
    top_doctors = (
        patient.appointments.values("doctor")
        .annotate(total=Count("id"))
        .order_by("-total")[:5]
    )

    # Replace doctor IDs with doctor objects
    for d in top_doctors:
        d["doctor_obj"] = Doctor.objects.get(id=d["doctor"])
    
    top_prescriptions = (
    patient.prescriptions.all()
    .order_by("-created_at")[:5]
    )

    recent_activities = patient.activities.select_related("created_by")[:5]
    recent_appointments = Appointment.objects.select_related("doctor", "patient").order_by("-appointment_date")[:5]

    context = {
        "patient": patient,
        "total_appointments": total_appointments,
        "last_week_appointments": last_week_appointments,
        "growth_rate": growth_rate,

        "total_prescriptions": total_prescriptions,
        "last_week_prescriptions": last_week_prescriptions,
        "prescription_growth": prescription_growth,

        "top_doctors": top_doctors,
        "blood_pressure":patient.blood_pressure,
        "heart_rate":patient.heart_rate,
        "weight":patient.weight,
        "bmi":patient.bmi,
        "pulse":patient.pulse,
        "spo2":patient.spo2,
        "temp":patient.temp,
        "height":patient.height,
        "top_prescriptions": top_prescriptions,   # 👈 added here
         "recent_activities": recent_activities,
         "wallet_balance": wallet_balance,   # 👈 Added to context
         "recent_appointments":recent_appointments,
    }
    return render(request, "dashboard.html", context)

