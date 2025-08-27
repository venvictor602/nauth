from django.contrib import admin
from .models import *

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ("patient_id", "user", "gender", "date_of_birth", "phone_number", "is_inpatient")
    search_fields = ("patient_id", "user__username", "user__first_name", "user__last_name", "phone_number")
    list_filter = ("gender", "is_inpatient")


admin.site.register(Appointment)

admin.site.register(Doctor)

admin.site.register(Prescription)

admin.site.register(PrescriptionItem)