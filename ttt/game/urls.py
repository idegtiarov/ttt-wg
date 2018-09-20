from django.urls import path

from game.views import desk, index, room

urls_list = [
    path('', index, name='index'),
    path('room_to_play/', room, name='room_to_play'),
    path('<str:desk_name>/', desk, name='desk'),
]

urlpatterns = (urls_list, 'game')
