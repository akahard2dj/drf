from django.db import models


class University(models.Model):
    name = models.CharField(null=False, max_length=100, unique=True)
    domain = models.CharField(null=False, max_length=100)


class Department(models.Model):
    name = models.CharField(null=False, max_length=100, unique=True)
