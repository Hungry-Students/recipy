# -*- coding: utf-8 -*-
from annoying.fields import AutoOneToOneField
from django.db import models

import activities.activities as acts
from users.models import URIs, User, uri


class Ingredient(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return str(self.name)


class RecipeCategory(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return str(self.name)


class RestrictedDiet(models.Model):
    # https://schema.org/RestrictedDiet
    name = models.CharField(max_length=200)

    def __str__(self):
        return str(self.name)


class Recipe(models.Model):
    ap_id = models.TextField(null=True)
    remote = models.BooleanField(default=False)

    name = models.CharField(max_length=200)
    ingredients = models.ManyToManyField(Ingredient, through="IngredientQuantity")

    # URL used to manage duplicatas
    url = models.CharField(max_length=400, blank=True, null=True)

    # Properties from https://schema.org/Recipe
    cook_time = models.IntegerField(blank=True, null=True)  # in minutes
    cooking_method = models.CharField(max_length=200, blank=True, null=True)
    category = models.ForeignKey(
        RecipeCategory, on_delete=models.PROTECT, blank=True, null=True
    )
    instructions = models.CharField(max_length=10000)
    quantity = models.IntegerField(blank=True, null=True)
    quantity_unit = models.CharField(max_length=200, blank=True, null=True)
    diets = models.ManyToManyField(RestrictedDiet)
    
    #number of cookbooks referencing this recipe. Used to know when to remove an unused recipe
    number_references = models.IntegerField(default=1)
    
    @property
    def cook_time_minutes(self):
    	if self.cook_time:
    		return self.cook_time%60
    	return 0
    	
    @property
    def cook_time_hours(self):
    	if self.cook_time:
    		return self.cook_time//60
    	return 0

    def __str__(self):
        return str(self.name)

    def get_yield(self):
        return "{} {}".format(self.quantity, self.quantity_unit)

    def to_activitystream(self):
        igdt_list = IngredientQuantity.objects.filter(recipe=self)
        recipe_as = {
            # "attributedTo": recipe.author,
            "name": str(self),
            "duration": "PT{}M".format(self.cook_time),
            "cookingMethod": str(self.cooking_method),
            "recipeCategory": str(self.category),
            "recipeIngredients": [
                igdt.to_activitystream().to_json() for igdt in igdt_list
            ],
            "content": str(self.instructions),
            "recipeYield": self.get_yield(),
            # "tag": [diet.to_activitystream for diet in self.diets.all()],
        }
        return acts.extended.Recipe(**recipe_as)


class IngredientQuantity(models.Model):
    quantity = models.IntegerField(blank=True, null=True)
    quantity_unit = models.CharField(max_length=200, blank=True, null=True)

    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.PROTECT)

    def get_quantity(self):
        return "{} {}".format(self.quantity, self.quantity_unit)

    def to_activitystream(self):
        ingredient_as = {"name": self.ingredient.name, "quantity": self.get_quantity()}
        return acts.extended.Ingredient(**ingredient_as)

    def __str__(self):
        return str(self.recipe) + "/" + str(self.ingredient)


class Comment(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="comments"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_on"]

    def __str__(self):
        return str(self.content)[:30]


class Cookbook(models.Model):
    owner = AutoOneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="cookbook",
    )
    recipes = models.ManyToManyField(Recipe, through="Entry")

    def __str__(self):
        return str(self.owner)


class Entry(models.Model):
    ap_id = models.TextField(null=True)
    remote = models.BooleanField(default=False)

    recipe = models.ForeignKey(Recipe, on_delete=models.PROTECT)
    cookbook = models.ForeignKey(Cookbook, on_delete=models.CASCADE)

    @property
    def uris(self):
        if self.remote:
            ap_id = self.ap_id
        else:
            ap_id = uri("recipes:cookbook-entry", self.cookbook.owner, self.id)
        return URIs(id=ap_id)

    def to_activitystream(self):
        recipe_as = self.recipe.to_activitystream().to_json()
        return acts.Entry(attributed_to=self.cookbook.owner.ap_id, parent=recipe_as)

    def __str__(self):
        return self.recipe.name
