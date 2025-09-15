from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User

# Catégories de produits
class Categorie(models.Model):
    nom = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.nom

# Produits en vente
class Produit(models.Model):
    nom = models.CharField(max_length=255)
    description = models.TextField()
    prix = models.DecimalField(max_digits=10, decimal_places=0)
    stock = models.PositiveIntegerField()
    image = models.ImageField(upload_to='produits/')
    categorie = models.ForeignKey(Categorie, on_delete=models.CASCADE)
    date_ajout = models.DateTimeField(auto_now_add=True)
    prix_promo = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)

    def __str__(self):
        return self.nom

# Adresse de livraison
class AdresseLivraison(models.Model):
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE)
    nom_complet = models.CharField(max_length=150, null=True, blank=True) 
    telephone = models.CharField(max_length=20, null=True, blank=True)    
    adresse = models.TextField()
    ville = models.CharField(max_length=100)
    code_postal = models.CharField(max_length=10)
    pays = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.nom_complet} ({self.utilisateur.username}) - {self.adresse}"

# Panier
class Panier(models.Model):
    utilisateur = models.OneToOneField(User, on_delete=models.CASCADE, related_name="panier")

    def __str__(self):
        return f"Panier de {self.utilisateur.username}"

    def get_total(self):
        return sum([ligne.get_total() for ligne in self.lignes.all()])
    
    def get_item_count(self):
        return sum([ligne.quantite for ligne in self.lignes.all()])


# Éléments du panier
class LignePanier(models.Model):
    panier = models.ForeignKey(Panier, on_delete=models.CASCADE, related_name='lignes')
    produit = models.ForeignKey('Produit', on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantite} x {self.produit.nom}"

    def get_total(self):
        prix_unitaire = self.produit.prix_promo if self.produit.prix_promo else self.produit.prix
        return prix_unitaire * self.quantite

# Commandes
class Commande(models.Model):
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE)
    adresse_livraison = models.ForeignKey(AdresseLivraison, on_delete=models.SET_NULL, null=True)
    date_commande = models.DateTimeField(auto_now_add=True)
    est_payee = models.BooleanField(default=False)
    statut = models.CharField(max_length=100, choices=[
        ("en_attente", "En attente"),
        ("expediee", "Expédiée"),
        ("livree", "Livrée"),
        ("annulee", "Annulée")
    ], default="en_attente")

    def __str__(self):
        return f"Commande {self.id} - {self.utilisateur.username}"

# Détail des produits commandés
class LigneCommande(models.Model):
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE, related_name='lignes')
    produit = models.ForeignKey(Produit, on_delete=models.SET_NULL, null=True)
    quantite = models.PositiveIntegerField()
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantite} x {self.produit.nom}"

    def get_total(self):
        return self.quantite * self.prix_unitaire
    

# Paiement
class Paiement(models.Model):
    commande = models.OneToOneField(Commande, on_delete=models.CASCADE)
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    date_paiement = models.DateTimeField(auto_now_add=True)
    methode = models.CharField(max_length=50, choices=[
        ("carte", "Carte bancaire"),
        ("cinetpay", "CinetPay"),
        ("whatsapp", "Orange Money via WhatsApp"),
    ])
    statut = models.CharField(max_length=50, default="réussi")

    def __str__(self):
        return f"Paiement de {self.montant} FCFA - {self.methode}"



# Avis client
class Avis(models.Model):
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE)
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    note = models.IntegerField()
    commentaire = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Avis de {self.utilisateur.username} sur {self.produit.nom}"

class MessageContact(models.Model):
    nom = models.CharField(max_length=150)
    email = models.EmailField()
    sujet = models.CharField(max_length=200)
    message = models.TextField()
    date_envoi = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nom} - {self.sujet}"