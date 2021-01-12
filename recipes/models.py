# -*- coding: utf-8 -*-
from django.db import models

# Create your models here.

class Ingredient(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class RecipeCategory(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class RestrictedDiet(models.Model):
    # https://schema.org/RestrictedDiet
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(max_length=200)
    ingredients = models.ManyToManyField(Ingredient)

    # Properties from https://schema.org/Recipe
    cook_time = models.DurationField()
    cooking_method = models.CharField(max_length=200)
    category = models.ForeignKey(RecipeCategory, on_delete=models.PROTECT)
    instruction = models.FileField(upload_to=None, max_length=100)
    quantity = models.IntegerField()
    quantity_unit = models.CharField(max_length=200)
    diet = models.ForeignKey(RestrictedDiet, on_delete=models.PROTECT)

    def __str__(self):
        return self.name
