from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from invoicing.models import Customer


class UserRegisterForm(UserCreationForm):
    """Formulaire d'inscription"""
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=100, required=True, label="Prénom")
    last_name = forms.CharField(max_length=100, required=True, label="Nom")

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Cette adresse email est déjà utilisée.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']  # Email comme username
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class UserUpdateForm(forms.ModelForm):
    """Formulaire de mise à jour du profil"""
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


class CustomerProfileForm(forms.ModelForm):
    """Formulaire du profil client"""
    class Meta:
        model = Customer
        fields = ['company', 'phone', 'address', 'city', 'postal_code', 'country']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }


class ContactForm(forms.Form):
    """Formulaire de contact"""
    name = forms.CharField(max_length=100, label="Nom")
    email = forms.EmailField(label="Email")
    subject = forms.CharField(max_length=200, label="Sujet")
    message = forms.CharField(widget=forms.Textarea(attrs={'rows': 5}), label="Message")


class ProductReviewForm(forms.Form):
    """Formulaire d'avis produit"""
    RATING_CHOICES = [(i, '★' * i) for i in range(1, 6)]
    
    rating = forms.ChoiceField(
        choices=RATING_CHOICES, 
        label="Votre note",
        widget=forms.RadioSelect(attrs={'class': 'rating-input'})
    )
    title = forms.CharField(
        max_length=100, 
        label="Titre de l'avis",
        widget=forms.TextInput(attrs={'placeholder': 'Résumez votre avis...'})
    )
    comment = forms.CharField(
        label="Votre avis",
        widget=forms.Textarea(attrs={'rows': 4, 'placeholder': 'Décrivez votre expérience...'})
    )


class AdvancedSearchForm(forms.Form):
    """Formulaire de recherche avancée"""
    q = forms.CharField(
        required=False, 
        label="Mots-clés",
        widget=forms.TextInput(attrs={'placeholder': 'Rechercher...'})
    )
    category = forms.ChoiceField(
        required=False, 
        label="Catégorie",
        choices=[('', 'Toutes les catégories')]
    )
    min_price = forms.DecimalField(
        required=False, 
        label="Prix minimum",
        min_value=0,
        widget=forms.NumberInput(attrs={'placeholder': 'Min'})
    )
    max_price = forms.DecimalField(
        required=False, 
        label="Prix maximum",
        min_value=0,
        widget=forms.NumberInput(attrs={'placeholder': 'Max'})
    )
    in_stock = forms.BooleanField(
        required=False, 
        label="En stock uniquement"
    )
    on_sale = forms.BooleanField(
        required=False, 
        label="En promotion"
    )
    min_rating = forms.ChoiceField(
        required=False,
        label="Note minimum",
        choices=[('', 'Toutes les notes'), ('4', '4★ et plus'), ('3', '3★ et plus'), ('2', '2★ et plus')]
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .models import Category
        categories = Category.objects.filter(is_active=True)
        self.fields['category'].choices = [('', 'Toutes les catégories')] + [
            (str(c.id), c.name) for c in categories
        ]

