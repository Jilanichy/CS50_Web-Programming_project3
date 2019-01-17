from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.conf import settings
from django.contrib import messages
from .forms import SignUpForm
# from .models import Regular_Pizza, Toppings, Sicilian_Pizza, Subs, Pasta, Salads, Dinner_Platters
from .models import Product, Profile, OrderItem, Order, Transaction
from django.contrib.auth.decorators import login_required
from django.urls import reverse
import datetime
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY



def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, ('Welcome! You are logged In!'))
            return redirect(reverse('orders:home'))
        else:
            messages.success(request, ('Please type correct Username and Password'))
            return redirect(reverse('orders:login'))
    else:
        return render(request, 'orders/login.html', {})


def logout_view(request):
    logout(request)
    messages.success(request, ('You are now logged out'))
    return redirect(reverse('orders:product_list'))


def registration_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, ('Registration Successful'))
            return redirect(reverse('orders:product_list'))
    else:
        form = SignUpForm()
    context = {'form': form}
    return render(request, 'orders/registration.html', context)


def product_list(request):
    object_list = Product.objects.all()
    filtered_orders = Order.objects.filter(is_ordered=False)
    current_order_products = []
    if filtered_orders.exists():
        user_order = filtered_orders[0]
        user_order_items = user_order.items.all()
        current_order_products = [product.product for product in user_order_items]
    context = {
        'object_list': object_list,
        'current_order_products': current_order_products
    }
    return render(request, "orders/product_list.html", context)


def get_user_pending_order(request):
    # get order for the correct user
    user_profile = get_object_or_404(Profile, user=request.user)
    order = Order.objects.filter(owner=user_profile, is_ordered=False)
    if order.exists():
        # get the only order in the list of filtered orders
        return order[0]
    return 0


@login_required()
def add_to_cart(request, **kwargs):
    # get the user profile
    user_profile = get_object_or_404(Profile, user=request.user)
    # filter products by id
    product = Product.objects.filter(id=kwargs.get('item_id', "")).first()
    # check if the user already owns this product
    if product in request.user.profile.products.all():
        messages.info(request, 'You already own this product')
        return redirect(reverse('orders:product_list'))
    # create orderItem of the selected product
    order_item, status = OrderItem.objects.get_or_create(product=product)

    # create order associated with the user
    user_order, status = Order.objects.get_or_create(owner=user_profile, is_ordered=False)
    user_order.items.add(order_item)

    # show confirmation message and redirect back to the same page
    messages.info(request, "item added to cart")
    return redirect(reverse('orders:product_list'))


def home(request):
    return render(request, 'orders/home.html')


@login_required()
def order_details(request, **kwargs):
    existing_order = get_user_pending_order(request)
    context = {
        'order': existing_order
    }
    return render(request, 'orders/order_summary.html', context)


@login_required()
def delete_from_cart(request, item_id):
    item_to_delete = OrderItem.objects.filter(pk=item_id)
    if item_to_delete.exists():
        item_to_delete[0].delete()
        messages.info(request, "Item has been deleted from Your Cart")
    return redirect(reverse('orders:order_summary'))


@login_required()
def checkout(request, **kwargs):
    # client_token = generate_client_token()
    existing_order = get_user_pending_order(request)
    publishKey = settings.STRIPE_PUBLISHABLE_KEY
    if request.method == 'POST':
        try:
            token = request.POST['stripeToken']

            charge = stripe.Charge.create(
                amount=100*existing_order.get_cart_total(),
                currency='usd',
                description='Example charge',
                source=token,
            )
            return redirect(reverse('orders:update_records',
                    kwargs={
                        'token': token
                    })
            )
        except:
            return redirect(reverse('orders:product_list'))
    context = {
        'order': existing_order,
        # 'client_token': client_token,
        'STRIPE_PUBLISHABLE_KEY': publishKey
    }
    return render(request, 'orders/checkout.html', context)


@login_required()
def update_transaction_records(request, token):
    # get the order being processed
    order_to_purchase = get_user_pending_order(request)
    # update the placed order
    order_to_purchase.is_ordered=True
    order_to_purchase.date_ordered=datetime.datetime.now()
    order_to_purchase.save()
    # get all items in the order - generates a queryset
    order_items = order_to_purchase.items.all()
    # update order items
    order_items.update(is_ordered=True, date_ordered=datetime.datetime.now())
    # Add products to user profile
    user_profile = get_object_or_404(Profile, user=request.user)

    # get the products from the items
    order_products = [item.product for item in order_items]
    user_profile.ebooks.add(*order_products)
    user_profile.save()

    # create a transaction
    transaction = Transaction(profile=request.user.profile,
                            token=token,
                            order_id=order_to_purchase.id,
                            amount=order_to_purchase.get_cart_total(),
                            success=True)
    transaction.save()
    messages.info(request, "Thank you! Your purchase was successful!")
    return redirect(reverse('accounts:my_profile'))


def success(request, **kwargs):
    return render(request, 'orders/purchase_success.html', {})
