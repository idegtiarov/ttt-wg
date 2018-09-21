import json
from logging import getLogger

from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.core.cache import cache
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.utils.safestring import mark_safe
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from config.settings import TTT_WAIT_TIME
from game.forms import AuthForm
from game.models import Progress

log = getLogger(__name__)


@login_required
def index(request):
    """
    View for the index page.
    """
    return render(request, 'game/index.html', {'url': reverse('game:room_to_play'), 'latency': TTT_WAIT_TIME})


@login_required
def desk(request, desk_name):
    """
    View for the desk page.

    :param desk_name: unique desk identifier.
    """
    context = {
        'desk_name_json': mark_safe(json.dumps(desk_name)),
        'latency': TTT_WAIT_TIME,  # time in seconds player is waiting for the opponent.
        'username': request.user.username,
        'url': reverse('game:update_progress'),
    }
    return render(
        request, 'game/desk.html', context
    )


@login_required
def room(request):
    """
    Assistive view. Implement naively designed queue.
    """
    room_id = cache.get('game_room')

    if not room_id:
        room_id = get_random_string(length=10)
        cache.set('game_room', room_id, TTT_WAIT_TIME)
    else:
        cache.delete('game_room')
    log.debug(f"The room id is: {room_id}")
    return JsonResponse(status=200, data={'room_id': room_id})


def _update_user_data(user_progress, wins):
    """
    Update user's progress on the database level.

    :param user_progress: progress model field which is updated.
    :param wins: dict with the archived result.
    """
    for k, v in wins.items():
        if not user_progress.get(k):
            user_progress[k] = v
        else:
            user_progress[k] += v


def _calculate_stats(progress):
    """
    Calculate the stats based on all user's games.

    :param progress: user's progress model.
    :return: dict which contains the stats strings.
    """
    draw_result = 'Wins: {}%; Losts: {}%; Draws: {}%'
    default_values = (0, 0, 0)
    result = {}
    for key in ('enemy', 'ai'):
        game_sum = 0
        for val in getattr(progress, key).values():
            game_sum += val
        result[key] = draw_result.format(
            *(
                int(getattr(progress, key)['win'] / game_sum * 100),
                int(getattr(progress, key)['lost'] / game_sum * 100),
                int(getattr(progress, key)['draw'] / game_sum * 100),
            ) if game_sum else default_values
        )
    return result


@require_POST
@login_required
@csrf_exempt
def progress(request):
    """
    Assistive view. Do user's progress update on the database level.

    :return: json response with the user's stats.
    """
    progrs, _ = Progress.objects.get_or_create(user=request.user)
    data = json.loads(request.POST.get('progress'))
    enemy = data.get('enemy')
    _update_user_data(progrs.enemy if enemy else progrs.ai, data['wins'])
    progrs.save()

    result = _calculate_stats(progrs)
    return JsonResponse(status=200, data=result)


class LoginGameView(LoginView):
    form_class = AuthForm


login = LoginGameView.as_view()
