function removeIngredient(n, name) {
	item = document.getElementById(`${name}_${n}_input`);
	item.parentNode.removeChild(item);
}

function addIngredient(name, display_type, value_name='', value_quantity='', value_exclude='') {
	var ingredient_counter =0;
	while (document.getElementById(`${name}_${ingredient_counter}_input`)){
		ingredient_counter+=1;
	}
	var tr_node = document.createElement("TR");
	var content="";
	if (display_type == 0){
		content = 	`<td>Quantity</td>
					<td>
						<input id="${name}_${ingredient_counter}_quantity" name="${name}_${ingredient_counter}_quantity" value="${value_quantity}">
					</td>
					`
	}
	if (display_type == 1){
		content = 	`<td>Exclude</td>
					<td>
						<input type="checkbox" id="${name}_exclude_${ingredient_counter}" name="${name}_exclude_${ingredient_counter}" ${value_exclude}>
					</td>
					`
	}
	tr_node.innerHTML =
	`<td>Name</td>
	<td>
		<input list="${name}_ingredients_list" id="${name}_${ingredient_counter}_name" name="${name}_${ingredient_counter}_name" value="${value_name}">
	</td>` + content + `<td>
		<button type="button" onclick=removeIngredient(${ingredient_counter},'${name}')>Remove ingredient</button><br>
	</td>`;
	tr_node.id = `${name}_${ingredient_counter}_input`;
	document.getElementById(`${name}_ingredient_input`).appendChild(tr_node);
}
