from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from core.models import *
from core.AIModel.recommender import BookRecommender
import os

@receiver(post_save, sender=Book)
def update_vectors(sender, instance, created, **kwargs):
    if created:
        print(f"📘 Book '{instance.title}' saved — Skipping embedding update (handled manually)")


@receiver(post_save, sender=Audio_book)
def generate_preview(sender, instance, created, **kwargs):
    if not instance.genre:
        genre, _ = Genre.objects.get_or_create(name='Audio', defaults={
            'description': 'Audio books genre',
            'genreBooks': 0
        })
        instance.genre = genre
        instance.save(update_fields=['genre'])