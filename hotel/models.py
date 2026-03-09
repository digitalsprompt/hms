from django.db import models
from django.conf import settings

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
        return f"Room {self.room_number} - {self.category} with {self.beds} beds for {self.capacity} people"

class Booking(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    check_in = models.DateTimeField(null=True, blank=True)
    check_out = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Booking for {self.user} in {self.room} from {self.check_in} to {self.check_out}"