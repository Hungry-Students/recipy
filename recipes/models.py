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
    ingredients = models.ManyToManyField(Ingredient, through='IngredientQuantity')
    
    #URL used to manage duplicatas
    url = models.CharField(max_length=400, blank=True, null=True)

    # Properties from https://schema.org/Recipe
    cook_time = models.IntegerField(blank=True, null=True) #in minutes
    cooking_method = models.CharField(max_length=200, blank=True, null=True)
    category = models.ForeignKey(RecipeCategory, on_delete=models.PROTECT, blank=True, null=True)
    instructions = models.CharField(max_length=10000)
    quantity = models.IntegerField(blank=True, null=True)
    quantity_unit = models.CharField(max_length=200, blank=True, null=True)
    diets = models.ManyToManyField(RestrictedDiet)

    def __str__(self):
        return self.name

class IngredientQuantity(models.Model):
	quantity = models.IntegerField(blank=True, null=True)
	quantity_unit = models.CharField(max_length=200, blank=True, null=True)

	recipe = models.ForeignKey(Recipe, on_delete=models.PROTECT)
	ingredient = models.ForeignKey(Ingredient, on_delete=models.PROTECT)

	def __str__(self):
		return str(self.recipe)+'/'+str(self.ingredient)
