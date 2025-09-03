from .models import *

def dashboard(request):
    # Default wallet balance
    wallet_balance = 0

    # Only access patient if the user is logged in and has a patient_profile
    if request.user.is_authenticated and hasattr(request.user, 'patient_profile'):
        patient = request.user.patient_profile
        wallet = getattr(patient, "wallet", None)
        wallet_balance = wallet.balance if wallet else 0

    return {
        "wallet_balance": wallet_balance,
    }


