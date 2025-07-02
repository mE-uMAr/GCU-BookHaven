from django.urls import path
from .views import *

urlpatterns = [
    path('', home, name='home'),
    path('login/', loginUser, name='login'),
    path('signup/', signupUser, name='signup'),
    path('logout/', logoutUser, name='logout'),
    path('profile/', profile, name='profile'),
    path('bookPage/<slug:slug>/', bookDetail, name='book_detail'),
    path('browse/', browseBooks, name='browse_books'),
    path('browse/<str:name>/', genrePage, name='genrePage'),
    path('exchange/', exchangeDash, name='exchange_dashboard'),
    path('exchangeoffer/<slug:slug>/', exchangeDetail, name="exchangePage"),
    path('addBook/', addBook, name='add_book'),
    path('cart/', cart, name='cart'),
    path('checkout/', checkout, name='checkout'),
    path("start-payment/<str:cat>/", start_jazzcash_payment, name="start_jazzcash_payment"),
    path("start-payment/<str:cat>/<str:slg>/", start_jazzcash_payment, name="start_jazzcash_payment"),
    path("payment/verify/", verify_payment, name="verify_payment"),
    path('orders', manageOrders, name='manage_orders'),
    path('search/', searchResults, name='search_books'),
    path('wishlist/', wishlist, name='wishlist'),
    path('discount/', discounts, name='discounts'),
    path('exchange-response/<int:req_id>/<str:action>/', exchange_response, name='exchange_response'),
    #AI Model Recommender
    path("api/recommend/", recommend_books, name="recommend_books"),
]