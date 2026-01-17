from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import (
    MainCategory, SubCategory, 
    Product, ProductImage, Cart, CartItem
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
    return redirect('dashboard')


@login_required
def profile_view(request):
    profile = request.user.userprofile
    form = UserProfileForm(instance=profile)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')

    return render(request, 'profile.html', {'form': form})


@login_required
def add_to_cart(request, product_id):
    cart = request.user.cart
    product = get_object_or_404(Product, id=product_id)

    item, created = CartItem.objects.get_or_create(
        cart=cart, product=product
    )
    if not created:
        item.quantity += 1
    item.save()
    return redirect('dashboard')
