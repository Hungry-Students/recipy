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
	`<td>Name</td>
	<td>
		<input list="ingredients_list" id="ingredient${ingredient_counter}_name" name="ingredient${ingredient_counter}_name">
	</td>
	<td>Quantity</td>
	<td>
		<input type="number" id="ingredient${ingredient_counter}_quantity" name="ingredient${ingredient_counter}_quantity" placeholder="42">
		<select name="ingredient${ingredient_counter}_quantity_unit" id="ingredient${ingredient_counter}_quantity_unit">
			<option value="units">units</option>
			<option value="grams">grams</option>
		</select>
	</td>
	<td>
		<button type="button" onclick=removeIngredient(${ingredient_counter}) >Remove ingredient</button><br>
	</td>`;
	tr_node.id = `ingredient${ingredient_counter}_input`;
	document.getElementById("ingredient_input").appendChild(tr_node);
}

