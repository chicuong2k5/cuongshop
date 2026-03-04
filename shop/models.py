from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Sum, Avg

# ================= CATEGORY =================
class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


# ================= BRAND =================
class Brand(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} ({self.category.name})"


# ================= PRODUCT =================
class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=12, decimal_places=2)
    discount_percent = models.IntegerField(default=0)
    stock = models.IntegerField(default=0)
    image = models.ImageField(upload_to='products/', blank=True, null=True)

    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, null=True, blank=True)

    variant_label = models.CharField(
        max_length=50,
        default="Phân loại")

    def final_price(self):
        return self.price * (100 - self.discount_percent) / 100
    
    @property
    def total_sold(self):
        return OrderItem.objects.filter(
            product=self,
            order__status='delivered'
        ).aggregate(
            total=Sum('quantity')
        )['total'] or 0

    @property
    def avg_rating(self):
        return self.review_set.aggregate(
            avg=Avg('rating')
        )['avg'] or 5
# ================= PRODUCT COLOR =================
class ProductColor(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="colors")
    name = models.CharField(max_length=50)
    image = models.ImageField(upload_to='variants/', blank=True, null=True)

    def __str__(self):
        return f"{self.product.name} - {self.name}"
# ================= PRODUCT IMAGE =================
class ProductImage(models.Model):
    color = models.ForeignKey(
        ProductColor,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(upload_to='products/colors/')
# ================= REVIEW =================
class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    rating = models.IntegerField()
    comment = models.TextField()

    image = models.ImageField(
        upload_to='reviews/',
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"
# ================= CART =================
class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def total_price(self):
        return self.product.final_price() * self.quantity

# ================= ORDER =================
class Order(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Chờ duyệt'),
        ('confirmed', 'Đã xác nhận'),
        ('shipping', 'Đang giao'),
        ('delivered', 'Đã giao'),
        ('cancelled', 'Đã hủy'),
        ('rejected', 'Từ chối'),
    ]

    PAYMENT_CHOICES = (
        ('cod', 'Thanh toán khi nhận hàng'),
        ('bank', 'Chuyển khoản ngân hàng'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    full_name = models.CharField(max_length=200, null=True)
    address = models.TextField( null=True)
    phone = models.CharField(max_length=20, null=True)

    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='cod')

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"
    @property
    def final_price(self):
        return self.price * (100 - self.discount_percent) / 100


# ================= ORDER ITEM =================
class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items"   # THÊM CÁI NÀY
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()

    @property
    def total_price(self):
            return self.product.final_price() * self.quantity
# ================= PROFILE =================
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default.png', blank=True)
    phone = models.CharField(max_length=20, blank=True)
    GENDER_CHOICES = (
    ('male', 'Nam'),
    ('female', 'Nữ'),
    ('other', 'Khác'),
)

    gender = models.CharField(
    max_length=10,
    choices=GENDER_CHOICES,
    blank=True,
    null=True
)

    birthday = models.DateField(
    blank=True,
    null=True
)

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

class ProductMedia(models.Model):
    MEDIA_TYPE = (
        ('image', 'Image'),
        ('video', 'Video'),
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='media'
    )

    media_type = models.CharField(
    max_length=10,
    choices=MEDIA_TYPE,
    default='image'
)
    file = models.FileField(upload_to='products/media/')
    thumbnail = models.ImageField(upload_to='products/video_thumb/', blank=True, null=True)