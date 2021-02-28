# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import (
    Comment,
    Ingredient,
    IngredientQuantity,
    Recipe,
    RecipeCategory,
    RestrictedDiet,
)

# Register your models here.


admin.site.register(Ingredient)
admin.site.register(Recipe)
admin.site.register(RestrictedDiet)
admin.site.register(RecipeCategory)
admin.site.register(IngredientQuantity)
admin.site.register(Comment)
