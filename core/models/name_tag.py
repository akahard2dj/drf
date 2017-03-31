from django.db import models

from core.models.category import (University, Department)
from core.models.donkey_user import DonkeyUser


class NameTag(models.Model):
    group_title = models.CharField(null=False, max_length=100, unique=True)
    user = models.ManyToManyField(DonkeyUser, null=True)
    university = models.ManyToManyField(University, null=True)
    department = models.ManyToManyField(Department, null=True)