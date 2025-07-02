
from django.contrib import admin
from .models import *

admin.site.register(Genre)
admin.site.register(Review)
admin.site.register(RevItem)

@admin.register(ExchangeRequest)
class ExchangeRequestAdmin(admin.ModelAdmin):
    list_display = ('exchange_book', 'user', 'status')
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'book', 'quantity')
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('orderId', 'user', 'quantity', 'total_price')
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'rating', 'price')
@admin.register(OrderState)
class OrderStateAdmin(admin.ModelAdmin):
    list_display = ('order', 'status')
@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ('min_books', 'discount_percent', 'active')
@admin.register(ExchangeBook)
class ExchangeBookAdmin(admin.ModelAdmin):
    list_display = ('uploadedBy' , 'title' , 'category', 'is_approved')
@admin.register(Audio_book)
class Audio_bookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'price')

admin.site.site_header = "📚 GCU BookHeaven Admin"   # top left site header
admin.site.site_title = "GCU BookHaven Admin Portal"          # browser tab title
admin.site.index_title = "Welcome to GCU BookHeaven Admin"  # dashboard title
