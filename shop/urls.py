from django.urls import path
from . import views
from django.urls import path, include
urlpatterns = [
    path('', views.home, name='home'),
    path('add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_view, name='cart'),
    path('update/<int:item_id>/', views.update_cart, name='update_cart'),
    path('remove/<int:item_id>/', views.remove_cart, name='remove_cart'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('login/', views.login_view, name='login'),
    path('profile/', views.profile, name='profile'),
    path('order/<int:id>/', views.order_detail, name='order_detail'),
    path('cancel/<int:id>/', views.cancel_order, name='cancel_order'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('buy-now/<int:pk>/', views.buy_now, name='buy_now'),
    path('checkout/<int:pk>/', views.checkout, name='checkout'),
    path('checkout/', views.checkout, name='checkout'),
    path('manage-orders/', views.manage_orders, name='manage_orders'),
    path('update-order/<int:pk>/<str:status>/',views.update_order_status,name='update_order_status'),
    path("product/<int:pk>/review/", views.add_review, name="add_review"),
    path('get-color-image/<int:color_id>/', views.get_color_image),
]