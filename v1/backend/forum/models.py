from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify

class ForumCategory(models.Model):
    """Catégories du forum (ex: Pièces moteur, Carrosserie, etc.)"""
    name = models.CharField(max_length=100, verbose_name="Nom")
    description = models.TextField(verbose_name="Description")
    icon = models.CharField(max_length=50, default="fa-comments", verbose_name="Icône FontAwesome")
    slug = models.SlugField(unique=True)
    order = models.IntegerField(default=0, verbose_name="Ordre d'affichage")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")

    class Meta:
        ordering = ['order', 'name']
        verbose_name = "Catégorie du forum"
        verbose_name_plural = "Catégories du forum"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('forum:category_detail', kwargs={'slug': self.slug})

    def get_topic_count(self):
        return self.topics.count()

    def get_latest_topic(self):
        return self.topics.order_by('-created_at').first()


class ForumTopic(models.Model):
    """Sujets de discussion créés par les utilisateurs"""
    title = models.CharField(max_length=200, verbose_name="Titre")
    content = models.TextField(verbose_name="Contenu")
    category = models.ForeignKey(ForumCategory, related_name='topics', on_delete=models.CASCADE, verbose_name="Catégorie")
    author = models.ForeignKey(User, related_name='forum_topics', on_delete=models.CASCADE, verbose_name="Auteur")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modifié le")
    slug = models.SlugField(unique=True)
    is_locked = models.BooleanField(default=False, verbose_name="Sujet verrouillé")
    is_pinned = models.BooleanField(default=False, verbose_name="Sujet épinglé")
    views = models.PositiveIntegerField(default=0, verbose_name="Vues")

    class Meta:
        ordering = ['-is_pinned', '-created_at']
        verbose_name = "Sujet du forum"
        verbose_name_plural = "Sujets du forum"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            # Ensure slug uniqueness
            counter = 1
            while ForumTopic.objects.filter(slug=self.slug).exists():
                self.slug = f"{slugify(self.title)}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('forum:topic_detail', kwargs={'slug': self.slug})

    def get_replies_count(self):
        return self.replies.count()

    def increment_view_count(self):
        self.views += 1
        self.save(update_fields=['views'])


class ForumReply(models.Model):
    """Réponses aux sujets du forum"""
    topic = models.ForeignKey(ForumTopic, related_name='replies', on_delete=models.CASCADE, verbose_name="Sujet")
    author = models.ForeignKey(User, related_name='forum_replies', on_delete=models.CASCADE, verbose_name="Auteur")
    content = models.TextField(verbose_name="Contenu")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modifié le")
    is_solution = models.BooleanField(default=False, verbose_name="Marqué comme solution")

    class Meta:
        ordering = ['created_at']
        verbose_name = "Réponse du forum"
        verbose_name_plural = "Réponses du forum"

    def __str__(self):
        return f"Réponse de {self.author.username} au sujet: {self.topic.title}"

    def get_absolute_url(self):
        return f"{self.topic.get_absolute_url()}#reply-{self.id}"
