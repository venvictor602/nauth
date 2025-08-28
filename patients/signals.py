from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import *
from doctor.models import *
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.db import transaction
from decimal import Decimal


@receiver(post_save, sender=Appointment)
def log_appointment_activity(sender, instance, created, **kwargs):
    if created:
        fee = Decimal(instance.doctor.fee or "0")  # convert fee safely to Decimal
        wallet = instance.patient.wallet  

        if wallet.balance < fee:
            raise ValidationError(
                [f"Insufficient wallet balance to book this appointment. Required: {fee}, Available: {wallet.balance}"]
            )

        # Deduct fee
        wallet.balance -= fee
        wallet.save()

        # Log transaction
        WalletTransaction.objects.create(
            wallet=wallet,
            amount=fee,
            transaction_type="debit",
            description=f"Appointment fee for Dr. {instance.doctor}"
        )

        # Patient activity
        PatientActivity.objects.create(
            patient=instance.patient,
            category="appointment",
            title=f"Appointment with {instance.doctor}",
            description=f"Reason: {instance.reason}",
            created_by=getattr(instance.doctor, "user", None)
        )


@receiver(post_save, sender=Prescription)
def log_prescription_activity(sender, instance, created, **kwargs):
    if created:  # log new prescription
        PatientActivity.objects.create(
            patient=instance.patient,
            category="prescription",
            title=instance.title,
            description="New prescription issued.",
            created_by=getattr(instance.doctor, "user", None)
        )



@receiver(post_save, sender=Patient)
def create_wallet_for_patient(sender, instance, created, **kwargs):
    if created:
        Wallet.objects.create(patient=instance)

