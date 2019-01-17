from django.urls import path

from . import views

app_name = 'orders'

urlpatterns = [
    path("", views.product_list, name='product_list'),
    path("home/", views.home, name='home'),
    path("registration/", views.registration_view, name='registration'),
    path("login/", views.login_view, name='login'),
    path("logout/", views.logout_view, name='logout'),
    path("add-to-cart/<item_id>/", views.add_to_cart, name="add_to_cart"),
    path("order-summary/", views.order_details, name="order_summary"),
    path("success/", views.success, name='purchase_success'),
    path("item/delete/<item_id>/", views.delete_from_cart, name='delete_item'),
    path("checkout/", views.checkout, name='checkout'),
    path("update-transaction/<token>/", views.update_transaction_records,
        name='update_records'),
]
