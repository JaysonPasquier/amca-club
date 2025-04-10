from django import forms
from .models import ForumTopic, ForumReply

class TopicForm(forms.ModelForm):
    """Formulaire de création/édition de sujet"""

    class Meta:
        model = ForumTopic
        fields = ['title', 'content', 'category']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Titre du sujet'}),
            'content': forms.Textarea(attrs={'class': 'form-input', 'placeholder': 'Décrivez votre question ou sujet en détail...', 'rows': 8}),
            'category': forms.Select(attrs={'class': 'form-input'}),
        }
        labels = {
            'title': 'Titre',
            'content': 'Contenu',
            'category': 'Catégorie',
        }

class ReplyForm(forms.ModelForm):
    """Formulaire de réponse à un sujet"""

    class Meta:
        model = ForumReply
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-input', 'placeholder': 'Votre réponse...', 'rows': 5}),
        }
        labels = {
            'content': '',
        }
