import json

from ddt import data, ddt, unpack
from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse


@ddt
class DeskTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='test')
        cls.user.set_password('test')
        cls.user.save()

    def setUp(self):
        self.client.login(username='test', password='test')

    def test_index_redirect_to_login(self):
        self.client.logout()
        response = self.client.get(reverse('game:index'))
        self.assertRedirects(response, reverse('login') + '?next=/game/')

    def test_logined_user_redirected_to_game(self):
        response = self.client.get(reverse('index'))
        self.assertRedirects(response, reverse('game:index'))

    def test_desk_required_authorization(self):
        self.client.logout()
        url = reverse('game:desk', args=['test_desk'])
        response = self.client.get(url)
        self.assertRedirects(response, reverse('login') + f'?next={url}')

    def test_user_take_same_room(self):
        response_one = json.loads(self.client.get(reverse('game:room_to_play')).content)
        response_two = json.loads(self.client.get(reverse('game:room_to_play')).content)
        self.assertEqual(response_one['room_id'], response_two['room_id'])

    @override_settings(TTT_WAIT_TIME=0)
    def test_user_take_different_rooms_if_TTT_WAIT_TIME_over(self):
        response_one = json.loads(self.client.get(reverse('game:room_to_play')).content)
        response_two = json.loads(self.client.get(reverse('game:room_to_play')).content)
        self.assertNotEqual(response_one['room_id'], response_two['room_id'])

    def test_third_user_take_different_room(self):
        response_one = json.loads(self.client.get(reverse('game:room_to_play')).content)
        response_two = json.loads(self.client.get(reverse('game:room_to_play')).content)
        response_three = json.loads(self.client.get(reverse('game:room_to_play')).content)
        self.assertEqual(response_one['room_id'], response_two['room_id'])
        self.assertNotEqual(response_one['room_id'], response_three['room_id'])

    @unpack
    @data(
        {'enemy': False, 'win': 1, 'lost': 0, 'draw': 0, 'expected': [(100, 0, 0), (0, 0, 0)]},
        {'enemy': False, 'win': 0, 'lost': 1, 'draw': 0, 'expected': [(0, 100, 0), (0, 0, 0)]},
        {'enemy': False, 'win': 0, 'lost': 0, 'draw': 1, 'expected': [(0, 0, 100), (0, 0, 0)]},
        {'enemy': False, 'win': 1, 'lost': 1, 'draw': 1, 'expected': [(33, 33, 33), (0, 0, 0)]},
        {'enemy': False, 'win': 10, 'lost': 5, 'draw': 5, 'expected': [(50, 25, 25), (0, 0, 0)]},
        {'enemy': True, 'win': 1, 'lost': 0, 'draw': 0, 'expected': [(0, 0, 0), (100, 0, 0)]},
        {'enemy': True, 'win': 0, 'lost': 1, 'draw': 0, 'expected': [(0, 0, 0), (0, 100, 0)]},
        {'enemy': True, 'win': 0, 'lost': 0, 'draw': 1, 'expected': [(0, 0, 0), (0, 0, 100)]},
        {'enemy': True, 'win': 1, 'lost': 1, 'draw': 1, 'expected': [(0, 0, 0), (33, 33, 33)]},
        {'enemy': True, 'win': 10, 'lost': 5, 'draw': 5, 'expected': [(0, 0, 0), (50, 25, 25)]},
    )
    def test_progress(self, enemy, win, lost, draw, expected):
        expected_result = {
            'ai': 'Wins: {}%; Losts: {}%; Draws: {}%'.format(*expected[0]),
            'enemy': 'Wins: {}%; Losts: {}%; Draws: {}%'.format(*expected[1])
        }
        url = reverse('game:update_progress')
        payload = {
            'progress': json.dumps(
                {
                    'enemy': enemy,
                    'wins': {
                        'win': win, 'lost': lost, 'draw': draw
                    },
                })
        }
        response = self.client.post(url, data=payload)
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data, expected_result)
