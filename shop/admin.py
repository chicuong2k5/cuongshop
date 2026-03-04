from django.contrib import admin
from .models import (
    Category, Product, Order, OrderItem,
    Review, Profile, Brand,
    ProductImage, ProductColor, ProductMedia
)

# ================= PRODUCT IMAGE INLINE =================
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


# ================= PRODUCT COLOR INLINE =================
class ProductColorInline(admin.TabularInline):
    model = ProductColor
    extra = 1


# ================= PRODUCT MEDIA INLINE =================
class ProductMediaInline(admin.TabularInline):
    model = ProductMedia
    extra = 1


# ================= PRODUCT =================
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'price', 'discount_percent', 'stock', 'category']
    list_filter = ['category']
    search_fields = ['name']
    inlines = [ProductColorInline, ProductMediaInline]  # GỘP LẠI


# ================= BRAND =================
@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'category']


# ================= CATEGORY =================
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']


# ================= ORDER ITEM INLINE =================
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


# ================= ORDER =================
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'total_price', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__username']
    list_editable = ['status']
    ordering = ['-created_at']
    inlines = [OrderItemInline]


# ================= ORDER ITEM =================
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity']


# ================= REVIEW =================
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'rating', 'created_at']


# ================= PROFILE =================
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone']


# ================= PRODUCT COLOR =================
@admin.register(ProductColor)
class ProductColorAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'name']
    inlines = [ProductImageInline]


# ================= PRODUCT IMAGE =================
@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['id', 'color']