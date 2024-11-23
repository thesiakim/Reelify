from django.apps import apps
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from .utils import invalidate_user_cache

Review = apps.get_model('movies', 'Review')
Movie = apps.get_model('movies', 'Movie')

@receiver(m2m_changed, sender=Review.likes.through)
def review_likes_changed(sender, instance, **kwargs):
    invalidate_user_cache(instance.user.id)

@receiver(m2m_changed, sender=Movie.likes.through)
def movie_likes_changed(sender, instance, **kwargs):
    for user in instance.likes.all():
        invalidate_user_cache(user.id)