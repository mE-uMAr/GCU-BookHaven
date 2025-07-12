from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import *
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from collections import Counter
from datetime import datetime, timedelta
import uuid
from django.db.models import Count, Avg, Sum
from django.views.decorators.csrf import csrf_exempt
import hashlib
import hmac
import urllib.parse

# AI model setup
from rest_framework.decorators import api_view
from rest_framework.response import Response
from core.models import Book

recommender = None

def get_recommender():
    global recommender
    if recommender is None:
        from core.AIModel.recommender import BookRecommender
        recommender = BookRecommender()
    return recommender


def serialize_book(book):
    return {
        "slug": book.slug,
        "title": book.title,
        "author": book.author,
        "genre": str(book.genre),
        "description": book.description,
        "rating": book.rating,
        "image": book.cover_image.url if book.cover_image else None,
        "price": book.price,
    }

@api_view(['POST'])
def recommend_books(request):
    slugs = request.data.get('slugs', [])
    recommender_instance = get_recommender()

    books = recommender_instance.recommend(slugs)
    return Response({"books": [serialize_book(b) for b in books]})


#AI model API ends here

def loginUser(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user_obj = User.objects.get(email=email)
            user = authenticate(request, username=user_obj.username, password=password)

            if user:
                login(request, user)
                return redirect('/')
            else:
                messages.error(request, 'Invalid credentials. Please try again.')
        except User.DoesNotExist:
            messages.error(request, 'No user with this email found.')

    return render(request, 'auth/login.html')

def signupUser(request):
    if request.method == 'POST':
        f_name = request.POST.get('fName')
        l_name = request.POST.get('lName')
        email    = request.POST.get('email')
        username = email.split('@')[0].lower()
        pass1 = request.POST.get('pass1')
        pass2 = request.POST.get('pass2')
        
        if pass1 != pass2:
            messages.error(request , 'Passwords do not match')
            return redirect('signup')
        if User.objects.filter(email=email).exists() or User.objects.filter(username=username).exists():
            messages.error(request , 'Username already exists')
            return redirect('signup')

        user = User.objects.create_user(first_name=f_name, last_name=l_name, username=username, email=email, password=pass1)
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, user)
        return redirect('/')
    return render(request, 'auth/signup.html')

def logoutUser(request):
    logout(request)
    return redirect('/')

def home(request):
    recent_books = Book.objects.all().order_by('-listDateTime')[:4]
    books = Book.objects.all()[:4]
    tBooks = Book.objects.all().order_by('-stock')[:4]
    allBooks = Book.objects.all()
    for book in allBooks:
        reviews = RevItem.objects.filter(book=book)
        if reviews.exists():
            num = reviews.count()
            stars = sum(rev.stars for rev in reviews)
            rating = stars / num
            book.rating = rating
            book.save()
    genres = Genre.objects.all()
    param = {
        'r_books': recent_books,
        'books': books,
        'trendBooks' : tBooks,
        'genres' : genres
    }
    return render(request, 'index.html', param)

@login_required
def profile(request):
    user = request.user

    # Profile update logic
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        if email == user.email and first_name == user.first_name and last_name == user.last_name:
            messages.error(request, 'No changes detected for the profile.')
        else:
            if first_name:
                user.first_name = first_name
            if last_name:
                user.last_name = last_name
            if email:
                user.email = email
            user.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('profile')

    orders = Order.objects.filter(user=user).prefetch_related('states')
    listings = ExchangeBook.objects.filter(uploadedBy=user)

    # Incoming requests (on user books)
    incoming_reqs = ExchangeRequest.objects.filter(exchange_book__uploadedBy=user).select_related('user', 'exchange_book')

    # Outgoing requests (user requested others)
    outgoing_reqs = ExchangeRequest.objects.filter(user=user).select_related('exchange_book', 'exchange_book__uploadedBy')

    context = {
        'user': user,
        'orders': orders,
        'listings': listings,
        'incoming_reqs': incoming_reqs,
        'outgoing_reqs': outgoing_reqs,
    }

    return render(request, 'profile.html', context)


@login_required
def exchange_response(request, req_id, action):
    req = get_object_or_404(ExchangeRequest, id=req_id, exchange_book__uploadedBy=request.user)
    if action == "accepted":
        req.status = "accepted"
    elif action == "rejected":
        req.status = "rejected"
    req.save()
    messages.success(request, f"Exchange request marked as {action}.")
    return redirect('profile')


def bookDetail(request, slug):
    user = request.user
    if request.method == "POST":
        audslg = request.POST.get("audslg")
        return redirect('start_jazzcash_payment', cat="audiobook", slg=audslg)
    try:
        aud_book = get_object_or_404(Audio_book, slug=slug)
        granted = False

        try:
            access = AccessAudio.objects.get(user=user, book=aud_book)
            granted = True
        except AccessAudio.DoesNotExist:
            granted = False

        context = {
            'book':aud_book,
            'granted':granted
        }

    except:
        inBook = get_object_or_404(Book, slug=slug)
        inter = inBook.stock
        inBook.stock = inter + 1
        inBook.save()

        book = get_object_or_404(Book, slug=slug)
        reviews = RevItem.objects.filter(book=book)
        star_counts = (
            reviews.values('stars').annotate(count=Count('stars')).order_by('-stars')
        )

        star_dict = {item['stars']: item['count'] for item in star_counts}

        total_reviews = reviews.count()
        star_percent = {}
        for star in range(1, 6):
            count = star_dict.get(star, 0)
            percent = (count / total_reviews * 100) if total_reviews > 0 else 0
            star_percent[star] = round(percent, 1)

        context = {
            'book': book,
            'reviews': reviews,
            'total_reviews': total_reviews,
            'star_counts': star_dict,
            'star_percent': star_percent,
        }
        
    return render(request, 'core/bookPage.html', context)

def browseBooks(request):
    books = Book.objects.all()
    genre = Genre.objects.all()
    return render(request, 'core/browse.html', {'books': books, 'genre': genre})

def genrePage(request, name):
    genre = Genre.objects.get(name = name)
    if name == "Audio" or name == "audio":
        books = Audio_book.objects.all()
    else:
        books = Book.objects.filter(genre = genre)
    return render(request, 'core/genrePage.html', {'books': books})

def exchangeDash(request):
    books = ExchangeBook.objects.filter(is_approved = True).exclude(
    requests__status__in=['accepted']
)
    return render(request, 'exchange/exchangeDash.html', {'books':books})

@login_required
def exchangeDetail(request, slug):
    if request.method == 'POST':
        message = request.POST.get('message')
        slug = request.POST.get('slug')
        user = request.user
        exchange_book = ExchangeBook.objects.filter(slug = slug).first()
        ExchangeRequest.objects.create(
            exchange_book = exchange_book,
            user = user,
            message = message,
        )
        messages.success(request, "Exchnage Request Submitted Successfully")

    book = ExchangeBook.objects.filter(slug = slug).first()
    return render(request, 'exchange/bookPage.html', {'book':book})

@login_required
def addBook(request):
    user = request.user
    if request.method == 'POST':
        image = request.FILES.get('book_image')
        title= request.POST.get('book_title')
        author = request.POST.get('book_author')
        condition = request.POST.get('book_condition')
        category = request.POST.get('book_category')
        description = request.POST.get('book_description')
        location = request.POST.get('book_location')
        price = request.POST.get('book_price')

        if image and title and author and category:
            addBook = ExchangeBook.objects.create(
                uploadedBy = user,
                title = title,
                author = author,
                cover_image = image,
                description = description,
                price = price,
                location = location,
                condition = condition,
                category = category,
            )
            messages.success(request, "Book submitted successfully, waiting for Admin approval!")
            return redirect('add_book')
        else:
            messages.error(request, "some error happened")
        
    return render(request, 'exchange/addBook.html')

@login_required
def cart(request):
    books = Book.objects.all()
    return render(request, 'core/cart.html', {'books': books})

#Payment gateway setup
@login_required
def checkout(request):
    user = request.user

    if request.method == 'POST':
        # Get submitted books from form
        book_slugs = request.POST.getlist("submittedBooks")
        if not book_slugs or not all(book_slugs):
            return HttpResponse("No books submitted. Please ensure JavaScript is enabled.")

        # Calculate quantities
        slug_counts = Counter(book_slugs)
        total_quantity = sum(slug_counts.values())

        # Total price comes from form/cart summary
        total_price = request.POST.get("total_price")
        if not total_price:
            return HttpResponse("Missing total price.")

        # Store all in session
        request.session["pending_order"] = {
            "p_number": request.POST.get('p_number'),
            "strAddress": request.POST.get('strAddr'),
            "city": request.POST.get('city'),
            "zip_code": request.POST.get('zip_code'),
            "country": request.POST.get('country'),
            "book_slugs": dict(slug_counts),  # {'slug1': 2, 'slug2': 1}
            "total_quantity": total_quantity,
            "total_price": total_price,
        }

        # Redirect to JazzCash payment view
        return redirect('start_jazzcash_payment', cat="checkout")

    # On GET — show checkout page
    books = Book.objects.all()
    offers = Offer.objects.filter(active=True).order_by('-min_books')

    return render(request, 'core/checkout.html', {
        'books': books,
        'user': user,
        'offers': offers,
    })

def start_jazzcash_payment(request, cat, slg=None):
    current_datetime = datetime.now()
    pp_TxnDateTime = current_datetime.strftime('%Y%m%d%H%M%S')
    expiry_datetime = current_datetime + timedelta(hours=1)
    pp_TxnExpiryDateTime = expiry_datetime.strftime('%Y%m%d%H%M%S')
    pp_TxnRefNo = "GCUBH" + pp_TxnDateTime

    # Defaults
    pp_Amount = "0"
    product_price = 0  # for display only
    txn_meta = {}  # anything we want to save like user, slug etc

    if cat == "checkout":
        order_data = request.session.get("pending_order")
        if not order_data:
            return redirect('checkout')

        total_price = float(order_data['total_price'])  # e.g. 78.93
        pp_Amount = str(int(total_price * 100))  # JazzCash needs it in paisa

        # Store txn ref
        order_data["txn_ref"] = pp_TxnRefNo
        request.session["pending_order"] = order_data
        PendingOrder.objects.update_or_create(txn_ref=pp_TxnRefNo, defaults={"data": order_data})

        product_price = total_price
        txn_meta = order_data

    elif cat == "audiobook":
        try:
            bk = Audio_book.objects.get(slug=slg)
        except Audio_book.DoesNotExist:
            return HttpResponse("Invalid audiobook slug")

        prc = float(bk.price)
        pp_Amount = str(int(prc * 100))
        product_price = prc

    else:
        return HttpResponse("Invalid payment source.")

    # JazzCash payload
    post_data = {
        "pp_Version": "1.1",
        "pp_TxnType": "",
        "pp_Language": "EN",
        "pp_MerchantID": 'MC185948',
        "pp_SubMerchantID": "",
        "pp_Password": 'v2ye1z9yw8',
        "pp_BankID": "TBANK",
        "pp_ProductID": "RETL",
        "pp_TxnRefNo": pp_TxnRefNo,
        "pp_Amount": pp_Amount,
        "pp_TxnCurrency": "PKR",
        "pp_TxnDateTime": pp_TxnDateTime,
        "pp_BillReference": "billRef",
        "pp_Description": "Book purchase from BookHeaven",
        "pp_TxnExpiryDateTime": pp_TxnExpiryDateTime,
        "pp_ReturnURL": 'http://127.0.0.1:8000/payment/verify/',
        "ppmpf_1": cat,
        "ppmpf_2": slg or "",
        "ppmpf_3": str(request.user.id),
        "ppmpf_4": "",
        "ppmpf_5": "",
    }

    integrity_salt = "twcauc2zw6"
    sorted_string = "&".join(
        f"{key}={value}" for key, value in sorted(post_data.items()) if value != ""
    )
    pp_SecureHash = hmac.new(
        integrity_salt.encode(),
        sorted_string.encode(),
        hashlib.sha256
    ).hexdigest().upper()

    post_data['pp_SecureHash'] = pp_SecureHash

    context = {
        'post_data': post_data,
        'product_price': product_price,
    }

    return render(request, "jazzcash_form.html", context)



@csrf_exempt
def verify_payment(request):
    if request.method != "POST":
        return HttpResponse("Invalid method", status=405)

    pp_ResponseCode = request.POST.get("pp_ResponseCode")
    txn_ref = request.POST.get("pp_TxnRefNo")
    cat = request.POST.get("ppmpf_1")
    audslug = request.POST.get("ppmpf_2")
    user_id = request.POST.get("ppmpf_3")

    if cat == "checkout":
        try:
            pending = PendingOrder.objects.get(txn_ref=txn_ref)
            order_data = pending.data
        except PendingOrder.DoesNotExist:
            return HttpResponse("No pending order found.")
        slug_counts = Counter(order_data['book_slugs'])
        books = Book.objects.filter(slug__in=slug_counts.keys())
        user = User.objects.get(id = user_id)
        order = Order.objects.create(
            user=user,
            p_number=order_data['p_number'],
            strAddress=order_data['strAddress'],
            city=order_data['city'],
            zip_code=order_data['zip_code'],
            country=order_data['country'],
            quantity=order_data['total_quantity'],
            total_price=order_data['total_price'],
        )

        for book in books:
            quan = slug_counts[book.slug]
            OrderItem.objects.create(order=order, book=book, quantity=quan)
            book.stock += 3
            book.save()

        OrderState.objects.create(order=order)
        pending.delete()
        request.session.pop("pending_order", None)
        context = {
            'order': order,
            'order_id' : order.orderId,
            'string': "Thank you, Your order has been successfully placed and is now being processed.",
            'link':"/orders",
            'price': order.total_price
        }

    elif cat == "audiobook":
        aud_book = Audio_book.objects.get(slug = audslug)
        user = User.objects.get(id = user_id)
        book = AccessAudio.objects.get_or_create(user = user, book = aud_book)
        context = {
            'book' : aud_book,
            'string': "Thank you, Your order has been successfully completed, Proceed to Audio Book page to download.",
            'link': f"/bookPage/{aud_book.slug}/",
            'price' : aud_book.price
        }

    return render(request, "payment_success.html", context)


#Payment gateway setup ends here


@login_required
def manageOrders(request):
    user = request.user
    if request.method == 'POST':
        odr_id = request.POST.get('odr_id')
        reorder = request.POST.get('reorder')
        stars = request.POST.get('starsRev')
        review = request.POST.get('starsRevTxt')
        revId = request.POST.get('odrId')

        if stars:
            revOdr = get_object_or_404(Order, orderId=revId)
            getprevRev = Review.objects.filter(order=revOdr).first()
            if getprevRev:
                messages.error(request, "Review Already exist")
                return redirect('manage_orders')
            objRev = Review.objects.create(
                order = revOdr,
                stars = stars,
                review = review
            )
            state = OrderState.objects.filter(order=revOdr).first()
            if state:
                state.rating = stars
                state.save()
            revOdr.save()
            revbks = OrderItem.objects.filter(order=revOdr)
            for item in revbks:
                RevItem.objects.create(
                    review = objRev, book = item.book, stars = stars, text = review
                )
            messages.success(request, "Review submitted successfully")
            return redirect('manage_orders')

        if reorder:
            reorder_obj = get_object_or_404(Order, orderId=reorder, user=user)
            new_order = Order(
                user=user,
                quantity=reorder_obj.quantity,
                total_price=reorder_obj.total_price,
                p_number=reorder_obj.p_number,
                strAddress=reorder_obj.strAddress,
                city=reorder_obj.city,
                state=reorder_obj.state,
                zip_code=reorder_obj.zip_code,
                country=reorder_obj.country,
                cardNumber=reorder_obj.cardNumber,
                ExpiryDate=reorder_obj.ExpiryDate,
                cvv=reorder_obj.cvv,
                holderName=reorder_obj.holderName,
                order_date=datetime.now(),
                status='pending',
            )
            new_order.save()
            original_items = OrderItem.objects.filter(order=reorder_obj)
            for item in original_items:
                OrderItem.objects.create(
                    order=new_order,
                    book=item.book,
                    quantity=item.quantity
                )
            OrderState.objects.create(order=new_order)
            messages.success(request, 'Order with same credentials placed successfully!')
            return redirect('manage_orders')

        order = get_object_or_404(Order, orderId=odr_id, user=user)
        if not order:
            messages.error(request, 'Order not found.')
            return redirect('manage_orders')
        else:
            odr_state = OrderState.objects.filter(order=order).first()
            if odr_state.status == "shipped":
                messages.error(request, 'Cannot cancel an order that has already been shipped.')
                return redirect('manage_orders')
            else:
                odr_state.status = "cancelled"
                odr_state.save()
                messages.success(request, 'Order cancelled successfully.')
                return redirect('manage_orders')

    orders = Order.objects.filter(user=user).order_by('-order_date')
    if not orders.exists():
        messages.error(request, 'You have no orders yet.')

    order_summaries = {}
    for order in orders:
        summary = ", ".join(
            f"{item.book.title} ({item.quantity})"
            for item in order.orderitem_set.all()
        )
        order_summaries[order.orderId] = summary

    reviewedOdr = Review.objects.filter(order__in=orders).values_list('order__orderId', flat=True)

    reqExc = ExchangeRequest.objects.filter(
        exchange_book__uploadedBy=request.user,
        status='accepted'
    ).select_related('exchange_book', 'user')

    total_earnings = ExchangeRequest.objects.filter(
        exchange_book__uploadedBy=request.user,
        status='accepted',
        exchange_book__category='sell'
    ).aggregate(total=Sum('exchange_book__price'))['total'] or 0

    total_swapped = ExchangeRequest.objects.filter(
        exchange_book__uploadedBy=request.user,
        status='accepted',
        exchange_book__category='swap'
    ).count()

    total_donated = ExchangeRequest.objects.filter(
        exchange_book__uploadedBy=request.user,
        status='accepted',
        exchange_book__category='donate'
    ).count()

    total_earnings = reqExc.filter(
        exchange_book__category='sell'
    ).aggregate(
        total=Sum('exchange_book__price')
    )['total'] or 0

    context = {
        'reviewed':reviewedOdr,
        'orders': orders,
        'summary': order_summaries,
        'reqExc':reqExc,
        'total_earnings': total_earnings,
        'total_swapped': total_swapped,
        'total_donated': total_donated,
        'total_earnings':total_earnings,
    }

    return render(request, 'core/order-management.html', context)


def searchResults(request):
    if request.method == 'GET':
        query = request.GET.get('query', '').strip()
    if query:
        books = Book.objects.filter(Q(title__icontains=query) |Q(author__icontains=query) | Q(description__icontains=query) | Q(publisher__icontains=query))
        if not books:
            messages.error(request, f'No results found for {query}.')
    else:
        messages.error(request, 'Please enter a search term.')
    
    return render(request, 'core/search-result.html', {'books': books, 'query': query})

def wishlist(request):
    books = Book.objects.all()
    return render(request, 'core/wishlist.html', {'books': books})

def discounts(request):
    offers = Offer.objects.all().order_by('min_books')
    return render(request, 'core/discount.html', {'offers' : offers})