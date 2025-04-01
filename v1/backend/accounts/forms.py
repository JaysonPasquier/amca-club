from django import forms
from django.contrib.auth.models import User
from .models import UserProfile, SignupRequest, Newsletter

class SignupRequestForm(forms.ModelForm):
    first_name = forms.CharField(max_length=100, required=True, label='Prénom')
    last_name = forms.CharField(max_length=100, required=True, label='Nom')
    email = forms.EmailField(required=True, label='Email')
    username = forms.CharField(max_length=150, required=True, label="Nom d'utilisateur")

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

class UserProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=100, required=True, label='Prénom')
    last_name = forms.CharField(max_length=100, required=True, label='Nom')
    email = forms.EmailField(required=True, label='Email')

    class Meta:
        model = UserProfile
        fields = ('profile_image', 'instagram', 'facebook', 'twitter')
        labels = {
            'profile_image': 'Photo de profil',
            'instagram': 'Instagram',
            'facebook': 'Facebook',
            'twitter': 'Twitter'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email

    def save(self, commit=True):
        profile = super().save(commit=False)

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
