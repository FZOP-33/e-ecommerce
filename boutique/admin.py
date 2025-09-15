from django.contrib import admin
from django.utils.html import format_html  # ✅ Import correct
from .models import (
    Categorie, Produit, Panier, LignePanier,
    Commande, LigneCommande, Paiement, Avis,
    AdresseLivraison
)

# Catégorie
@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ('nom', 'description')
    search_fields = ('nom',)

# Produit
@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    list_display = ('image_preview', 'nom', 'categorie', 'prix', 'stock', 'date_ajout')
    list_filter = ('categorie',)
    search_fields = ('nom', 'description')
    readonly_fields = ['image_preview']

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="80" height="80" style="object-fit:contain;border:1px solid #ccc;" />',
                obj.image.url
            )
        return "(Pas d'image)"
    image_preview.short_description = "Image"

# Adresse de Livraison
@admin.register(AdresseLivraison)
class AdresseLivraisonAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'nom_complet', 'telephone', 'ville', 'code_postal', 'pays')
    search_fields = ('nom_complet', 'telephone', 'ville', 'pays')

# Panier
@admin.register(Panier)
class PanierAdmin(admin.ModelAdmin):
    list_display = ('utilisateur',)

# Ligne Panier
@admin.register(LignePanier)
class LignePanierAdmin(admin.ModelAdmin):
    list_display = ('panier', 'produit', 'quantite')
    list_filter = ('produit',)

# Commande
class LigneCommandeInline(admin.TabularInline):
    model = LigneCommande
    extra = 0
    readonly_fields = ('produit', 'quantite', 'prix_unitaire')
    can_delete = False

@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    list_display = ('id', 'utilisateur', 'date_commande', 'est_payee', 'statut')
    list_filter = ('statut', 'est_payee')
    search_fields = ('utilisateur__username', 'id')
    inlines = [LigneCommandeInline]

# Paiement
@admin.register(Paiement)
class PaiementAdmin(admin.ModelAdmin):
    list_display = ('commande', 'montant', 'methode', 'date_paiement', 'statut')
    list_filter = ('methode', 'statut')
    search_fields = ('commande__id',)

# Avis
@admin.register(Avis)
class AvisAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'produit', 'note', 'date')
    list_filter = ('note',)
    search_fields = ('produit__nom', 'utilisateur__username')
