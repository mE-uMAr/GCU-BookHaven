from django.contrib import admin
from .models import *

@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'latitude', 'longitude', 'created_at')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(StoreBook)
class StoreBookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'price', 'available')