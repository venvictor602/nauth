from django.db import models
from django.contrib.auth.models import User


class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="patient_profile")

    # Extra patient info
    patient_id = models.CharField(max_length=20, unique=True)  # E-Card / Hospital ID
    gender_choices = [
        ("M", "Male"),
        ("F", "Female"),
    ]
    gender = models.CharField(max_length=1, choices=gender_choices)
    date_of_birth = models.DateField()

    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    # Emergency Contact
    next_of_kin = models.CharField(max_length=100)
    relationship = models.CharField(max_length=50, blank=True, null=True)
    emergency_contact = models.CharField(max_length=20)

    # Hospital tracking
    is_inpatient = models.BooleanField(default=False)
    date_registered = models.DateTimeField(auto_now_add=True)
    blood_pressure = models.CharField(max_length=3, blank=True, null=True)
    heart_rate = models.CharField(max_length=3, blank=True, null=True)
    weight = models.CharField(max_length=3, blank=True, null=True)
    bmi = models.CharField(max_length=3, blank=True, null=True)
    pulse = models.CharField(max_length=3, blank=True, null=True)
    spo2 = models.CharField(max_length=3, blank=True, null=True)
    temp = models.CharField(max_length=3, blank=True, null=True)
    height = models.CharField(max_length=3, blank=True, null=True)







    def __str__(self):
        return f"{self.patient_id} - {self.user.get_full_name()}"





class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="doctor_profile")
    first_name = models.CharField(max_length=20, blank=True, null=True)
    last_name = models.CharField(max_length=20, blank=True, null=True)
    doctor_id = models.CharField(max_length=20, unique=True)
    specialization = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    room_number = models.CharField(max_length=20, blank=True, null=True)
    date_registered = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Dr. {self.first_name} {self.last_name} - {self.specialization}"



class Appointment(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("ACCEPTED", "Accepted"),
        ("REJECTED", "Rejected"),
        ("CANCELLED", "Cancelled"),
    ]

    patient = models.ForeignKey("Patient", on_delete=models.CASCADE, related_name="appointments")
    doctor = models.ForeignKey("Doctor", on_delete=models.CASCADE, related_name="appointments")

    appointment_date = models.DateTimeField()
    reason = models.TextField(blank=True, null=True)

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="PENDING")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def accept(self):
        self.status = "ACCEPTED"
        self.save()

    def reject(self):
        self.status = "REJECTED"
        self.save()

    def __str__(self):
        return f"Appointment {self.id} - {self.patient.user.get_full_name()} with {self.doctor.user.get_full_name()}"





class Prescription(models.Model):
    patient = models.ForeignKey("Patient", on_delete=models.CASCADE, related_name="prescriptions")
    doctor = models.ForeignKey("Doctor", on_delete=models.CASCADE, related_name="prescriptions")
    appointment = models.ForeignKey("Appointment", on_delete=models.SET_NULL, blank=True, null=True, related_name="prescriptions")

    diagnosis = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Prescription {self.id} for {self.patient.user.get_full_name()} by Dr. {self.doctor.user.get_full_name()}"


class PrescriptionItem(models.Model):
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name="items")
    
    medicine_name = models.CharField(max_length=100)
    dosage = models.CharField(max_length=50, help_text="e.g. 500mg, 1 tablet")
    frequency = models.CharField(max_length=50, help_text="e.g. Twice a day")
    duration = models.CharField(max_length=50, help_text="e.g. 5 days")
    instructions = models.TextField(blank=True, null=True, help_text="Additional instructions (e.g. Take after meals)")

    def __str__(self):
        return f"{self.medicine_name} - {self.dosage} for {self.prescription.patient.user.get_full_name()}"
