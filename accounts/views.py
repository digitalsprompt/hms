import re

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import ProfileUpdateForm, UserUpdateForm
from .models import Profile
from payment.models import Payment


@login_required
def dashboard(request):
    return redirect('hotel:index')


@login_required
def profile_details(request):
    profile = get_object_or_404(Profile, user=request.user)
    booking_history = (
        Payment.objects.filter(user=request.user, status=Payment.STATUS_COMPLETED)
        .select_related("booking", "booking__room")
        .order_by("-updated_at")
    )
    return render(
        request,
        'profile.html',
        {
            'profile': profile,
            'booking_history': booking_history,
        },
    )


@login_required
def profile_update(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile_details')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }

    return render(request, 'profile_update.html', context)


@require_POST
def password_reset_token_redirect(request):
    raw_value = request.POST.get("reset_token", "")
    cleaned = re.sub(r"\s+", "", raw_value)
    cleaned = cleaned.replace("=\r", "").replace("=\n", "").replace("=", "")

    match = re.search(r"/password/reset/key/([^/]+)/?$", cleaned)
    if match:
        cleaned = match.group(1)

    if not cleaned or "-" not in cleaned:
        messages.error(request, "Enter a valid reset token or reset link.")
        return redirect("account_reset_password")

    uidb36, key = cleaned.split("-", 1)
    return redirect("account_reset_password_from_key", uidb36=uidb36, key=key)
