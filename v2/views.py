from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import *

def store_map(request):
    return render(request, 'v2/stores_map.html')

def store_locations(request):
    stores = Store.objects.all()
    data = [{
        'name': store.name,
        'slug': store.slug,
        'lat': store.latitude,
        'lng': store.longitude,
    } for store in stores]
    return JsonResponse(data, safe=False)

def store_detail(request, slug):
    store = get_object_or_404(Store, slug=slug)
    books = StoreBook.objects.filter(store = store)
    return render(request, 'v2/store_detail.html', {'store': store, 'books': books})