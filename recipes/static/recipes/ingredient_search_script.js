function removeIngredient(n, name='ingredients') {
	item = document.getElementById(`${name}_${n}_input`);
	item.parentNode.removeChild(item);
}

function addIngredient(name) {
	var ingredient_counter =0;
	while (document.getElementById(`${name}_${n}_input`)){
		ingredient_counter+=1;
	}
	var tr_node = document.createElement("TR");
	tr_node.innerHTML = 
	`<td>Ingredient name</td>
	<td>
		<input list="ingredients_list" id="${name}_${ingredient_counter}_name" name="${name}_${ingredient_counter}_name">
	</td>
	<td>Exclude</td>
	<td>
		<input type="checkbox" id="${name}_exclude_${ingredient_counter}" name="${name}_exclude_${ingredient_counter}">
	</td>
	<td>
		<button type="button" onclick=removeIngredient(${ingredient_counter}) >Remove ingredient</button><br>
	</td>`;
	tr_node.id = `${name}_${ingredient_counter}_input`;
	document.getElementById(`${name}_ingredient_input`).appendChild(tr_node);
}
