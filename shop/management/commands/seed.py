from django.core.management.base import BaseCommand
from shop.models import Category, Product
from django.contrib.auth.models import User
import random


class Command(BaseCommand):
    help = "Seed database with demo data"

    def handle(self, *args, **kwargs):

        categories = ['Keyboard', 'Mouse', 'Headset', 'Monitor']

        for c in categories:
            Category.objects.get_or_create(name=c)

        for i in range(20):
            Product.objects.create(
                name=f"RGB Gear {i}",
                description="Gaming RGB Product",
                price=random.randint(500000, 5000000),
                discount_percent=random.choice([0,10,20]),
                stock=random.randint(5, 50),
                category=random.choice(Category.objects.all())
            )

        self.stdout.write(self.style.SUCCESS("Seed data created successfully!"))