from django.db import models
from django.utils.text import slugify

class Store(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    address = models.TextField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class StoreBook(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    price = models.FloatField()
    available = models.BooleanField(default=True)
    image = models.ImageField(upload_to='store_book_covers/' , blank=True, null=True)
    def __str__(self):
        return self.store.name + self.title