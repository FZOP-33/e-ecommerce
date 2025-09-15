# forms.py
from django import forms
from django.contrib.auth.models import User
from .models import AdresseLivraison,MessageContact
from django.contrib.auth.forms import UserCreationForm



class InscriptionForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label="Email",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'exemple@mail.com'})
    )

    username = forms.CharField(
        required=True,
        label="Nom d'utilisateur",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Votre nom d’utilisateur'})
    )

    password1 = forms.CharField(
        required=True,
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Mot de passe'})
    )

    password2 = forms.CharField(
        required=True,
        label="Confirmation du mot de passe",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirmez le mot de passe'})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Cet email est déjà utilisé.")
        return email
        

class AdresseLivraisonForm(forms.ModelForm):
    class Meta:
        model = AdresseLivraison
        fields = ['nom_complet', 'telephone', 'adresse', 'ville', 'code_postal', 'pays']
        widgets = {
            'adresse': forms.Textarea(attrs={'rows':2, 'class':'form-control'}),
            'ville': forms.TextInput(attrs={'class':'form-control'}),
            'code_postal': forms.TextInput(attrs={'class':'form-control'}),
            'pays': forms.TextInput(attrs={'class':'form-control'}),
            'nom_complet': forms.TextInput(attrs={'class':'form-control'}),
            'telephone': forms.TextInput(attrs={'class':'form-control'}),
        }

class ContactForm(forms.ModelForm):
    class Meta:
        model = MessageContact
        fields = ['nom', 'email', 'sujet', 'message']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Votre nom'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Votre email'}),
            'sujet': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Sujet'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Votre message'}),
        }