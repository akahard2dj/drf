from django.db import models
#from core.models.donkey_user import DonkeyUser
#from core.models.name_tag import NameTag


class University(models.Model):
    name = models.CharField(null=False, max_length=100, unique=True)
    domain = models.CharField(null=False, max_length=100)


class Department(models.Model):
    name = models.CharField(null=False, max_length=100, unique=True)
