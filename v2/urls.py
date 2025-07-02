from django.urls import path
from . import views
urlpatterns = [
    path('stores/', views.store_map, name='store_map'),
    path('api/store-locations/', views.store_locations, name='store_locations'),
    path('store/<slug:slug>/', views.store_detail, name='store_detail'),
]