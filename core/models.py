from django.db import models
from django.utils.text import slugify
import uuid
from datetime import datetime
from django.contrib.auth import get_user_model
User = get_user_model()

class Genre(models.Model):
    name = models.CharField(max_length=50)
    genreBooks = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=5.0)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE, related_name='books')
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    available = models.BooleanField(default=True)
    publisher = models.CharField(max_length=100)
    language = models.CharField(max_length=30)
    pages = models.PositiveIntegerField()
    stock = models.PositiveIntegerField(default=0)
    cover_image = models.ImageField(upload_to='book_covers/')
    published_date = models.DateField()
    isbn = models.CharField(max_length=13, unique=True)
    listDateTime = models.DateTimeField(auto_now_add=True)
    #unique slug 
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            original_slug = self.slug
            num = 1
            while Book.objects.filter(slug=self.slug).exists():
                self.slug = f'{original_slug}-{num}'
                num += 1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class Audio_book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=5.0)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE, related_name='audio_books', null=True, blank=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    available = models.BooleanField(default=True)
    publisher = models.CharField(max_length=100)
    language = models.CharField(max_length=30)
    audio_file = models.FileField(upload_to='audiobooks/full/', null=True, blank=True)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            original_slug = self.slug
            num = 1
            while Book.objects.filter(slug=self.slug).exists():
                self.slug = f'{original_slug}-{num}'
                num += 1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class AccessAudio(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Audio_book, on_delete=models.CASCADE)


class ExchangeBook(models.Model):
    uploadedBy = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    cover_image = models.ImageField(upload_to='exchange_covers/')
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    location = models.CharField(max_length=100)
    condition = models.CharField(max_length=50)
    category = models.CharField(max_length=50, choices=[
        ('swap', 'Swap'),
        ('sell', 'Sell'),
        ('donate', 'Donate'),
    ])
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    #unique slug 
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            original_slug = self.slug
            num = 1
            while Book.objects.filter(slug=self.slug).exists():
                self.slug = f'{original_slug}-{num}'
                num += 1
        super().save(*args, **kwargs)
    def __str__(self):
        return self.uploadedBy.username + " - " + self.title

class Order(models.Model):
    orderId =  models.CharField(max_length=20, unique=True, blank=True)
    book = models.ManyToManyField(Book, through='OrderItem')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], default='pending')
    p_number= models.CharField(max_length=15, blank=True, null=True)
    strAddress = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    zip_code = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    cardNumber = models.CharField(max_length=20, blank=True, null=True)
    ExpiryDate = models.CharField(max_length=7, blank=True, null=True)  # Format: MM/YY
    cvv = models.CharField(max_length=4, blank=True, null=True)
    holderName = models.CharField(max_length=100, blank=True, null=True)
    
    def save(self, *args, **kwargs):
        if not self.orderId:
            year = datetime.now().year
            uid = uuid.uuid4().hex[:5].upper() 
            self.orderId = f"ORD-{year}-{uid}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.user.username + "'s order - " + self.orderId

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return self.order.orderId + " - " + self.book.title

class OrderState(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='states')
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ], default='pending')
    expected_delivery_date = models.DateField( blank=True, null=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)

    def __str__(self):
        return self.order.orderId + " - " + self.status

class Review(models.Model):
    reviewId = models.CharField(max_length=20)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    book = models.ManyToManyField(Book, through='RevItem')
    stars = models.PositiveIntegerField()
    review = models.CharField(max_length=300)
    def save(self, *args, **kwargs):
        if not self.reviewId:
            uid = uuid.uuid4().hex[:5].upper() 
            self.reviewId = f"REW-{uid}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.order.orderId} - {self.stars}"
        
class RevItem(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    stars = models.PositiveIntegerField()
    text = models.TextField()
    def __str__(self):
        return self.review.reviewId + " - " + self.book.title

class ExchangeRequest(models.Model):
    exchange_book = models.ForeignKey(ExchangeBook, on_delete=models.CASCADE, related_name='requests')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ], default='pending')

class Offer(models.Model):
    min_books = models.PositiveIntegerField(help_text="Minimum number of books to get discount")
    discount_percent = models.PositiveIntegerField(help_text="Percentage discount (e.g. 10 for 10%)")
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-min_books']

    def __str__(self):
        return f"{self.min_books}+ books = {self.discount_percent}% off"

class PendingOrder(models.Model):
    txn_ref = models.CharField(max_length=64, unique=True)
    data = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"TxnRef: {self.txn_ref} @ {self.created_at}"
