from django.db import models
from django.contrib.auth.models import User
from doctor.models import *
from django.core.exceptions import ValidationError
from django.conf import settings
from django.db.models import Sum
from num2words import num2words  # Install with: pip install num2words
from decimal import Decimal



class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="patient_profile")
    first_name = models.CharField(max_length=20, blank=True, null=True)
    last_name = models.CharField(max_length=20, blank=True, null=True)



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
    appointment = models.ForeignKey("Appointment", on_delete=models.SET_NULL, blank=True, null=True, related_name="prescriptions")

    title = models.CharField(max_length=100, blank=True, null=True)  # e.g. "Cardiology Prescription"
    department = models.CharField(max_length=100, blank=True, null=True)  # e.g. "Cardiology OP"
    consultation_type = models.CharField(max_length=50, blank=True, null=True)  # e.g. "Video" / "In-person"

    diagnosis = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    advice = models.TextField(blank=True, null=True)  # for "Advice" section
    follow_up_notes = models.TextField(blank=True, null=True)  # e.g. "Follow up after 3 months"
    follow_up_date = models.DateField(blank=True, null=True)  # optional structured follow-up date

    doctor_signature = models.ImageField(upload_to="doctor_signatures/", blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Prescription {self.id} for {self.patient.user.get_full_name()} by Dr. {self.doctor.user.get_full_name()}"


class PrescriptionItem(models.Model):
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name="items")
    
    medicine_name = models.CharField(max_length=100)
    dosage = models.CharField(max_length=50, help_text="e.g. 500mg, 1 tablet")
    frequency = models.CharField(max_length=50, help_text="e.g. 1-0-1, Twice a day")
    duration = models.CharField(max_length=50, help_text="e.g. 5 days, 1 month")
    timings = models.CharField(max_length=100, blank=True, null=True, help_text="e.g. Before meal, After meal")
    instructions = models.TextField(blank=True, null=True, help_text="Additional instructions")

    def __str__(self):
        return f"{self.medicine_name} - {self.dosage} for {self.prescription.patient.user.get_full_name()}"





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




class BaseAbstractModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True







class Invoice(BaseAbstractModel):
    number = models.CharField(max_length=50, unique=True, blank=True, null=True)
    patient = models.ForeignKey("Patient", on_delete=models.CASCADE, related_name="invoices")
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_in_words = models.CharField(max_length=255, blank=True, null=True)
    issued_on = models.DateField()
    due_date = models.DateField()

    status = models.CharField(
        max_length=20,
        choices=[
            ("draft", "Draft"),
            ("sent", "Sent"),
            ("paid", "Paid"),
            ("overdue", "Overdue"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
    )

    vat = models.DecimalField(max_digits=12, decimal_places=2, default=0)


    terms = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    signed_by = models.CharField(max_length=100, blank=True, null=True)
    signed_role = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        ordering = ["-issued_on"]

    def __str__(self):
        return f"Invoice {self.number} - {self.patient}"

    def save(self, *args, **kwargs):
        if not self.number:
            last_invoice = Invoice.objects.all().order_by("id").last()
            if last_invoice:
                last_number = int(last_invoice.number.replace("INV", ""))
                new_number = last_number + 1
            else:
                new_number = 1
            self.number = f"INV{str(new_number).zfill(4)}"
        super().save(*args, **kwargs)










class InvoiceItem(BaseAbstractModel):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="items")
    product_name = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    unit_cost = models.DecimalField(max_digits=12, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    amount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return f"{self.product_name} ({self.invoice.number})"

    def save(self, *args, **kwargs):
        self.amount = self.unit_cost * self.quantity
        super().save(*args, **kwargs)
        self.update_invoice_totals()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.update_invoice_totals()

    def update_invoice_totals(self):
        invoice = self.invoice

        # Get subtotal from all items
        subtotal = invoice.items.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

        # Add VAT if applicable
        total = subtotal + (invoice.vat or Decimal('0.00'))

        # Convert total to words in Naira
        naira_words = num2words(total, lang='en').replace("euro", "naira").replace("cents", "kobo").title()

        # Update invoice fields
        invoice.subtotal = subtotal
        invoice.total = total
        invoice.total_in_words = f"{naira_words} Only"
        invoice.save()



