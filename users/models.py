# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import AbstractUser
from recipes.models import Recipe

class User(AbstractUser):
    recipes = models.ManyToManyField(Recipe, through='RecipeDate')

    def __str__(self):
        return self.username


class RecipeDate(models.Model):
    date_added = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    recipe = models.ForeignKey(Recipe, on_delete=models.PROTECT)

    def __str__(self):
        return self.recipe.name
