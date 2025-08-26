from django.db import models
from django.contrib.auth.models import User


class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="patient_profile")

    # Extra patient info
    patient_id = models.CharField(max_length=20, unique=True)  # E-Card / Hospital ID
    gender_choices = [
        ("M", "Male"),
        ("F", "Female"),
        ("O", "Other"),
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

    def __str__(self):
        return f"{self.patient_id} - {self.user.get_full_name()}"
