var addIngredient = (function () {
	var ingredient_counter = 1;
	return function () {
		ingredient_counter +=1;
		var input = 
		`<tr>
			<td>Ingredient ${ingredient_counter}</td>
			<td>
				  <input list="ingredients_list" id="ingredient${ingredient_counter}" name="ingredient${ingredient_counter}">
			</td>
		</tr>
		<tr>
			<td>Quantity</td>
			<td>
				  <input type="number" id="ingredient${ingredient_counter}_quantity" name="ingredient${ingredient_counter}_quantity" placeholder="42">
				  <select name="ingredient${ingredient_counter}_quantity_unit" id="ingredient${ingredient_counter}_quantity_unit">
						<option value="units">units</option>
						<option value="grams">grams</option>
				  </select>
			</td>
		</tr>`;
		document.getElementById("ingredient_input").innerHTML += input;
	}
}) ()
