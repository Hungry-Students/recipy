from django import forms
from django.forms import ModelForm, Textarea
from .models import Recipe, Ingredient, IngredientQuantity

class RecipeForm(ModelForm):
	class Meta:
		model = Recipe
		fields = ['name', 'quantity', 'quantity_unit', 'instructions']
		widgets = {
			'instructions': Textarea(attrs={'cols': 80, 'rows': 20}),
		}
	
	def save(self):
		#building new recipe
		r = self.instance
		r.name = self.cleaned_data['name']
		r.instructions = self.cleaned_data['instructions']
		r.quantity = self.cleaned_data['quantity']
		r.quantity_unit = self.cleaned_data['quantity_unit']
		r.save()
		return r
		
		r.ingredients.all().delete()
		for i in range(1,6):
			add_ingredient(r, self.cleaned_data['ingredient_'+str(i)], 5, 'x')
		"""
		for ingredient_name in ingredient_quantities.keys():
		    add_ingredient(new_recipe, ingredient_name, ingredient_quantities[ingredient_name], ingredient_quantity_units[ingredient_name])
		"""
