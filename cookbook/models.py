# -*- coding: utf-8 -*-
from django.db import models
from recipes.models import Recipe
from users.models import User

class Cookbook(models.Model):
    owner = models.OneToOneField(
        User,
        on_delete = models.CASCADE,
        primary_key = True,
        related_name = 'cookbook',
    )
    recipes = models.ManyToManyField(Recipe, through='Entry')

    def __str__(self):
        possesive = '' if self.owner.username[-1] == 's' else 's'
        return "%s'%s cookbook" % (self.owner.username, possesive)

class Entry(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.PROTECT)
    cookbook = models.ForeignKey(Cookbook, on_delete=models.CASCADE)
    # TODO: in the future, add comments (and likes ?)

    def __str__(self):
        return self.recipe.name
