from django.contrib import admin
from .models import Product, Profile, Order, OrderItem, Transaction

# Register your models here.
admin.site.register(Product)
admin.site.register(Profile)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Transaction)
