from django.db import models


class Item(models.Model):
    text = models.TextField(default='')


class List(models.Model):
    pass
