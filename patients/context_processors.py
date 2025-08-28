from .models import *

def dashboard(request):
    patient = request.user.patient_profile

    wallet = getattr(patient, "wallet", None)
    wallet_balance = wallet.balance if wallet else 0

    return {
        "wallet_balance": wallet_balance,  
    }

