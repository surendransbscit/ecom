from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import (
    MainCategory, SubCategory, 
    Product, ProductImage, Cart, CartItem, UserProfile,Order, OrderItem,
)
from .forms import RegisterForm, UserProfileForm, SearchForm
from django.db.models import Subquery, OuterRef
from django.db.models import F
from django.utils import timezone


def dashboard(request):

    categories = MainCategory.objects.prefetch_related('sub_categories__products')
    products = Product.objects.order_by('-created_at')[:8]
    discount_products = Product.objects.filter(discount_percent__gt=0).order_by('-discount_percent')[:6]
    best_offers = Product.objects.prefetch_related('images').order_by('?')[:6]

    return render(request, 'dashboard.html', {
        'categories': categories,
        'products': products,
        'discount_products': discount_products,
        'best_offers': best_offers,
    })



def product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    images = product.images.all()
    return render(request, 'product_detail.html', {
        'product': product,
        'images': images
    })


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            Cart.objects.create(user=user)
            login(request, user)
            return redirect('dashboard')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def profile_view(request):
    profile, created = UserProfile.objects.get_or_create(
        user=request.user
    )

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile)

    return render(request, 'profile.html', {'form': form})


@login_required
def add_to_cart(request, product_id):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    product = get_object_or_404(Product, id=product_id)

    item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product
    )

    if not created:
        item.quantity += 1
        item.save()

    return redirect('dashboard')


@login_required
def cart_view(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    items = cart.items.select_related('product')

    total = sum(item.product.discounted_price() * item.quantity for item in items)

    return render(request, 'cart.html', {
        'cart': cart,
        'items': items,
        'total': total
    })


@login_required
def place_order(request):
    cart = request.user.cart
    items = cart.items.select_related('product')

    if not items.exists():
        return redirect('cart')

    total = sum(item.product.discounted_price() * item.quantity for item in items)

    order = Order.objects.create(
        user=request.user,
        total_price=total,
        status='PLACED'
    )

    for item in items:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price=item.product.discounted_price()
        )

    items.delete()

    return redirect('my_orders')


@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).prefetch_related('items__product')

    return render(request, 'my_orders.html', {
        'orders': orders
    })


