# context_processors.py
from .models import Categorie,Panier

def categories_processor(request):
    return {'categories': Categorie.objects.all()}




from .models import Panier

def panier_info(request):
    if request.user.is_authenticated:
        panier, created = Panier.objects.get_or_create(utilisateur=request.user)
        total_items = panier.get_item_count()
    else:
        total_items = 0

    return {
        'panier_count': total_items
    }
