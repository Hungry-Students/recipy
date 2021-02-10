function removeIngredient(n) {
	item = document.getElementById("ingredient"+n+"_input");
	item.parentNode.removeChild(item);
}

function addIngredient() {
	var ingredient_counter =0;
	while (document.getElementById("ingredient"+ingredient_counter+"_input")){
		ingredient_counter+=1;
	}
	var tr_node = document.createElement("TR");
	tr_node.innerHTML = 
	`<td>Ingredient name</td>
	<td>
		<input list="ingredients_list" id="ingredient${ingredient_counter}_name" name="ingredient${ingredient_counter}_name">
	</td>
	<td>Exclude</td>
	<td>
		<input type="checkbox" id="exclude_${ingredient_counter}" name="exclude_${ingredient_counter}">
	</td>
	<td>
		<button type="button" onclick=removeIngredient(${ingredient_counter}) >Remove ingredient</button><br>
	</td>`;
	tr_node.id = `ingredient${ingredient_counter}_input`;
	document.getElementById("ingredient_input").appendChild(tr_node);
}
