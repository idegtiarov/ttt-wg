from django.urls import path

from game.views import desk, index, progress, room

urls_list = [
    path('', index, name='index'),
    path('room_to_play/', room, name='room_to_play'),
    path('update_progress/', progress, name='update_progress'),
    path('<str:desk_name>/', desk, name='desk'),
]

urlpatterns = (urls_list, 'game')
