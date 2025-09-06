from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .models import Doctor
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404

from patients.models import Appointment

def doctor_login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            # ✅ Ensure this user has a Doctor profile
            if hasattr(user, "doctor_profile"):
                login(request, user)
                messages.success(request, "Welcome Doctor!")
                return redirect("doctor_dashboard")  # 🔄 Replace with your doctor dashboard route
            else:
                messages.error(request, "This account is not registered as a doctor.")
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, "login.html")



@login_required
def doctor_dashboard(request):
    # Ensure only doctors can access
    if not hasattr(request.user, "doctor_profile"):
        return redirect("doctor_login")

    doctor = request.user.doctor_profile
    context = {
        "doctor": doctor,
    }
    return render(request, "doctor-dashboard.html", context)




@login_required
def doctor_dashboard(request):
    if not hasattr(request.user, "doctor_profile"):
        return redirect("doctor_login")

    doctor = request.user.doctor_profile

    # Count appointments for this doctor
    total_appointments = doctor.appointments.count()
    pending_appointments = doctor.appointments.filter(status="PENDING").count()
    accepted_appointments = doctor.appointments.filter(status="ACCEPTED").count()
    rejected_appointments = doctor.appointments.filter(status="REJECTED").count()
    cancelled_appointments = doctor.appointments.filter(status="CANCELLED").count()

    # recent 10 appointments
    recent_appointments = doctor.appointments.select_related("patient__user").order_by("-appointment_date")[:10]

    # Top 5 patients (most appointments with this doctor)
    top_patients = (
        doctor.appointments
        .values(
            "patient__id",
            "patient__first_name",
            "patient__last_name",
            "patient__phone_number",
        )
        .annotate(total_appointments=Count("id"))
        .order_by("-total_appointments")[:5]
    )
    context = {
        "doctor": doctor,
        "total_appointments": total_appointments,
        "pending_appointments": pending_appointments,
        "accepted_appointments": accepted_appointments,
        "rejected_appointments": rejected_appointments,
        "cancelled_appointments": cancelled_appointments,
        "recent_appointments": recent_appointments,
        "top_patients": top_patients,
    }
    return render(request, "doctor-dashboard.html", context)




@login_required
@csrf_exempt   # not strictly needed since we already send CSRF token, but keeps fetch happy
def update_appointment(request, pk):
    if request.method == "POST":
        appointment = get_object_or_404(Appointment, pk=pk)

        new_status = request.POST.get("status")
        if new_status not in dict(Appointment.STATUS_CHOICES):
            return JsonResponse({"success": False, "error": "Invalid status"}, status=400)

        appointment.status = new_status
        appointment.save(update_fields=["status"])

        return JsonResponse({"success": True, "message": "Appointment updated successfully"})

    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)