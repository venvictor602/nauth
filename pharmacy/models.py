from django.db import models

# Create your models here.
# pharmacy/models.py
from django.db import models
from patients.models import Prescription, PrescriptionItem
from django.contrib.auth.models import User

class PharmacistProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="pharmacist_profile")
    phone = models.CharField(max_length=20, blank=True)
    department = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Pharmacist: {self.user.get_full_name() or self.user.username}"

class DispensedItem(models.Model):
    prescription_item = models.OneToOneField(PrescriptionItem, on_delete=models.CASCADE)
    pharmacist = models.ForeignKey(PharmacistProfile, on_delete=models.CASCADE)
    dispensed_at = models.DateTimeField(auto_now_add=True)
    remarks = models.TextField(blank=True)

    def __str__(self):
        return f"{self.prescription_item.medicine_name} dispensed by {self.pharmacist}"
