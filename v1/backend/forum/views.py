from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count
from .models import ForumCategory, ForumTopic, ForumReply
from .forms import TopicForm, ReplyForm
from django.urls import reverse
from django.utils import timezone

def forum_home(request):
    """Page d'accueil du forum avec la liste des catégories"""
    categories = ForumCategory.objects.all().annotate(topics_count=Count('topics'))

    # Calculer le nombre total de sujets directement dans la vue
    total_topics = ForumTopic.objects.count()

    # Pour chaque catégorie, récupérer le dernier sujet
    for category in categories:
        category.latest_topic = category.topics.order_by('-created_at').first()

    return render(request, 'forum/forum_home.html', {
        'categories': categories,
        'total_topics': total_topics,  # Passer le total à la template
        'active_forum': True  # Pour marquer l'onglet forum comme actif dans la navigation
    })

def category_detail(request, slug):
    """Liste des sujets d'une catégorie"""
    category = get_object_or_404(ForumCategory, slug=slug)

    # Récupérer tous les sujets de la catégorie triés par épinglés et date de création
    topics = category.topics.all().annotate(replies_count=Count('replies'))

    # Séparer les sujets épinglés des sujets normaux
    pinned_topics = topics.filter(is_pinned=True)
    regular_topics = topics.filter(is_pinned=False)

    return render(request, 'forum/category_detail.html', {
        'category': category,
        'pinned_topics': pinned_topics,
        'regular_topics': regular_topics,
        'active_forum': True
    })

def topic_detail(request, slug):
    """Détail d'un sujet avec ses réponses"""
    topic = get_object_or_404(ForumTopic, slug=slug)

    # Incrémenter le compteur de vues
    topic.increment_view_count()

    # Récupérer toutes les réponses au sujet
    replies = topic.replies.all()

    # Vérifier si un reply est marqué comme solution
    solution = replies.filter(is_solution=True).first()

    # Formulaire pour ajouter une réponse
    reply_form = ReplyForm()

    return render(request, 'forum/topic_detail.html', {
        'topic': topic,
        'replies': replies,
        'solution': solution,
        'reply_form': reply_form,
        'active_forum': True
    })

@login_required
def create_topic(request, category_slug=None):
    """Créer un nouveau sujet"""
    initial = {}
    if category_slug:
        category = get_object_or_404(ForumCategory, slug=category_slug)
        initial['category'] = category

    if request.method == 'POST':
        form = TopicForm(request.POST)
        if form.is_valid():
            topic = form.save(commit=False)
            topic.author = request.user
            topic.save()
            messages.success(request, "Votre sujet a été créé avec succès.")
            return redirect(topic.get_absolute_url())
    else:
        form = TopicForm(initial=initial)

    return render(request, 'forum/topic_form.html', {
        'form': form,
        'is_new': True,
        'active_forum': True
    })

@login_required
def edit_topic(request, slug):
    """Modifier un sujet existant"""
    topic = get_object_or_404(ForumTopic, slug=slug)

    # Vérifier que l'utilisateur est l'auteur du sujet
    if request.user != topic.author:
        messages.error(request, "Vous n'avez pas l'autorisation de modifier ce sujet.")
        return redirect(topic.get_absolute_url())

    if request.method == 'POST':
        form = TopicForm(request.POST, instance=topic)
        if form.is_valid():
            form.save()
            messages.success(request, "Votre sujet a été modifié avec succès.")
            return redirect(topic.get_absolute_url())
    else:
        form = TopicForm(instance=topic)

    return render(request, 'forum/topic_form.html', {
        'form': form,
        'topic': topic,
        'is_new': False,
        'active_forum': True
    })

@login_required
def create_reply(request, topic_slug):
    """Ajouter une réponse à un sujet"""
    topic = get_object_or_404(ForumTopic, slug=topic_slug)

    # Vérifier si le sujet est verrouillé
    if topic.is_locked:
        messages.error(request, "Ce sujet est verrouillé. Vous ne pouvez pas y répondre.")
        return redirect(topic.get_absolute_url())

    if request.method == 'POST':
        form = ReplyForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.topic = topic
            reply.author = request.user
            reply.save()

            # Si la requête est AJAX, renvoyer une réponse JSON
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'reply_id': reply.id,
                    'content': reply.content,
                    'author': reply.author.get_full_name() or reply.author.username,
                    'created_at': reply.created_at.strftime('%d/%m/%Y %H:%M'),
                })

            messages.success(request, "Votre réponse a été ajoutée avec succès.")
            return redirect(f"{topic.get_absolute_url()}#reply-{reply.id}")

    # Si ce n'est pas un POST, rediriger vers la page du sujet
    return redirect(topic.get_absolute_url())

@login_required
def mark_solution(request, reply_id):
    """Marquer une réponse comme solution"""
    reply = get_object_or_404(ForumReply, id=reply_id)
    topic = reply.topic

    # Vérifier que l'utilisateur est l'auteur du sujet
    if request.user != topic.author:
        messages.error(request, "Seul l'auteur du sujet peut marquer une réponse comme solution.")
        return redirect(topic.get_absolute_url())

    # Effacer l'ancienne solution si elle existe
    ForumReply.objects.filter(topic=topic, is_solution=True).update(is_solution=False)

    # Marquer cette réponse comme solution
    reply.is_solution = True
    reply.save()

    messages.success(request, "La réponse a été marquée comme solution.")
    return redirect(f"{topic.get_absolute_url()}#reply-{reply.id}")
