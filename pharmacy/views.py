from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from patients.models import Prescription, PrescriptionItem
from .models import DispensedItem
from django.contrib.auth import authenticate, login, logout
from .models import DispensedItem, PharmacistProfile


def pharmacy_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            try:
                # make sure user is a pharmacist
                user.pharmacist_profile
                login(request, user)
                return redirect("pharmacy_dashboard")
            except PharmacistProfile.DoesNotExist:
                messages.error(request, "You are not authorized as a pharmacist.")
        else:
            messages.error(request, "Invalid username or password")

    return render(request, "login.html")

@login_required
def pharmacy_dashboard(request):
    prescriptions = Prescription.objects.all().order_by("-created_at")
    return render(request, "pharmacy-dashboard.html", {"prescriptions": prescriptions})

@login_required
def prescription_detail(request, pk):
    prescription = get_object_or_404(Prescription, pk=pk)
    dispensed_items = DispensedItem.objects.filter(prescription_item__prescription=prescription)
    return render(request, "prescription-detail.html", {
        "prescription": prescription,
        "dispensed_items": dispensed_items,
    })

@login_required
def dispense_item(request, item_id):
    item = get_object_or_404(PrescriptionItem, id=item_id)
    pharmacist = request.user.pharmacist_profile

    # Prevent double-dispensing
    if DispensedItem.objects.filter(prescription_item=item).exists():
        messages.warning(request, "This medicine has already been dispensed.")
    else:
        DispensedItem.objects.create(
            prescription_item=item,
            pharmacist=pharmacist,
            remarks=request.POST.get("remarks", "")
        )
        messages.success(request, f"{item.medicine_name} dispensed successfully!")

    return redirect("pharmacy_prescription_detail", pk=item.prescription.id)