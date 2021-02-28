# -*- coding: utf-8 -*-
import re


class IngredientParser:
    def quantity_units(self):
        # syntax : dictionnary containing the version stored in DB as key, and the possible tokens in a list associated to it.
        return {
            "grammes": ["grammes", "gr", "g"],
            "kg": ["kg"],
            "cuillères à soupe": [
                "cuillère à soupe",
                "cuillères à soupe",
                "càs",
                "c. à. s.",
            ],
            "verres": ["verre", "verres"],
            "cL": ["cl", "centilitres"],
            "mL": ["ml", "millilitres"],
            "L": ["l", "litres"],
            "pincées": ["pincées", "pincée"],
        }

    def separators(self):
        # list of separators between quantity units and ingredients
        return [
            "de",
            "d'",
        ]  # Attention : garder la chaine vide à la fin, sinon elle mange le token

    def build_regexps(self):
        # builds regexps for parsing ingredients and quantity_units
        spaces = "[ \\r\\n\\t]*"
        # Optionnal quantity
        regexp = "(?P<quantity>[0-9]+)?"
        regexp_quantity = "(?P<quantity>[0-9]+)?"
        regexp += spaces
        regexp_quantity += spaces

        # For quantities parsing, we first parse number + string and then will parse the unit separately
        regexp_quantity += r"(?P<quantity_unit>[\w'.\- ]*)"

        # Optionnal quantity unit and separator
        regexp_unit = "(?P<quantity_unit>"
        regexp += "((?P<quantity_unit>"
        temp = False
        for _, token_list in self.quantity_units().items():
            for q_unit in token_list:
                if temp:
                    regexp += "|"
                    regexp_unit += "|"
                else:
                    temp = True
                regexp += q_unit
                regexp_unit += q_unit
        regexp += ")"
        regexp += spaces
        regexp_unit += ")"
        regexp_unit += spaces

        temp = False
        regexp += "("
        for sep in self.separators():
            if temp:
                regexp += "|"
            else:
                temp = True
            regexp += sep
        regexp += "))?"
        regexp += spaces

        # Ingredient name
        regexp += r"(?P<ingredient_name>[\w'.\- ]*\w)"
        regexp += spaces

        return regexp, regexp_unit, regexp_quantity

    def __init__(self):

        # Output variables
        self.quantity = None
        self.quantity_unit = None
        self.ingredient_name = None

        # Constructing regexps in order to parse input
        self.regexp, self.regexp_unit, self.regexp_quantity = self.build_regexps()

    def match_unit_token(self, candidate_token_string):
        # matches s to the token assigned in the database. If not possible, returns s. WARNING : not time efficient
        for token, value in self.quantity_units().items():
            if candidate_token_string in value:
                return token
        return candidate_token_string

    def parse_unit(self, raw_unit):
        # parses a unit of measure
        known_unit = re.search(self.regexp_unit, raw_unit)
        if known_unit is not None:
            return self.match_unit_token(known_unit.group("quantity_unit"))
        return raw_unit

    def parse_quantity(self, raw_quantity):
        known_quantity = re.search(self.regexp_quantity, raw_quantity)
        quantity, unit = None, None
        if known_quantity is not None:
            quantity = known_quantity.group("quantity")
            if quantity is not None:
                quantity = int(quantity)
            unit = known_quantity.group("quantity_unit")
            if unit is not None:
                unit = self.parse_unit(unit)
        return (quantity, unit)

    def parse(self, raw_quantified_ingredient):
        # parses an ingredient and the quantities requiered in the recipe
        parsed_ingredient = re.search(self.regexp, raw_quantified_ingredient)
        if parsed_ingredient is not None:
            self.quantity = parsed_ingredient.group("quantity")
            if self.quantity is not None:
                self.quantity = int(self.quantity)
            self.quantity_unit = self.match_unit_token(
                parsed_ingredient.group("quantity_unit")
            )
            self.ingredient_name = parsed_ingredient.group("ingredient_name")
            return 0
        return 2  # error code, parsing failed


class YieldsParser:
    def build_regexps(self):
        # builds regexps for parsing yields and yield units
        spaces = "[ \\r\\n\\t]*"
        # Optionnal quantity
        regexp = "(?P<yields>[0-9]+)"
        regexp += spaces

        regexp += r"(?P<yields_unit>[\w'.\- ]+\w)"
        regexp += spaces

        return regexp

    def __init__(self):

        # Output variables
        self.yields = None
        self.yields_unit = None

        # Constructing regexp in order to parse input
        self.regexp = self.build_regexps()

    def parse(self, raw_yield):
        # parses an ingredient and the quantities requiered in the recipe
        parsed_yield = re.search(self.regexp, raw_yield)
        if parsed_yield is not None:
            self.yields = parsed_yield.group("yields")
            self.yields_unit = parsed_yield.group("yields_unit")
            return 0
        return 2  # error code, parsing failed


def test_parsers():
    print("Test of IngredientParser :\n")
    parser = IngredientParser()
    print(parser.regexp)
    test_list = ["Poivre", "300 càs de farine"]
    for e in test_list:
        parser.parse(e)
        print(parser.quantity)
        print(parser.quantity_unit)
        print(parser.ingredient_name, "\n")

    # print(p.parse_unit("g"),'\n')

    # print("Test of YieldsParser :\n")
    # p = YieldsParser()
    # p.parse("8 personnes")
    # print(p.yields)
    # print(p.yields_unit)


# test_parsers()
