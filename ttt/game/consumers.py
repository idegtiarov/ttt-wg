from collections import defaultdict
import random

from channels.generic.websocket import AsyncWebsocketConsumer
import json

WINS = ((0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6))


class Gambling(object):
    gambling = defaultdict(set)

    def __get__(self, obj, objtype):
        return self.gambling

    def __set__(self, obj, value):
        self.gambling = defaultdict(set)


class DeskConsumer(AsyncWebsocketConsumer):

    gambling = Gambling()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.init_set = set(range(9))
        self.desk_name = None
        self.desk_group_name = None

    async def connect(self):
        self.desk_name = self.scope['url_route']['kwargs']['desk_name']
        self.desk_group_name = f'desk_{self.desk_name}'

        # Join desk group
        await self.channel_layer.group_add(
            self.desk_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, code):
        # left desk group
        await self.channel_layer.group_discard(
            self.desk_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data=None):
        draw, ai_win = None, None
        data = json.loads(text_data)
        if data.get("user"):
            await self.channel_layer.group_send(
                self.desk_group_name,
                {
                    'type': 'desk_message',
                    'user': data.get('user'),
                    'loop': data.get('loop'),
                }
            )
            return
        username = self.scope["user"].username
        print(f'Checking the scope {username}')
        if data.get('new_game'):
            self.gambling = defaultdict(set)
            await self.channel_layer.group_send(
                self.desk_group_name,
                {
                    'type': 'desk_message',
                    'new_game': True
                }
            )
            return
        enemy = data.get('enemy', False)
        choice = data.get('id')
        player_set = self.gambling[username]
        player_set.add(int(data['id']))
        player_win = check_result(player_set, username, player=True)
        if not player_win:
            second_player = [v for k, v in self.gambling.items() if k != username]
            choice_list = list(
                self.init_set - player_set - (second_player[0] if second_player else set())
            )
            print(choice_list)
            if choice_list:
                if not enemy:
                    choice = None
                    for win in WINS:
                        win_diff = set(win) - player_set
                        if len(win_diff) == 1 and (win_diff - self.gambling['ai']):
                            choice = win_diff.pop()
                            break
                    choice = choice or random.choice(choice_list)
                    self.gambling['ai'].add(choice)
                    ai_win = check_result(self.gambling['ai'], username)
            else:
                draw = {'win': 'draw'}
        print(self.gambling)

        # Send message to the group
        await self.channel_layer.group_send(
            self.desk_group_name,
            {
                'type': 'desk_message',
                'username': username,
                'char': data['char'],
                'id': choice,
                'result': player_win or ai_win or draw,
            }
        )

    async def desk_message(self, event):
        user = event.get('user')
        if user:
            await self.send(text_data=json.dumps({
                'user': user,
                'loop': event.get('loop'),
            }))
            return
        new_game = event.get('new_game')
        if new_game:
            await self.send(text_data=json.dumps({
                'new_game': new_game,
            }))
            return

        id = event['id']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'id': id,
            'username': event.get('username'),
            'result': event.get('result')
        }))


def check_result(check_set, username, player=False):

    for win in WINS:
        if check_set >= set(win):
            return {'win': True if player else False, 'player': username, 'ids': win}
