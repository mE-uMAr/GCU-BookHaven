import os
import uuid
import random
import requests
from datetime import datetime, timedelta
from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from PIL import Image, ImageDraw, ImageFont
import textwrap
from faker import Faker

# Get the User model
User = get_user_model()

from ...models import (
    Genre, Book, ExchangeBook, Order, OrderItem,
    OrderState, Review, RevItem, ExchangeRequest, Offer
)

fake = Faker()

class Command(BaseCommand):
    help = 'Seed the database with highly realistic data'

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting database seeding process...")
        self.create_genres()
        self.create_users()
        self.create_books()
        self.create_exchange_books()
        self.create_orders()
        self.create_reviews()
        self.create_exchange_requests()
        self.create_offers()
        self.stdout.write(self.style.SUCCESS("Database seeded successfully!"))

    def create_genres(self):
        self.stdout.write("Creating genres...")
        genres = [
            ("Fiction", "Works of imaginative narration, often including novels, short stories, and novellas."),
            ("Non-Fiction", "Factual works including biographies, histories, and reference books."),
            ("Science Fiction", "Fiction dealing with futuristic concepts, space travel, time travel, etc."),
            ("Fantasy", "Fiction involving magical or supernatural elements."),
            ("Mystery", "Fiction dealing with the solution of a crime or puzzle."),
            ("Romance", "Fiction focusing on love and romantic relationships."),
            ("Thriller", "Fiction intended to excite and suspense the reader."),
            ("Biography", "Non-fiction accounts of people's lives."),
            ("History", "Non-fiction works about past events."),
            ("Science", "Non-fiction works about scientific topics."),
            ("Self-Help", "Non-fiction works intended to help readers improve themselves."),
            ("Business", "Non-fiction works about business and economics."),
            ("Technology", "Non-fiction works about technology and computing."),
            ("Cooking", "Non-fiction works about cooking and food."),
            ("Travel", "Non-fiction works about travel and places."),
            ("Braille", "Books for blindes"),
            ("Islamic", "Islamic religious books"),
        ]

        for name, description in genres:
            Genre.objects.get_or_create(
                name=name,
                defaults={'description': description, 'genreBooks': 0}
            )

        self.stdout.write(self.style.SUCCESS(f"Created {len(genres)} genres"))

    def generate_book_cover(self, title, author):
        width, height = 600, 800
        
        # Fetch a random background image from Unsplash
        try:
            response = requests.get(f'https://source.unsplash.com/random/{width}x{height}?abstract,texture,nature')
            response.raise_for_status()
            image = Image.open(BytesIO(response.content)).convert('RGB')
        except requests.exceptions.RequestException:
            # Fallback to a plain background if the image fetch fails
            bg_color = (random.randint(50, 150), random.randint(50, 150), random.randint(50, 150))
            image = Image.new('RGB', (width, height), bg_color)

        draw = ImageDraw.Draw(image)

        # Add a semi-transparent overlay for text readability
        overlay = Image.new('RGBA', (width, height), (0, 0, 0, 128))
        image.paste(overlay, (0, 0), overlay)

        # Try to load a more professional font
        try:
            # You might need to change this path to a font file on your system
            title_font = ImageFont.truetype("arialbd.ttf", 60)
            author_font = ImageFont.truetype("arial.ttf", 36)
        except IOError:
            title_font = ImageFont.load_default()
            author_font = ImageFont.load_default()

        # Add title (wrapped)
        title_lines = textwrap.wrap(title, width=20)
        title_y = height / 3
        for line in title_lines:
            bbox = draw.textbbox((0, 0), line, font=title_font)
            text_width = bbox[2] - bbox[0]
            draw.text(((width - text_width) / 2, title_y), line, fill=(255, 255, 255), font=title_font)
            title_y += bbox[3] - bbox[1] + 10

        # Add author
        author_text = f"by {author}"
        bbox = draw.textbbox((0, 0), author_text, font=author_font)
        text_width = bbox[2] - bbox[0]
        draw.text(((width - text_width) / 2, title_y + 30), author_text, fill=(200, 200, 200), font=author_font)
        
        # Save to a temporary in-memory file
        temp_file = BytesIO()
        image.save(temp_file, format='JPEG', quality=95)
        temp_file.seek(0)
        
        return SimpleUploadedFile(
            name=f"{slugify(title)}.jpg",
            content=temp_file.read(),
            content_type='image/jpeg'
        )

    def create_books(self):
        self.stdout.write("Creating books...")
        genres = list(Genre.objects.all())
        publishers = [
            "Penguin Random House", "HarperCollins", "Simon & Schuster",
            "Hachette Book Group", "Macmillan", "Scholastic", "Disney Publishing",
            "Oxford University Press", "Cambridge University Press", "Pearson"
        ]
        languages = ["English", "Spanish", "French", "German", "Chinese", "Japanese"]

        for _ in range(100):
            title = fake.sentence(nb_words=random.randint(2, 6))[:-1]
            author = fake.name()
            genre = random.choice(genres)
            
            book = Book(
                title=title,
                author=author,
                rating=round(random.uniform(3.0, 5.0), 1),
                genre=genre,
                description="\n\n".join(fake.paragraphs(nb=random.randint(3, 6))),
                price=round(random.uniform(5.99, 29.99), 2),
                publisher=random.choice(publishers),
                language=random.choice(languages),
                pages=random.randint(100, 800),
                cover_image=self.generate_book_cover(title, author),
                published_date=fake.date_between(start_date='-30y', end_date='today'),
                isbn=fake.isbn13(),
                available=random.choice([True, True, False]) # More likely to be available
            )
            book.save()

            # Update genre book count accurately
            genre.genreBooks += 1
            genre.save()

        self.stdout.write(self.style.SUCCESS(f"Created 100 books"))

    def create_users(self):
        self.stdout.write("Creating users...")
        for _ in range(20):
            User.objects.create_user(
                username=fake.user_name(),
                email=fake.email(),
                password="testpass123",
                first_name=fake.first_name(),
                last_name=fake.last_name()
            )

        # Create an admin user if it doesn't exist
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser(
                username="admin",
                email="admin@example.com",
                password="adminpass123",
                first_name="Admin",
                last_name="User"
            )

        self.stdout.write(self.style.SUCCESS("Created 20 regular users and 1 admin user"))

    def create_exchange_books(self):
        self.stdout.write("Creating exchange books...")
        users = list(User.objects.all())
        conditions = ["New", "Like New", "Very Good", "Good", "Acceptable"]
        categories = ["swap", "sell", "donate"]

        for _ in range(50):
            title = fake.sentence(nb_words=random.randint(2, 6))[:-1]
            author = fake.name()
            category = random.choice(categories)

            exchange_book = ExchangeBook(
                uploadedBy=random.choice(users),
                title=title,
                author=author,
                cover_image=self.generate_book_cover(title, author),
                description="\n\n".join(fake.paragraphs(nb=random.randint(2, 4))),
                price=round(random.uniform(1.00, 20.00), 2) if category == 'sell' else None,
                location=fake.city(),
                condition=random.choice(conditions),
                category=category,
                is_approved=random.choice([True, False])
            )
            exchange_book.save()

        self.stdout.write(self.style.SUCCESS("Created 50 exchange books"))

    def create_orders(self):
        self.stdout.write("Creating orders...")
        users = list(User.objects.exclude(is_staff=True))
        available_books = list(Book.objects.filter(available=True, stock__gt=0))

        if not available_books:
            self.stdout.write(self.style.WARNING("No available books to create orders. Skipping."))
            return

        for _ in range(30):
            user = random.choice(users)
            order_date = fake.date_time_between(start_date='-1y', end_date='now', tzinfo=None)
            
            order = Order.objects.create(
                user=user,
                total_price=0, # Will be updated
                order_date=order_date,
                status='pending', # Initial status
                p_number=fake.phone_number(),
                strAddress=fake.street_address(),
                city=fake.city(),
                state=fake.state(),
                zip_code=fake.zipcode(),
                country=fake.country(),
                cardNumber=fake.credit_card_number(),
                ExpiryDate=fake.credit_card_expire(),
                cvv=fake.credit_card_security_code(),
                holderName=user.get_full_name()
            )

            total_price = 0
            num_items = random.randint(1, 5)
            order_books = random.sample(available_books, min(num_items, len(available_books)))

            for book in order_books:
                quantity = random.randint(1, 2)
                if book.stock >= quantity:
                    OrderItem.objects.create(
                        order=order,
                        book=book,
                        quantity=quantity
                    )
                    total_price += book.price * quantity
                    book.stock -= quantity
                    book.save()

            if total_price > 0:
                order.total_price = total_price
                order_status = random.choice(['pending', 'completed', 'cancelled'])
                order.status = order_status
                order.save()
                
                # Create corresponding order states
                self.create_order_states(order, order_status, order_date)
            else:
                # If no items could be added, delete the empty order
                order.delete()

        self.stdout.write(self.style.SUCCESS("Created orders with items and states"))

    def create_order_states(self, order, final_status, order_date):
        states = ['pending']
        if final_status in ['completed', 'cancelled']:
            states.append('processing')
            if final_status == 'completed':
                states.extend(['shipped', 'delivered'])
            else:
                states.append('cancelled')
        
        for status in states:
            delivery_date = (order_date + timedelta(days=random.randint(2, 10))).date() if status != 'cancelled' else None
            OrderState.objects.create(
                order=order,
                status=status,
                expected_delivery_date=delivery_date
            )

    def create_reviews(self):
        self.stdout.write("Creating reviews...")
        completed_orders = list(Order.objects.filter(status='completed'))
        
        if not completed_orders:
            self.stdout.write(self.style.WARNING("No completed orders to review. Skipping."))
            return

        for order in random.sample(completed_orders, k=min(15, len(completed_orders))):
            review = Review.objects.create(
                order=order,
                stars=random.randint(1, 5),
                review=fake.paragraph(nb_sentences=random.randint(2, 5))
            )
            
            for item in order.orderitem_set.all():
                RevItem.objects.create(
                    review=review,
                    book=item.book,
                    stars=random.randint(max(1, review.stars - 1), min(5, review.stars + 1)),
                    text=fake.paragraph(nb_sentences=random.randint(1, 3))
                )
        
        self.stdout.write(self.style.SUCCESS("Created reviews for completed orders"))

    def create_exchange_requests(self):
        self.stdout.write("Creating exchange requests...")
        approved_books = list(ExchangeBook.objects.filter(is_approved=True))
        users = list(User.objects.exclude(is_staff=True))

        if not approved_books:
            self.stdout.write(self.style.WARNING("No approved exchange books to create requests for. Skipping."))
            return

        for book in random.sample(approved_books, k=min(20, len(approved_books))):
            possible_requesters = [u for u in users if u != book.uploadedBy]
            if not possible_requesters:
                continue

            requester = random.choice(possible_requesters)
            
            ExchangeRequest.objects.create(
                exchange_book=book,
                user=requester,
                message=fake.paragraph(nb_sentences=random.randint(1, 4)),
                status=random.choice(['pending', 'accepted', 'rejected'])
            )
        
        self.stdout.write(self.style.SUCCESS("Created 20 exchange requests"))

    def create_offers(self):
        self.stdout.write("Creating special offers...")
        offers = [
            {'min_books': 2, 'discount_percent': 5},
            {'min_books': 3, 'discount_percent': 10},
            {'min_books': 5, 'discount_percent': 15},
            {'min_books': 10, 'discount_percent': 25},
        ]

        for offer_data in offers:
            Offer.objects.get_or_create(
                min_books=offer_data['min_books'],
                defaults={'discount_percent': offer_data['discount_percent'], 'active': True}
            )
            
        self.stdout.write(self.style.SUCCESS(f"Created {len(offers)} special offers"))