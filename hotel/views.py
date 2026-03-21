# from unicodedata import category

from django.contrib import messages
from django.shortcuts import render, HttpResponse, redirect
from django.views.generic import ListView, FormView, View, DeleteView
from django.urls import reverse, reverse_lazy
from .models import Room, Booking 
from .forms import AvailabilityForm
from hotel.booking_functions.availability import check_availability


# Create your views here.
def index(request):
    room_list = Room.objects.all()
    
    context = {
        'room_list': room_list
    }
    
    return render(request, 'index.html', context)

def RoomListView(request):
    room_list = Room.objects.all()
    context = {
        "room_list": room_list,
    }
    return render(request, 'room_list_view.html', context)

class BookingListView(ListView):
    model = Booking
    template_name = 'booking_list_view.html'
    
    def get_queryset(self, *args, **kwargs):
        if self.request.user.is_staff:
            booking_list = Booking.objects.exclude(payments__status="Completed").distinct()
            return booking_list
        else:
            booking_list = (
                Booking.objects.filter(user=self.request.user)
                .exclude(payments__status="Completed")
                .distinct()
            )
            return booking_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        bookings = context["booking_list"]
        total_bookings = bookings.count() if hasattr(bookings, "count") else len(bookings)
        total_nights = 0
        total_guests = 0
        total_due = 0

        for booking in bookings:
            if booking.check_in and booking.check_out:
                stay_nights = max(1, (booking.check_out.date() - booking.check_in.date()).days)
            else:
                stay_nights = 0
            total_nights += stay_nights
            total_guests += booking.room.capacity or 0
            if booking.room.price_per_night:
                total_due += stay_nights * booking.room.price_per_night

        context.update(
            {
                "total_bookings": total_bookings,
                "total_nights": total_nights,
                "total_guests": total_guests,
                "total_due": total_due,
                "checkout_url": reverse("payment:checkout_latest"),
            }
        )
        return context

class RoomDetailView(View):
    def get(self, request, *args, **kwargs):
        category = self.kwargs.get('category', None)
        form = AvailabilityForm()
        room_list = Room.objects.filter(category=category)
        
        if len(room_list)>0:
            room = room_list[0]
            room_category = dict(room.ROOM_CATEGORIES).get(room.category, None)
            context = {
                'room': room,
                'room_category' : room_category,
                'form': form,
            }
            return render(request, 'room_detail_view.html', context)
        else:
            return HttpResponse("category does not exist")
    
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f"{reverse('account_login')}?next={request.path}")

        category = self.kwargs.get('category', None)
        room_list = Room.objects.filter(category=category)
        form = AvailabilityForm(request.POST)
        
        if form.is_valid():
            data = form.cleaned_data
        else:
            messages.error(request, "Please enter valid booking dates before continuing.")
            return redirect(request.path)
        
        available_room = []
        for room in room_list:
            if check_availability(room, data['check_in'], data['check_out']):
                available_room.append(room)
                
        
        if len(available_room) > 0:
            room = available_room[0]
            booking = Booking.objects.create(
                user=self.request.user,
                room=room,
                check_in=data['check_in'],
                check_out=data['check_out']
            )
            booking.save()
            messages.success(request, "Room booked successfully. Continue to payment to complete your reservation.")
            return redirect("payment:pay", booking_id=booking.pk)
        else:
            messages.error(request, "No rooms are available for the selected category and dates.")
            return redirect("hotel:RoomListView")


class CancelBookingView(DeleteView):
    model = Booking
    template_name = 'booking_cancel_view.html'
    success_url = reverse_lazy('hotel:BookingListView')

# class BookingView(FormView):
#     form_class = AvailabilityForm
#     template_name = 'availability_form.html'
    
#     def form_valid(self, form):
#         data = form.cleaned_data
#         room_list = Room.objects.filter(category=data['room_category'])
#         available_room = []
#         for room in room_list:
#             if check_availability(room, data['check_in'], data['check_out']):
#                 available_room.append(room)
                
        
#         if len(available_room) > 0:
#             room = available_room[0]
#             booking = Booking.objects.create(
#                 user=self.request.user,
#                 room=room,
#                 check_in=data['check_in'],
#                 check_out=data['check_out']
#             )
#             booking.save()
#             return HttpResponse(booking)
#         else:
#             return HttpResponse("No rooms available for the selected category and dates.")
