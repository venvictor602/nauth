# pharmacy/admin.py
from django.contrib import admin
from .models import PharmacistProfile, DispensedItem

@admin.register(PharmacistProfile)
class PharmacistProfileAdmin(admin.ModelAdmin):
    list_display = ("user",  "phone")
    search_fields = ("user__username", "user__first_name", "user__last_name")


@admin.register(DispensedItem)
class DispensedItemAdmin(admin.ModelAdmin):
    list_display = ("prescription_item", "pharmacist", "dispensed_at", "remarks")
    search_fields = ("prescription_item__medicine_name", "pharmacist__user__username")
    list_filter = ("dispensed_at",)
