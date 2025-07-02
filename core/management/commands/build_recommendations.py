from django.core.management.base import BaseCommand
from core.AIModel.recommender import BookRecommender

class Command(BaseCommand):
    help = "Rebuild book vector embeddings"

    def handle(self, *args, **options):
        print("🔄 Rebuilding book embeddings...")
        BookRecommender().build()
        print("✅ Embeddings updated.")
