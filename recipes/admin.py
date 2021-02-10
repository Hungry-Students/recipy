# -*- coding: utf-8 -*-
from django.contrib import admin

# Register your models here.

from.models import Ingredient, Recipe, RecipeCategory, RestrictedDiet, IngredientQuantity

admin.site.register(Ingredient)
admin.site.register(Recipe)
admin.site.register(RestrictedDiet)
admin.site.register(RecipeCategory)
admin.site.register(IngredientQuantity)
