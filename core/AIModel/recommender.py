from sentence_transformers import SentenceTransformer, util
from core.models import Book
import torch
import os
import pickle

class BookRecommender:
    def __init__(self):
        self.model_name = "all-MiniLM-L6-v2"
        self.model_path = os.path.join("core", "AIModel", self.model_name)
        self.vector_file = os.path.join("core", "vector_cache.pkl")

        # Ensure model is available locally
        self.model = self._load_or_download_model()

        self.book_texts = []
        self.book_slugs = []
        self.book_embeddings = None

        if os.path.exists(self.vector_file):
            self._load_embeddings()
        else:
            self._build_embeddings()

    def _load_or_download_model(self):
        """
        Loads model from local path or downloads it once and saves locally.
        """
        if os.path.exists(self.model_path):
            print(f"✅ Loading local model from {self.model_path}")
            return SentenceTransformer(self.model_path)
        else:
            print("📥 Downloading model from HuggingFace and caching it...")
            model = SentenceTransformer(self.model_name)
            model.save(self.model_path)
            return model

    def _build_embeddings(self):
        print("🔄 Building embeddings from book database...")
        books = Book.objects.all()
        self.book_slugs = [b.slug for b in books]
        self.book_texts = [f"{b.title} {b.description}" for b in books]
        self.book_embeddings = self.model.encode(self.book_texts, convert_to_tensor=True)

        with open(self.vector_file, 'wb') as f:
            pickle.dump({
                "slugs": self.book_slugs,
                "texts": self.book_texts,
                "embeddings": self.book_embeddings.cpu().numpy()
            }, f)
        print("✅ Embeddings cached.")

    def _load_embeddings(self):
        print("📦 Loading cached book embeddings...")
        with open(self.vector_file, 'rb') as f:
            data = pickle.load(f)
            self.book_slugs = data['slugs']
            self.book_texts = data['texts']
            self.book_embeddings = torch.tensor(data['embeddings'])

    def recommend(self, selected_slugs, top_k=4):
        if not selected_slugs:
            return Book.objects.order_by('-rating')[:top_k]

        selected_books = Book.objects.filter(slug__in=selected_slugs)
        if not selected_books.exists():
            return Book.objects.order_by('-rating')[:top_k]

        query = " ".join(f"{b.title} {b.description}" for b in selected_books)
        query_embedding = self.model.encode(query, convert_to_tensor=True)

        cos_scores = util.cos_sim(query_embedding, self.book_embeddings)[0]
        top_results = torch.topk(cos_scores, k=top_k + len(selected_slugs))

        recommended = []
        for score, idx in zip(top_results.values, top_results.indices):
            book_slug = self.book_slugs[idx]
            if book_slug not in selected_slugs:
                try:
                    bk = Book.objects.get(slug=book_slug)
                    recommended.append(bk)
                    intra = bk.stock
                    bk.stock = intra + 1
                    bk.save()
                except Book.DoesNotExist:
                    continue
            if len(recommended) == top_k:
                break

        return recommended

    def build(self):
        self._build_embeddings()
