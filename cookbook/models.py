# -*- coding: utf-8 -*-
from django.db import models
from recipes.models import Recipe
from users.models import User
from django.utils.translation import gettext as _

class Cookbook(models.Model):
    owner = models.OneToOneField(
        User,
        on_delete = models.CASCADE,
        primary_key = True,
        related_name = 'cookbook',
    )
    recipes = models.ManyToManyField(Recipe, through='Entry')

    def __str__(self):
        return str(self.owner)

class Entry(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.PROTECT)
    cookbook = models.ForeignKey(Cookbook, on_delete=models.CASCADE)
    # TODO: in the future, add comments (and likes ?)

    def __str__(self):
        return self.recipe.name
