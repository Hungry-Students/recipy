function removeIngredient(n) {
	item = document.getElementById("ingredient_"+n+"_input");
	item.parentNode.removeChild(item);
}

function addIngredient(name) {
	var ingredient_counter =0;
	while (document.getElementById("ingredient_"+ingredient_counter+"_input")){
		ingredient_counter+=1;
	}
	var tr_node = document.createElement("TR");
	tr_node.innerHTML = 
	`<td>Name</td>
	<td>
		<input list="${name}_ingredients_list" id="${name}_${ingredient_counter}_name" name="${name}_${ingredient_counter}_name">
	</td>
	<td>Quantity</td>
	<td>
		<input id="${name}_${ingredient_counter}_quantity" name="${name}_${ingredient_counter}_quantity" placeholder="42 spoons">
	</td>
	<td>
		<button type="button" onclick=removeIngredient(${ingredient_counter}) >Remove ingredient</button><br>
	</td>`;
	tr_node.id = `${name}_${ingredient_counter}_input`;
	document.getElementById(`${name}_ingredient_input`).appendChild(tr_node);
}

