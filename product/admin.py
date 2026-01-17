from django.contrib import admin
from .models import (
    UserProfile,
    MainCategory,
    SubCategory,
    Product,
    ProductImage,
    Cart,
    CartItem,
    Order,
    OrderItem
)


# -----------------------
# User Profile
# -----------------------
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone')
    search_fields = ('user__username', 'phone')


# -----------------------
# Categories
# -----------------------
@admin.register(MainCategory)
class MainCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'main_category')
    list_filter = ('main_category',)
    search_fields = ('name',)



# -----------------------
# Product Images (INLINE)
# -----------------------
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


# -----------------------
# Products
# -----------------------
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock', 'created_at')
    list_filter = ('category',)
    search_fields = ('name',)
    inlines = [ProductImageInline]


# -----------------------
# Cart
# -----------------------
class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user',)
    inlines = [CartItemInline]


# -----------------------
# Orders
# -----------------------
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_price', 'status', 'ordered_at')
    list_filter = ('status',)
    inlines = [OrderItemInline]
