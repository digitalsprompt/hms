from django.urls import path

from . import views

app_name = "payment"

urlpatterns = [
    path("checkout/", views.checkout_latest, name="checkout_latest"),
    path("pay/<int:booking_id>/", views.pay, name="pay"),
    path("verify/", views.verify, name="verify"),
]
