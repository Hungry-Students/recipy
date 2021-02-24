# -*- coding: utf-8 -*-
from django import forms
import re
from django.forms import Form, Textarea, ModelForm
from .models import Recipe, Ingredient, IngredientQuantity, RestrictedDiet, Comment, RecipeCategory
from .parser import IngredientParser, YieldsParser
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

class CustomNumberInput(forms.NumberInput):
	def __init__(self, label, attrs=None):
		self.label = label
		super().__init__(attrs)
				
	def render(self, name, value, attrs = None ,renderer=None):
		r = super().render(name, value, attrs,renderer) + self.label
		return r

class CookTimeWidget(forms.MultiWidget):
	def __init__(self, attrs=None):
		widgets = {
			'hours' : CustomNumberInput('hours', attrs={'size' : 10, 'min_value' : 0, 'initial' : 0}), 
			'minutes' : CustomNumberInput('minutes', attrs={'size' : 10, 'min_value' : 0, 'initial' : 0}),
		}
		super().__init__(widgets, attrs)
	
	def render(self, name, value, attrs = None ,renderer=None):
		hours_render = self.widgets[0].render(name+'_hours', value, attrs, renderer)
		minutes_render = self.widgets[1].render(name+'_minutes', value, attrs, renderer)
		return hours_render+minutes_render
		
	def decompress(self, value):
		if value:
			return [value//60, value%60]
		else:
			return [None,None]
			
class CookTimeField(forms.MultiValueField):
	widget = CookTimeWidget
	
	def __init__(self, **kwargs):
		fields = (forms.IntegerField(required=False, min_value=0), forms.IntegerField(required=False, min_value=0))
		super().__init__(fields=fields, require_all_fields=False, **kwargs)
		
	def compress(self, data_list):
		r=0
		if data_list:
			if data_list[0]:
				r+=60*data_list[0]
			if data_list[1]:
				r+=data_list[1]
			return r
		return None #note : if no input at all, empty data_list is passed

class IngredientObject():
	"""Used to easily work with all informations concerning 1 ingredient"""
	def __init__(self, name='', quantity = None, quantity_unit=None, exclude=False):
		self.name = name
		self.quantity = quantity
		self.quantity_unit = quantity_unit
		self.exclude = exclude
		
	def format(self):
		if self.quantity:
			self.quantity = str(self.quantity)
		return self
		
	def to_python(self):
		if self.quantity:
			self.quantity = int(self.quantity)
		return self

		
class IngredientsWidget(forms.Widget):
	template_name = 'recipes/ingredients_widget_template.html'
	
	def value_from_datadict(self, data, files, name):
		return_list = []
		print("extracting values")
		for e in data.keys():
			m = re.search(name+'_(?P<id>[0-9]+)_name', e)
			if m is not None:
				ingredient_id = m.group('id')
				ingredient_name = data[e].lower() #note : we enforce lower case here for ingredient name
			
				p = IngredientParser()
				quantity, quantity_unit = p.parse_quantity(data.get(name+'_'+ingredient_id+'_quantity', ''))
			
				exclude = bool(data.get(name+'_exclude_'+ingredient_id,None))
			
				return_list.append(IngredientObject(name=ingredient_name, quantity=quantity, quantity_unit=quantity_unit, exclude=exclude))
		return return_list
		
	def format_value(self, value):
		#We keep an object that will be handled by the template
		if value:
			return [ingredient.format() for ingredient in value]
		return [IngredientObject()]
		
		
class IngredientsField(forms.Field):
	widget = IngredientsWidget
	def __init__(self, empty_value=None, **kwargs):
		self.empty_value=empty_value
		super().__init__(**kwargs)
		
	def to_python(self, value):
		if value is not None:
			return [ingredient.to_python() for ingredient in value]
		else:
 			return []
		
	def widget_attrs(self, widget):
		#Doesn't work for now :/
		return {'ingredient_list' :  Ingredient.objects.order_by('name')}
		
def validate_no_duplicate(value_list):
	l=[]
	for e in value_list:
		if e.name in l:
			raise ValidationError(
				_('%(ingredient_name) has been listed twice'),
				params={'ingredient_name': e.name},
			)
		l.append(e.name)
		    
def validate_non_empty_name(value_list):
	for e in value_list:
		if (e.quantity or e.quantity_unit) and not e.name:
			raise ValidationError(
		        _('You have included an ingredient without name'),
		        params={},
		    )
				


class RecipeForm(Form):
	name = forms.CharField(label = 'Name')
	category = forms.ModelChoiceField(RecipeCategory.objects.all(), label = 'Category', required=False)
	quantity = forms.IntegerField(min_value=1, label = 'Yield')
	quantity_unit = forms.CharField(label = 'Yield unit', initial='Servings')
	cook_time = CookTimeField(required=False)
	diets = forms.ModelMultipleChoiceField(RestrictedDiet.objects.all(), label = 'Diets', widget = forms.CheckboxSelectMultiple, required=False)
	instructions = forms.CharField(label = 'Instructions', widget = Textarea(attrs={'cols': 80, 'rows': 20}))
	ingredients = IngredientsField(label='Ingredients', required=False, validators = [validate_no_duplicate, validate_non_empty_name])
	
	def save(self):
		#building new recipe
		r = Recipe()
		r.name = self.cleaned_data['name']
		r.instructions = self.cleaned_data['instructions']
		r.quantity = self.cleaned_data['quantity']
		r.quantity_unit = self.cleaned_data['quantity_unit']
		r.cook_time = self.cleaned_data['cook_time']
		r.save()

		for diet in self.cleaned_data['diets']:
		    r.diets.add(diet)
		
		for ingredient in self.cleaned_data['ingredients']:
			add_ingredient(r, ingredient.name, ingredient.quantity, ingredient.quantity_unit)

		return r


class CommentForm(forms.ModelForm):
    content = forms.CharField(label ='', widget = forms.Textarea(
        attrs = {
            'class': 'form-control',
            'placeholder': 'Leave a comment!',
            'rows': 4,
            'cols': 50
        }))
    class Meta:
        model = Comment
        fields = ['content']
        
        
def add_ingredient(recipe, ingredient_name, ingredient_quantity, ingredient_quantity_unit):
    #Fetching or creating ingredient
    possible_ing_obj = Ingredient.objects.filter(name = ingredient_name)
    if possible_ing_obj :
        ingredient_object = possible_ing_obj[0]
    else :
        ingredient_object = Ingredient(name = ingredient_name)
        ingredient_object.save()

    #Building relation to recipe
    relation = IngredientQuantity(recipe = recipe,
                                  ingredient = ingredient_object,
                                  quantity = ingredient_quantity,
                                  quantity_unit = ingredient_quantity_unit
                                  )
    relation.save()
