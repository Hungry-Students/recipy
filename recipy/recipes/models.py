from django.db import models

# Create your models here.

class Ingredient(models.Model):
	ingredient_name = models.CharField(max_length=200)
	
	def __str__(self):
		return self.ingredient_name
	
class Recipe(models.Model):
	recipe_name = models.CharField(max_length=200)
	ingredients = models.ManyToManyField(Ingredient)
	
	def __str__(self):
		return self.recipe_name
