from django.db import models
from django.contrib.auth.models import User
from doctor.models import *
from django.core.exceptions import ValidationError


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







class Appointment(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("ACCEPTED", "Accepted"),
        ("REJECTED", "Rejected"),
        ("CANCELLED", "Cancelled"),
    ]

    patient = models.ForeignKey("Patient", on_delete=models.CASCADE, related_name="appointments")
    doctor = models.ForeignKey("doctor.Doctor", on_delete=models.CASCADE, related_name="appointments")
    appointment_date = models.DateTimeField()
    reason = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="PENDING")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if not self.pk:  # only when creating a new appointment
            if self.doctor and self.patient:
                fee = float(self.doctor.fee or 0)
                if fee > 0 and self.patient.wallet.balance < fee:
                    raise ValidationError(
                        {"patient": f"{self.patient.user.get_full_name()} does not have enough balance to book this appointment (Fee: {fee})"}
                    )


    def __str__(self):
        return f"Appointment {self.id} - {self.patient.user.get_full_name()} with {self.doctor.user.get_full_name()}"




class Prescription(models.Model):
    patient = models.ForeignKey("Patient", on_delete=models.CASCADE, related_name="prescriptions")
    doctor = models.ForeignKey("doctor.Doctor", on_delete=models.CASCADE, related_name="prescriptions")
    title= models.CharField(max_length=50, blank=True, null=True,)
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



from django.conf import settings

class PatientActivity(models.Model):
    CATEGORY_CHOICES = [
        ("appointment", "Appointment"),
        ("prescription", "Prescription"),
        ("vitals", "Vitals Check"),
        ("therapy", "Therapy"),
        ("note", "Doctor Note"),
        ("diet", "Dietary Advice"),
    ]
    patient = models.ForeignKey("Patient", on_delete=models.CASCADE, related_name="activities")
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    title = models.CharField(max_length=255)  # short label
    description = models.TextField(blank=True)  # optional longer note
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.patient} - {self.category} - {self.title}"





class Wallet(models.Model):
    patient = models.OneToOneField(
        "patients.Patient", on_delete=models.CASCADE, related_name="wallet"
    )
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def credit(self, amount, description=""):
        """Add funds to wallet"""
        self.balance += amount
        self.save()
        WalletTransaction.objects.create(
            wallet=self, amount=amount, transaction_type="credit", description=description
        )

    def debit(self, amount, description=""):
        """Deduct funds if balance is enough"""
        if self.balance < amount:
            raise ValueError("Insufficient wallet balance")
        self.balance -= amount
        self.save()
        WalletTransaction.objects.create(
            wallet=self, amount=amount, transaction_type="debit", description=description
        )

    def __str__(self):
        return f"{self.patient} Wallet - Balance: {self.balance}"


class WalletTransaction(models.Model):
    TRANSACTION_TYPES = (
        ("credit", "Credit"),
        ("debit", "Debit"),
    )

    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name="transactions")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.transaction_type.title()} - {self.amount} ({self.wallet.patient})"



