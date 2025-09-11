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

from patients.models import *

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



@login_required
def doctor_appointment(request):
    if not hasattr(request.user, "doctor_profile"):
        return redirect("doctor_login")  # or raise PermissionDenied
    
    doctor = request.user.doctor_profile
    appointments = Appointment.objects.filter(doctor=doctor).order_by("-appointment_date")
    return render(request, "doctors-appointments.html", {"appointments": appointments})



@login_required
def update_appointment_status(request, pk):
    if request.method == "POST":
        appointment = get_object_or_404(Appointment, pk=pk, doctor=request.user)
        new_status = request.POST.get("status")

        if new_status not in dict(Appointment.STATUS_CHOICES):
            return JsonResponse({"success": False, "error": "Invalid status."})

        appointment.status = new_status
        appointment.save()
        return JsonResponse({"success": True})

    return JsonResponse({"success": False, "error": "Invalid request"})




@login_required
def doctor_prescription_list(request):
    """List prescriptions for logged-in doctor and allow creating new"""
    doctor = request.user.doctor_profile
    prescriptions = Prescription.objects.filter(doctor=doctor).order_by("-created_at")

    # For form dropdowns
    patients = Patient.objects.all()
    appointments = Appointment.objects.filter(doctor=doctor)

    return render(request, "doctor_prescription_list.html", {
        "prescriptions": prescriptions,
        "patients": patients,
        "appointments": appointments,
    })


@login_required
def doctor_add_prescription(request):
    doctor = request.user.doctor_profile  # doctor is linked via OneToOne to User

    if request.method == "POST":
        patient_id = request.POST.get("patient")
        appointment_id = request.POST.get("appointment")

        # Get patient
        patient = get_object_or_404(Patient, id=patient_id)

        # Appointment is optional
        appointment = None
        if appointment_id:
            appointment = get_object_or_404(Appointment, id=appointment_id, doctor=doctor)

        # Create prescription
        prescription = Prescription.objects.create(
            patient=patient,
            doctor=doctor,
            appointment=appointment,
            title=request.POST.get("title"),
            department=request.POST.get("department"),
            consultation_type=request.POST.get("consultation_type"),
            diagnosis=request.POST.get("diagnosis"),
            notes=request.POST.get("notes"),
            advice=request.POST.get("advice"),
            follow_up_notes=request.POST.get("follow_up_notes"),
            follow_up_date=request.POST.get("follow_up_date") or None,
        )

        # Medicine fields (lists)
        medicine_names = request.POST.getlist("medicine_name[]")
        dosages = request.POST.getlist("dosage[]")
        frequencies = request.POST.getlist("frequency[]")
        durations = request.POST.getlist("duration[]")
        timings = request.POST.getlist("timings[]")
        instructions = request.POST.getlist("instructions[]")

        # Loop through medicines
        for med, dose, freq, dur, time, instr in zip(
            medicine_names, dosages, frequencies, durations, timings, instructions
        ):
            if med.strip():  # ensure not empty
                PrescriptionItem.objects.create(
                    prescription=prescription,
                    medicine_name=med,
                    dosage=dose,
                    frequency=freq,
                    duration=dur,
                    timings=time,
                    instructions=instr,
                )

        messages.success(request, "Prescription added successfully!")
        return redirect("doctor_prescription_list")

    # GET request → show modal form context
    patients = Patient.objects.filter(appointments__doctor=doctor).distinct()
    appointments = Appointment.objects.filter(doctor=doctor)

    return render(request, "doctor/add_prescription.html", {
        "patients": patients,
        "appointments": appointments,
    })



@login_required
def doctor_prescription_detail(request, pk):
    """Show detailed view of one prescription (for doctor)"""
    try:
        doctor = request.user.doctor_profile
    except Doctor.DoesNotExist:
        return render(request, "error.html", {"message": "You are not registered as a doctor."})

    prescription = get_object_or_404(Prescription, pk=pk, doctor=doctor)
    return render(request, "doctor_prescription_detail.html", {"prescription": prescription})
