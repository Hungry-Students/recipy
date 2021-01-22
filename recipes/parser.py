import re

spaces = "[ \\r\\n\\t]*"

quantity_units = ["grammes", "gr", "g", "kg"
				  "cuillère à soupe", "cuillères à soupe", "càs", "c. à. s."
				 ]
				 
separators = ["de", "d'", ""] #Attention : garder la chaine vide à la fin, sinon elle mange le token

### Optionnal quantity ###
regexp = "(?P<quantity>[0-9]+)?"
regexp += spaces

### Optionnal quantity unit and separator###
regexp += "((?P<quantity_unit>"
temp = False
for q_unit in quantity_units:
	if temp:
		regexp += "|"
	else:
		temp=True
	regexp+= q_unit
regexp+=")"
regexp+=spaces

temp = False
regexp+="("
for sep in separators:
	if temp:
		regexp += "|"
	else:
		temp=True
	regexp+= sep
regexp +="))?"
regexp+=spaces

### Ingredient name ###
regexp += "(?P<ingredient_name>[\w ]+)"


m = re.search(regexp, "500g de patates")
if m is not None:
	print(m.group('quantity'))
	print(m.group('quantity_unit'))
	print(m.group('ingredient_name'))

