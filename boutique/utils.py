# boutique/utils.py
from .models import Panier

def get_or_create_panier(user):
    panier, created = Panier.objects.get_or_create(utilisateur=user)
    return panier
