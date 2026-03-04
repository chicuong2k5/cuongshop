from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum
from django.core.paginator import Paginator
from datetime import datetime
import json
from .forms import RegisterForm
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.contrib.auth import authenticate, login
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.db.models import Sum, Count
from .forms import UserUpdateForm, ProfileUpdateForm
from .forms import CheckoutForm
from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.db.models.functions import TruncMonth
from django.db.models.functions import TruncMonth, TruncDay

@staff_member_required
def manage_orders(request):
    orders = Order.objects.all().order_by('-id')

    # 🔎 Tìm kiếm theo username
    search_query = request.GET.get('search')
    if search_query:
        orders = orders.filter(user__username__icontains=search_query)

    # 🎯 Lọc theo trạng thái
    status_filter = request.GET.get('status')
    if status_filter:
        orders = orders.filter(status=status_filter)

    # 📦 Annotate tổng số lượng sản phẩm
    orders = orders.annotate(total_items=Sum('orderitem__quantity'))

    # 📄 Phân trang
    paginator = Paginator(orders, 5)  # 5 đơn mỗi trang
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'manage_orders.html', {
        'page_obj': page_obj
    })
@login_required
def checkout(request, pk=None):

    # ===== MUA NGAY 1 SẢN PHẨM =====
    if pk:
        product = get_object_or_404(Product, id=pk)
        total = product.final_price()

        if request.method == "POST":
            form = CheckoutForm(request.POST)
            if form.is_valid():
                order = form.save(commit=False)
                order.user = request.user
                order.total_price = total
                order.save()

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=1
                )

                messages.success(request, "Đặt hàng thành công!")
                return redirect("home")
        else:
            form = CheckoutForm()

        return render(request, "checkout.html", {
            "form": form,
            "product": product,
            "total": total
        })

    # ===== CHECKOUT GIỎ HÀNG =====
    selected_ids = request.POST.getlist('selected_items')

    cart_items = CartItem.objects.filter(
    user=request.user,
    id__in=selected_ids
)

    if not cart_items:
        messages.error(request, "Vui lòng chọn sản phẩm để thanh toán.")
        return redirect("cart")

    if not cart_items:
        messages.error(request, "Giỏ hàng trống!")
        return redirect("cart")

    total = sum(item.total_price() for item in cart_items)

    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.total_price = total
            order.save()

            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity
                )

            cart_items.delete()
            messages.success(request, "Đặt hàng thành công!")
            return redirect("home")
    else:
        form = CheckoutForm()

    return render(request, "checkout.html", {
        "form": form,
        "cart_items": cart_items,
        "total": total
    })
def buy_now(request, pk):
    product = Product.objects.get(id=pk)

    # Thêm vào giỏ
    CartItem.objects.create(
        user=request.user,
        product=product,
        quantity=1
    )

    return redirect('cart')
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@login_required
def cancel_order(request, id):

    order = get_object_or_404(
        Order,
        id=id,
        user=request.user
    )

    if request.method == "POST":

        reason = request.POST.get("reason")

        if order.can_cancel:

            order.status = "cancelled"
            order.cancel_reason = reason
            order.save()

            messages.success(
                request,
                "Đã hủy đơn hàng"
            )

        else:
            messages.error(
                request,
                "Không thể hủy đơn này"
            )

    return redirect("order_detail", id=order.id)
@login_required
def order_detail(request, id):
    order = get_object_or_404(Order, id=id, user=request.user)
    items = OrderItem.objects.filter(order=order)

    return render(request, 'order_detail.html', {
        'order': order,
        'items': items
    })
@login_required
def profile(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')

    total_spent = orders.aggregate(
        total=Sum('total_price')
    )['total'] or 0

    return render(request, 'profile.html', {
        'orders': orders,
        'total_spent': total_spent
    })

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Sai tài khoản hoặc mật khẩu")

    return render(request, 'login.html')
def logout_view(request):
    logout(request)
    return redirect('home')
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = RegisterForm()

    return render(request, 'register.html', {'form': form})
def home(request):
    products = Product.objects.all()
    categories = Category.objects.all()

    # SEARCH
    q = request.GET.get('q')
    if q:
        products = products.filter(Q(name__icontains=q))

    # FILTER CATEGORY
    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(category_id=category_id)

    brand_id = request.GET.get('brand')
    if brand_id:
        products = products.filter(brand_id=brand_id)
    # PAGINATION
    paginator = Paginator(products, 6)
    page = request.GET.get('page')
    products = paginator.get_page(page)
    hot_product = Product.objects.order_by('-discount_percent').first()

    return render(request, 'home.html', {
    'products': products,
    'categories': categories,
    'hot_product': hot_product,   # thêm dòng này
})

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    cart_item, created = CartItem.objects.get_or_create(
        user=request.user,
        product=product
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    messages.success(request, "Đã thêm vào giỏ hàng")
    return redirect('home')


@login_required
def cart_view(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total = sum(item.total_price() for item in cart_items)

    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total': total
    })


@login_required
def update_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id)

    try:
        quantity = int(request.POST.get('quantity'))
        if quantity > 0:
            item.quantity = quantity
            item.save()
    except:
        pass

    return redirect('cart')


@login_required
def remove_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id)
    item.delete()
    return redirect('cart')

@login_required
def dashboard(request):
    if not request.user.is_superuser:
        return redirect('home')

    today = timezone.now().date()
    current_month = timezone.now().month
    current_year = timezone.now().year
    # ================= DOANH THU =================
    # Chỉ tính đơn đã xác nhận hoặc đang giao hoặc đã giao

    total_revenue = Order.objects.filter(
        status__in=['confirmed', 'shipping', 'delivered']
    ).aggregate(Sum('total_price'))['total_price__sum'] or 0

    today_revenue = Order.objects.filter(
        status__in=['confirmed', 'shipping', 'delivered'],
        created_at__date=today
    ).aggregate(Sum('total_price'))['total_price__sum'] or 0

    month_revenue = Order.objects.filter(
        status__in=['confirmed', 'shipping', 'delivered'],
        created_at__month=current_month,
        created_at__year=current_year
    ).aggregate(Sum('total_price'))['total_price__sum'] or 0

    # ================= ĐƠN HÀNG =================

    total_orders = Order.objects.count()

    today_orders = Order.objects.filter(
        created_at__date=today
    ).count()

    # ================= USER =================

    total_users = User.objects.count()

    new_users_today = User.objects.filter(
        date_joined__date=today
    ).count()

    # ================= TOP PRODUCT =================

    top_products = OrderItem.objects.values(
        'product__name'
    ).annotate(
        total_sold = Sum('quantity')
    ).order_by('-total_sold')[:5]



    top_products_json = list(top_products)

    orders_by_day = Order.objects.annotate(
            day=TruncDay('created_at')
            ).values('day').annotate(
            total=Count('id')
            ).order_by('day')

    days = []
    orders_count = []

    for o in orders_by_day:
        days.append(o['day'].strftime("%d/%m"))
        orders_count.append(o['total'])

    # ================= TRẠNG THÁI =================

    pending = Order.objects.filter(status='pending').count()
    confirmed = Order.objects.filter(status='confirmed').count()
    shipping = Order.objects.filter(status='shipping').count()
    delivered = Order.objects.filter(status='delivered').count()
    rejected = Order.objects.filter(status='rejected').count()
    cancelled = Order.objects.filter(status='cancelled').count()


    approved = confirmed + shipping + delivered

    sales = Order.objects.filter(
    status='delivered'
).annotate(
    month=TruncMonth('created_at')
).values('month').annotate(
    total=Sum('total_price')
).order_by('month')

    months = []
    revenues = []

    for s in sales:
        months.append(s['month'].strftime("%m/%Y"))
        revenues.append(float(s['total']))


    months = months
    revenues = revenues


    return render(request, 'dashboard.html', {
        'total_revenue': total_revenue,
        'today_revenue': today_revenue,
        'month_revenue': month_revenue,
        'total_orders': total_orders,
        'today_orders': today_orders,
        'total_users': total_users,
        'new_users_today': new_users_today,
        'top_products': top_products,
        'pending': pending,
        'confirmed': confirmed,
        'shipping': shipping,
        'delivered': delivered,
        'rejected': rejected,
        'cancelled': cancelled,
        'months': months,
        'revenues': revenues,
        'approved': approved,
        'top_products_json': top_products_json,   # thêm dòng này
        'cancelled': cancelled,
        'days': days,
        'orders_count': orders_count,
    })
def product_detail(request, pk):
    product = Product.objects.get(id=pk)

    colors = product.colors.all()
    media = product.media.all()
    fallback_image = product.image.url if product.image else None

    reviews = Review.objects.filter(product=product)

    user_can_review = False
    user_already_reviewed = False

    if request.user.is_authenticated:
        has_bought = OrderItem.objects.filter(
            product=product,
            order__user=request.user,
            order__status='delivered'
        ).exists()

        user_already_reviewed = Review.objects.filter(
            product=product,
            user=request.user
        ).exists()

        user_can_review = has_bought and not user_already_reviewed

    # ===== THỐNG KÊ SAO =====
    total_reviews = reviews.count()

    star_counts = {
        5: reviews.filter(rating=5).count(),
        4: reviews.filter(rating=4).count(),
        3: reviews.filter(rating=3).count(),
        2: reviews.filter(rating=2).count(),
        1: reviews.filter(rating=1).count(),
    }

    star_percent = {}
    for star in star_counts:
        if total_reviews > 0:
            star_percent[star] = int((star_counts[star] / total_reviews) * 100)
        else:
            star_percent[star] = 0

    return render(request, 'product_detail.html', {
        'product': product,
        'colors': colors,
        'media': media,
        'fallback_image': fallback_image,
        'reviews': reviews.order_by("-created_at"),
        'user_can_review': user_can_review,
        'user_already_reviewed': user_already_reviewed,
        'star_counts': star_counts,
        'star_percent': star_percent,
        'total_reviews': total_reviews,
    })
@login_required
def edit_profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(
            request.POST,
            request.FILES,
            instance=profile
        )

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, "Cập nhật thành công!")
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=profile)

    return render(request, 'edit_profile.html', {
        'u_form': u_form,
        'p_form': p_form
    })
@staff_member_required
def update_order_status(request, pk):
    order = Order.objects.get(id=pk)

    if request.method == "POST":
        new_status = request.POST.get('status')
        order.status = new_status
        order.save()

    return redirect('manage_orders')


def get_color_image(request, color_id):
    color = ProductColor.objects.get(id=color_id)
    images = color.images.all()

    return JsonResponse({
        'main_image': images.first().image.url if images else '',
        'images': [img.image.url for img in images]
    })

@login_required
def add_review(request, pk):
    product = get_object_or_404(Product, id=pk)

    if request.method == "POST":
        rating = request.POST.get("rating")
        comment = request.POST.get("comment")
        image = request.FILES.get("image")

        has_bought = OrderItem.objects.filter(
            product=product,
            order__user=request.user,
            order__status='delivered'
        ).exists()

        already_reviewed = Review.objects.filter(
            product=product,
            user=request.user
        ).exists()

        if not has_bought:
            messages.error(request, "Bạn chưa mua sản phẩm này.")
            return redirect('product_detail', pk=pk)

        if already_reviewed:
            messages.error(request, "Bạn đã đánh giá rồi.")
            return redirect('product_detail', pk=pk)

        Review.objects.create(
            user=request.user,
            product=product,
            rating=rating,
            comment=comment,
            image=image
        )

        messages.success(request, "Đánh giá thành công!")

    return redirect('product_detail', pk=pk)