from django.http import Http404, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q, F, Sum
from django.urls import reverse

import requests
import stripe

from ecommerce import settings
from .models import (
    AdresseLivraison, Avis, Commande, LigneCommande, Paiement,
    Produit, Panier, LignePanier, Categorie
)
from .forms import AdresseLivraisonForm, ContactForm, InscriptionForm
from .utils import get_or_create_panier

from boutique import models

def accueil(request):
    produits = Produit.objects.select_related('categorie').all()

    # Filtre par catégorie
    categorie_id = request.GET.get('categorie')
    if categorie_id:
        try:
            categorie_id = int(categorie_id)
            produits = produits.filter(categorie_id=categorie_id)
        except ValueError:
            pass  # ignore si catégorie invalide

    # Recherche par mot-clé
    q = request.GET.get('q')
    if q:
        produits = produits.filter(
            Q(nom__icontains=q) |
            Q(description__icontains=q)
        )

    # Tri des produits
    sort = request.GET.get('sort')
    if sort == "prix_asc":
        produits = produits.order_by('prix')
    elif sort == "prix_desc":
        produits = produits.order_by('-prix')
    elif sort == "nouveaux":
        produits = produits.order_by('-id')

    # Total items pour badge (corrigé pour éviter None)
    total_items = 0
    if request.user.is_authenticated:
        panier = get_or_create_panier(request.user)
        total_items = panier.lignes.aggregate(total=Sum('quantite'))['total']
        if total_items is None:
            total_items = 0

    context = {
        'produits': produits,
        'categories': Categorie.objects.all(),
        'categorie_active': int(categorie_id) if categorie_id else None,
        'tri_actif': sort or '',
        'q': q or '',
        'total_items': total_items,  # pour badge initial
    }

    # Si requête AJAX pour le badge uniquement
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'total_items': total_items})

    return render(request, 'accueil.html', context)



def detail_produit(request, produit_id):
    produit = get_object_or_404(Produit, id=produit_id)
    produits_similaires = Produit.objects.filter(categorie=produit.categorie).exclude(id=produit.id)[:4]
    avis = Avis.objects.filter(produit=produit).order_by('-date')[:5]  # les 5 derniers avis

    return render(request, 'boutique/detail_produit.html', {
        'produit': produit,
        'produits_similaires': produits_similaires,
        'avis': avis
    })



def poster_avis(request, produit_id):
    produit = get_object_or_404(Produit, id=produit_id)
    if request.method == "POST" and request.user.is_authenticated:
        note = int(request.POST.get('note'))
        commentaire = request.POST.get('commentaire')
        Avis.objects.create(utilisateur=request.user, produit=produit, note=note, commentaire=commentaire)
    return redirect('detail_produit', produit_id=produit.id)

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>A REVOIR AVEC PRECISION>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

# ✅ Fonction pour récupérer ou créer un panier lié à l'utilisateur
def get_or_create_panier(user):
    panier, created = Panier.objects.get_or_create(utilisateur=user)
    return panier



@login_required(login_url='login')
def ajouter_au_panier(request, produit_id):
    produit = get_object_or_404(Produit, id=produit_id)
    panier = get_or_create_panier(request.user)

    # On ajoute sans incrémentation
    LignePanier.objects.get_or_create(panier=panier, produit=produit)

    # ✅ Redirection directe vers le panier
    return redirect('panier')



# ✅ Ajouter un produit au panier
@login_required(login_url='login')
def ajouter_au_panier_ajax(request, produit_id):
    if request.method == "POST":
        produit = get_object_or_404(Produit, id=produit_id)
        panier = get_or_create_panier(request.user)

        ligne, created = LignePanier.objects.get_or_create(panier=panier, produit=produit)

        if not created:
            ligne.quantite += 1
            ligne.save()

        # Compteur total du panier
        total_items = sum(l.quantite for l in panier.lignes.all())

        return JsonResponse({
            "success": True,
            "message": f"{produit.nom} ajouté au panier !",
            "total_items": total_items,
        })
    return JsonResponse({"success": False}, status=400)


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>A REVOIR AVEC PRECISION###############
# ✅ Afficher le panier
@login_required(login_url='login')
def panier_view(request):
    panier = get_or_create_panier(request.user)
    items = panier.lignes.all()
    total = panier.get_total()

    context = {
        "items": items,
        "total": total,
    }
    return render(request, "panier.html", context)


def register_view(request):
    if request.method == 'POST':
        form = InscriptionForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Connexion automatique de l'utilisateur
            login(request, user)
            messages.success(request, f"Bienvenue {user.username}, votre compte a été créé et vous êtes connecté 🎉.")
            return redirect('accueil')  # Redirige vers accueil ou panier directement
    else:
        form = InscriptionForm()
    return render(request, 'register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, "Connexion réussie ✅.")
            return redirect('accueil')  # Redirige vers accueil ou panier
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect ❌.")

    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    messages.info(request, "Vous êtes déconnecté 👋.")
    return redirect('login')



# ✅ Mettre à jour la quantité
@login_required(login_url='login')
def maj_quantite(request, ligne_id):
    """
    Met à jour la quantité d'une ligne de panier identifiée par ligne_id.
    Reçoit POST {'quantite': <int>} et redirige vers la page panier.
    """
    panier = get_or_create_panier(request.user)
    ligne = get_object_or_404(LignePanier, id=ligne_id, panier=panier)

    if request.method == 'POST':
        q = request.POST.get('quantite', '')
        try:
            quantite = int(q)
        except (ValueError, TypeError):
            messages.error(request, "Quantité invalide.")
            return redirect('panier')

        # si quantité <= 0 => on supprime la ligne
        if quantite <= 0:
            ligne.delete()
            messages.info(request, "Produit supprimé du panier.")
            return redirect('panier')

        # vérifier le stock
        if ligne.produit.stock is not None and quantite > ligne.produit.stock:
            messages.error(request, f"Quantité demandée ({quantite}) supérieure au stock disponible ({ligne.produit.stock}).")
            return redirect('panier')

        # Mise à jour
        ligne.quantite = quantite
        ligne.save()
        messages.success(request, "Quantité mise à jour.")
    # Pour GET, on redirige quand même vers le panier
    return redirect('panier')


# ✅ Supprimer un produit du panier
@login_required(login_url='login')
def supprimer_du_panier(request, ligne_id):
    """
    Option : on accepte POST pour supprimer (plus sûr), mais on peut accepter GET aussi.
    Ici on accepte POST et GET pour compatibilité.
    """
    panier = get_or_create_panier(request.user)
    ligne = get_object_or_404(LignePanier, id=ligne_id, panier=panier)

    # Si POST demandé, supprimer. Si GET (lien), on peut aussi supprimer après confirmation.
    if request.method == 'POST' or request.method == 'GET':
        ligne.delete()
        messages.success(request, "Produit supprimé du panier.")

    return redirect('panier')


#>>>>>>>>>>>>>>>>>>><  commande ++++++++++++++++++++++++

@login_required
def passer_commande(request):
    panier = get_object_or_404(Panier, utilisateur=request.user)
    items = panier.lignes.all()
    total = panier.get_total()

    # Gestion ajout adresse
    if request.method == "POST" and "add_adresse" in request.POST:
        form = AdresseLivraisonForm(request.POST)
        if form.is_valid():
            adresse = form.save(commit=False)
            adresse.utilisateur = request.user
            adresse.save()
            return redirect('passer_commande')
    else:
        form = AdresseLivraisonForm()

    adresses = AdresseLivraison.objects.filter(utilisateur=request.user)

    context = {
        "items": items,
        "total": total,
        "adresses": adresses,
        "form": form
    }
    return render(request, "boutique/passer_commande.html", context)


@login_required
def confirmer_commande(request, adresse_id):
    panier = get_object_or_404(Panier, utilisateur=request.user)
    adresse = get_object_or_404(AdresseLivraison, id=adresse_id, utilisateur=request.user)
    items = panier.lignes.all()
    if not items:
        return redirect("panier")

    # Création commande
    commande = Commande.objects.create(
        utilisateur=request.user,
        adresse_livraison=adresse
    )
    for item in items:
        commande.lignes.create(
            produit=item.produit,
            quantite=item.quantite,
            prix_unitaire=item.produit.prix_promo if item.produit.prix_promo else item.produit.prix
        )

    # 👉 on NE vide PAS encore le panier
    return redirect('paiement', commande_id=commande.id)




stripe.api_key = settings.STRIPE_SECRET_KEY  # Clé secrète Stripe

@login_required
def paiement(request, commande_id):
    commande = get_object_or_404(Commande, id=commande_id, utilisateur=request.user)
    total = int(sum([ligne.get_total() for ligne in commande.lignes.all()]))

    # 🔥 Numéros WhatsApp + message pré-rempli
    raw_numbers = ["+33 6 65 74 33 08", "+223 94 22 81 38"]
    whatsapp_numbers = [num.replace(" ", "").replace("+", "") for num in raw_numbers]
    whatsapp_message = f"Informer nous avant de payer par Orange Money. Merci 🙏.\nCommande #{commande.id}, Montant : {total} FCFA"

    if request.method == "POST":
        methode = request.POST.get("methode")

        # 🚀 Stripe → paiement direct
        if methode == "carte":
            try:
                session = stripe.checkout.Session.create(
                    payment_method_types=['card'],
                    line_items=[{
                        'price_data': {
                            'currency': 'xof',
                            'unit_amount': int(total),
                            'product_data': {'name': f'Commande #{commande.id}'},
                        },
                        'quantity': 1,
                    }],
                    mode='payment',
                    success_url=request.build_absolute_uri(
                        reverse("paiement_success", args=[commande.id])
                    ),
                    cancel_url=request.build_absolute_uri(
                        reverse("confirmation_commande", args=[commande.id])
                    ),
                    metadata={'commande_id': commande.id}
                )
                return redirect(session.url, code=303)

            except Exception as e:
                return render(request, "boutique/paiement.html", {
                    "commande": commande,
                    "total": total,
                    "error": f"Erreur Stripe: {str(e)}",
                    "whatsapp_numbers": whatsapp_numbers,
                    "whatsapp_message": whatsapp_message
                })

        # 🚀 CinetPay → paiement direct
        elif methode == "cinetpay":
            url = "https://sandbox.cinetpay.com/v1/payment"
            data = {
                "apikey": settings.CINETPAY_API_KEY,
                "site_id": settings.CINETPAY_SITE_ID,
                "transaction_id": f"CMD{commande.id}",
                "amount": total,
                "currency": "XOF",
                "description": f"Paiement commande #{commande.id}",
                "return_url": request.build_absolute_uri(
                    reverse("paiement_success", args=[commande.id])
                ),
                "notify_url": request.build_absolute_uri('/cinetpay-webhook/')
            }
            try:
                response = requests.post(url, json=data, timeout=10)
                result = response.json()
                payment_url = result.get("payment_url")
                if payment_url:
                    return redirect(payment_url)
                else:
                    return render(request, "boutique/paiement.html", {
                        "commande": commande,
                        "total": total,
                        "error": "Impossible de créer la session CinetPay. Réponse: " + str(result),
                        "whatsapp_numbers": whatsapp_numbers,
                        "whatsapp_message": whatsapp_message
                    })
            except Exception as e:
                return render(request, "boutique/paiement.html", {
                    "commande": commande,
                    "total": total,
                    "error": f"Erreur CinetPay: {str(e)}",
                    "whatsapp_numbers": whatsapp_numbers,
                    "whatsapp_message": whatsapp_message
                })

        # 🚀 WhatsApp (confirmation obligatoire)
        elif methode == "whatsapp":
            confirme = request.POST.get("confirme")
            if not confirme:
                return render(request, "boutique/paiement.html", {
                    "commande": commande,
                    "total": total,
                    "error": "⚠️ Vous devez d’abord discuter sur WhatsApp puis cocher la case.",
                    "whatsapp_numbers": whatsapp_numbers,
                    "whatsapp_message": whatsapp_message
                })

            # Créer un paiement WhatsApp
            Paiement.objects.create(
                commande=commande,
                montant=total,
                methode="orange_money_whatsapp"
            )
            commande.est_payee = True
            commande.statut = "en_attente"
            commande.save()

            # Vider le panier
            panier = get_object_or_404(Panier, utilisateur=request.user)
            panier.lignes.all().delete()

            return redirect("confirmation_commande", commande_id=commande.id)

    # GET → affichage du template
    return render(request, "boutique/paiement.html", {
        "commande": commande,
        "total": total,
        "whatsapp_numbers": whatsapp_numbers,
        "whatsapp_message": whatsapp_message
    })


@login_required
def paiement_success(request, commande_id):
    """
    Vue appelée après succès Stripe ou CinetPay
    """
    commande = get_object_or_404(Commande, id=commande_id, utilisateur=request.user)
    total = sum([ligne.get_total() for ligne in commande.lignes.all()])

    Paiement.objects.create(
        commande=commande,
        montant=total,
        methode="en_ligne"
    )

    commande.est_payee = True
    commande.statut = "en_attente"
    commande.save()

    panier = get_object_or_404(Panier, utilisateur=request.user)
    panier.lignes.all().delete()

    return redirect("confirmation_commande", commande_id=commande.id)








@login_required
def confirmation_commande(request, commande_id=None, id=None, pk=None):
    cid = commande_id or id or pk
    if cid is None:
        raise Http404("Commande introuvable")
    commande = get_object_or_404(Commande, id=cid, utilisateur=request.user)
    total = sum(l.get_total() for l in commande.lignes.all())
    return render(request, "boutique/confirmation_commande.html", {
        "commande": commande,
        "total": total,
    })










def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Votre message a été envoyé avec succès !")
            return redirect('contact')
    else:
        form = ContactForm()
    return render(request, 'contact.html', {'form': form})