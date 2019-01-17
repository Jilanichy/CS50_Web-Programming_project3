from __future__ import unicode_literals
from django.db import models
from django.conf import settings
from django.db.models.signals import post_save

# Create your models here.
class Product(models.Model):
    order_name = models.CharField(max_length=64, blank=True)
    order_subs = models.CharField(max_length=20, blank=True)
    other_order_name = models.CharField(max_length=64, blank=True)
    order_item = models.CharField(max_length=64)
    size = models.CharField(max_length=20, blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)


    def __str__(self):
        if self.order_name:
            return self.order_name
        if self.other_order_name:
            return self.other_order_name
        else:
            return self.order_subs

# class Product2(models.Model):
#     order_name = models.CharField(max_length=64)
#     order_item = models.CharField(max_length=64)
#     size = models.CharField(max_length=20, blank=True)
#     price = models.DecimalField(max_digits=6, decimal_places=2)

#     def __str__(self):
#         return self.order_name


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, blank=True)
    stripe_id = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.user.username


def post_save_profile_create(sender, instance, created, *args, **kwargs):
    user_profile, created = Profile.objects.get_or_create(user=instance)

    if user_profile.stripe_id is None:
        user_profile.save()

post_save.connect(post_save_profile_create, sender=settings.AUTH_USER_MODEL)


class OrderItem(models.Model):
    product = models.OneToOneField(Product, on_delete=models.SET_NULL, null=True)
    is_ordered = models.BooleanField(default=False)
    date_added = models.DateTimeField(auto_now=True)
    date_ordered = models.DateTimeField(null=True)

    def __str__(self):
        return self.product.order_name


class Order(models.Model):
    ref_code = models.CharField(max_length=15)
    owner = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True)
    is_ordered = models.BooleanField(default=False)
    items = models.ManyToManyField(OrderItem)
    date_ordered = models.DateTimeField(auto_now=True)

    def get_cart_items(self):
        return self.items.all()

    def get_cart_total(self):
        return sum([item.product.price for item in self.items.all()])


    def __str__(self):
        return '{0} - {1}'.format(self.owner, self.ref_code)





class Transaction(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    token = models.CharField(max_length=120)
    order_id = models.CharField(max_length=120)
    amount = models.DecimalField(max_digits=100, decimal_places=2)
    success = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)

    def __str__(self):
        return self.order_id

    class Meta:
        ordering = ['-timestamp']



# class Sicilian_Pizza(models.Model):
#     order_item = models.CharField(max_length=64)
#     small_item_price = models.FloatField()
#     large_item_price = models.FloatField()

#     def __str__(self):
#         return self.order_item

# class Subs(models.Model):
#     order_item = models.CharField(max_length=64)
#     additions = models.CharField(max_length=64)
#     small_item_price = models.FloatField()
#     large_item_price = models.FloatField()

#     def __str__(self):
#         return self.order_item

# class Pasta(models.Model):
#     order_item = models.CharField(max_length=64)
#     price = models.FloatField()

#     def __str__(self):
#         return self.order_item

# class Salads(models.Model):
#     order_item = models.CharField(max_length=64)
#     price = models.FloatField()

#     def __str__(self):
#         return self.order_item

# class Dinner_Platters(models.Model):
#     order_item = models.CharField(max_length=64)
#     small_item_price = models.FloatField()
#     large_item_price = models.FloatField()

#     def __str__(self):
#         return self.order_item
