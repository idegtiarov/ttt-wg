from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path('ws/desk/<str:desk_name>/', consumers.DeskConsumer)
]
