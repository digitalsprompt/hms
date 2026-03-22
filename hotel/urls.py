from django.urls import path
from . import views
from .views import RoomListView, BookingListView, RoomDetailView, CancelBookingView

app_name = 'hotel'

urlpatterns = [
    path('', views.index, name= 'index'),
    path('room_list/', RoomListView, name='RoomListView'),
    path('booking_list/', BookingListView.as_view(), name='BookingListView'),
    path('room/<int:pk>/', RoomDetailView.as_view(), name='RoomDetailView'),
    path('booking/cancel/<pk>', CancelBookingView.as_view(), name='CancelBookingView'),
]
