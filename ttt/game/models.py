from collections import defaultdict

from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField
from django.db import models


def default_dict_set():
    return defaultdict(set)


class Progress(models.Model):
    """
    The model for User's progress.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ai = JSONField(default=default_dict_set, blank=True)
    enemy = JSONField(default=default_dict_set, blank=True)

    def __str__(self):
        return "<{}'s progress>".format(self.user)
