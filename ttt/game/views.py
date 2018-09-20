import json
from logging import getLogger
import re

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.core.cache import cache
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.utils.safestring import mark_safe
import requests

from config.settings import TTT_WAIT_TIME
from game.forms import AuthForm

log = getLogger(__name__)


@login_required
def index(request):
    return render(request, 'game/index.html', {'url': reverse('game:room_to_play'), 'latency': TTT_WAIT_TIME})


def desk(request, desk_name):
    context = {
        'desk_name_json': mark_safe(json.dumps(desk_name)),
        'latency': TTT_WAIT_TIME,
        'username': request.user.username,
    }
    print(request.user)
    return render(
        request, 'game/desk.html', context
    )


def room(request):
    room_id = cache.get('game_room')
    wait = True

    log.debug(f"The room id is: {room_id}")
    if not room_id:
        room_id = get_random_string(length=10)
        cache.set('game_room', room_id, TTT_WAIT_TIME)
    # else:
        # cache.delete('game_room')
        # return HttpResponse(status=400)
    return JsonResponse(status=200, data={'room_id': room_id, 'wait': wait})


class LoginGameView(LoginView):
    form_class = AuthForm


login = LoginGameView.as_view()
