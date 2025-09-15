from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.accueil, name='accueil'),
    path('produit/<int:produit_id>/', views.detail_produit, name='detail_produit'),
    path('produit/<int:produit_id>/poster-avis/', views.poster_avis, name='poster_avis'),  # poster un avis
    
    path("panier/", views.panier_view, name="panier"), # affichage du panier
    path('ajouter_au_panier/<int:produit_id>/', views.ajouter_au_panier, name='ajouter_au_panier'),
    path("ajouter-au-panier/<int:produit_id>/ajax/", views.ajouter_au_panier_ajax, name="ajouter_au_panier_ajax"),
    path("panier/supprimer/<int:ligne_id>/", views.supprimer_du_panier, name="supprimer_du_panier"),
    path("panier/maj/<int:ligne_id>/", views.maj_quantite, name="maj_quantite"),

    path('passer_commande/', views.passer_commande, name='passer_commande'),
    path('confirmer_commande/<int:adresse_id>/', views.confirmer_commande, name='confirmer_commande'),
    path('paiement/<int:commande_id>/', views.paiement, name='paiement'),
    path('confirmation_commande/<int:commande_id>/', views.confirmation_commande, name='confirmation_commande'),
    path('paiement-success/<int:commande_id>/', views.paiement_success, name='paiement_success'),
    #path('paiement-whatsapp/<int:commande_id>/', views.paiement_whatsapp, name='paiement_whatsapp'),
    path('contact/', views.contact, name='contact'),

    
    
    
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

]
