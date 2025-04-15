from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import UserProfile, SignupRequest, Newsletter

class SignupRequestForm(forms.ModelForm):
    first_name = forms.CharField(max_length=100, required=True, label='Prénom')
    last_name = forms.CharField(max_length=100, required=True, label='Nom')
    email = forms.EmailField(required=True, label='Email')
    username = forms.CharField(max_length=150, required=True, label="Nom d'utilisateur")

    # Add password fields
    password = forms.CharField(
        widget=forms.PasswordInput,
        required=True,
        label="Mot de passe",
        help_text="Votre mot de passe doit contenir au moins 8 caractères."
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput,
        required=True,
        label="Confirmer le mot de passe"
    )

    class Meta:
        model = SignupRequest
        fields = ('first_name', 'last_name', 'email', 'username')

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Cet email est déjà utilisé.")
        if SignupRequest.objects.filter(email=email, is_approved=False, is_rejected=False).exists():
            raise forms.ValidationError("Une demande avec cet email est déjà en attente d'approbation.")
        return email

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Ce nom d'utilisateur est déjà pris.")
        if SignupRequest.objects.filter(username=username, is_approved=False, is_rejected=False).exists():
            raise forms.ValidationError("Une demande avec ce nom d'utilisateur est déjà en attente d'approbation.")
        return username

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password:
            validate_password(password)
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', "Les mots de passe ne correspondent pas.")

        return cleaned_data

class UserProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=100, required=True, label='Prénom')
    last_name = forms.CharField(max_length=100, required=True, label='Nom')
    email = forms.EmailField(required=True, label='Email')
    # Nouvelles options pour bannière
    banner_color = forms.CharField(
        max_length=20,
        required=False,
        label="Couleur de bannière",
        widget=forms.TextInput(attrs={'type': 'color', 'class': 'form-color'})
    )

    class Meta:
        model = UserProfile
        fields = (
            'profile_image', 'bio', 'instagram', 'facebook',
            'twitter', 'banner_image', 'banner_color'
        )
        labels = {
            'profile_image': 'Photo de profil',
            'bio': 'Biographie',
            'instagram': 'Instagram',
            'facebook': 'Facebook',
            'twitter': 'Twitter',
            'banner_image': 'Image de bannière',
        }
        help_texts = {
            'banner_image': 'La bannière sera examinée par un administrateur avant d\'être affichée.',
            'banner_color': 'Vous pouvez choisir une couleur à utiliser si vous n\'avez pas d\'image de bannière.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email

    def save(self, commit=True):
        profile = super().save(commit=False)

        # Si la bannière est modifiée, elle doit être réapprouvée
        if 'banner_image' in self.changed_data or 'banner_color' in self.changed_data:
            profile.banner_approved = False

        # Update the related User model fields
        user = profile.user
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        user.save()

        if commit:
            profile.save()

        return profile

class NewsletterForm(forms.ModelForm):
    class Meta:
        model = Newsletter
        fields = ('email',)
        labels = {
            'email': 'Email'
        }
