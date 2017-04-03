from django.db import models

from core.models.category import (University, Department)


class BulletinBoard(models.Model):
    board_status = models.IntegerField(null=False, default=0)
    title = models.CharField(null=False, max_length=200)
    desc = models.CharField(null=False, max_length=300)
    university = models.ManyToManyField(University, null=True)
    department = models.ManyToManyField(Department, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
