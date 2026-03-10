from django.db import models
from django.conf import settings
from django.urls import reverse_lazy

# Create your models here.
class Room(models.Model):
    ROOM_CATEGORIES = (
        ('Single', 'Single'),
        ('Dual', 'Dual'),
        ('Suite', 'Suite'),
        ('Deluxe', 'Deluxe'),
        ('Family', 'Family'),
    )
    room_number = models.IntegerField()
    category = models.CharField(max_length=20, choices=ROOM_CATEGORIES)
    beds = models.IntegerField()
    capacity = models.IntegerField()
    
    def __str__(self):
        return f"{self.room_number}. {dict(self.ROOM_CATEGORIES).get(self.category)} Beds = {self.beds} People = {self.capacity}"

class Booking(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    check_in = models.DateTimeField(null=True, blank=True)
    check_out = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"From = {self.check_in.strftime('%d-%b-%y %H:%M')} To = {self.check_out.strftime('%d-%b-%y %H:%M')}"
    
    def get_room_category(self):
        room_categories = dict(self.room.ROOM_CATEGORIES)
        room_category = room_categories.get(self.room.category)
        return room_category
    
    def get_cancel_booking_url(self):
        return reverse_lazy('hotel:CancelBookingView', args=[self.pk])