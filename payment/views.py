import uuid
from decimal import Decimal

import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from hotel.models import Booking
from .models import Payment


def _booking_total_amount(booking):
    if booking.check_in and booking.check_out:
        stay_nights = max(1, (booking.check_out.date() - booking.check_in.date()).days)
    else:
        stay_nights = 1
    room_rate = booking.room.price_per_night or Decimal("0.00")
    return room_rate * stay_nights


@login_required
def checkout_latest(request):
    booking = Booking.objects.filter(user=request.user).order_by("-check_in", "-id").first()
    if not booking:
        messages.error(request, "You need at least one booking before checkout.")
        return redirect("hotel:BookingListView")
    return redirect("payment:pay", booking_id=booking.pk)


@login_required
def pay(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id)
    if not request.user.is_staff and booking.user != request.user:
        messages.error(request, "You are not allowed to pay for this booking.")
        return redirect("hotel:BookingListView")

    amount = _booking_total_amount(booking)
    reference = uuid.uuid4().hex

    payment = Payment.objects.create(
        user=booking.user,
        booking=booking,
        amount=amount,
        reference=reference,
        status=Payment.STATUS_PENDING,
    )

    callback_url = request.build_absolute_uri(reverse("payment:verify"))
    paystack_public_key = getattr(settings, "PAYSTACK_PUBLIC_KEY", "")
    email = booking.user.email if booking.user and booking.user.email else ""

    context = {
        "booking": booking,
        "payment": payment,
        "reference": reference,
        "amount_kobo": int(amount * Decimal("100")),
        "amount_display": amount,
        "email": email,
        "paystack_public_key": paystack_public_key,
        "callback_url": callback_url,
    }
    return render(request, "payment/pay.html", context)


@login_required
def verify(request):
    reference = request.GET.get("reference")
    if not reference:
        messages.error(request, "Missing payment reference.")
        return redirect("hotel:BookingListView")

    payment = get_object_or_404(Payment, reference=reference)
    if not request.user.is_staff and payment.user != request.user:
        messages.error(request, "You are not allowed to verify this payment.")
        return redirect("hotel:BookingListView")

    secret_key = getattr(settings, "PAYSTACK_SECRET_KEY", "")
    headers = {"Authorization": f"Bearer {secret_key}"}
    url = f"https://api.paystack.co/transaction/verify/{reference}"

    try:
        response = requests.get(url, headers=headers, timeout=20)
        data = response.json()
        transaction_data = data.get("data", {})
        status = str(transaction_data.get("status", "")).lower()
        amount_paid = Decimal(str(transaction_data.get("amount", 0))) / Decimal("100")

        if status == "success" and amount_paid == payment.amount:
            payment.status = Payment.STATUS_COMPLETED
            payment.save(update_fields=["status", "updated_at"])
            return render(request, "payment/success.html", {"payment": payment, "booking": payment.booking})

        payment.status = Payment.STATUS_FAILED
        payment.save(update_fields=["status", "updated_at"])
        return render(request, "payment/failed.html", {"payment": payment, "booking": payment.booking})
    except Exception:
        payment.status = Payment.STATUS_FAILED
        payment.save(update_fields=["status", "updated_at"])
        return render(request, "payment/failed.html", {"payment": payment, "booking": payment.booking})
