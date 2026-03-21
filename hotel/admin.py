from django.contrib import admin
from .models import Room, Booking


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("room_number", "category", "capacity", "beds", "price_per_night", "image")
    list_filter = ("category",)
    search_fields = ("room_number", "category", "tag1", "tag2", "tag3")


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("user", "room", "check_in", "check_out")
