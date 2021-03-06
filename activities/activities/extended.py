from .core import Activity, Object


class Add(Activity):
    """
    https://www.w3.org/ns/activitystreams#Add
    Indicates that the `actor` has added the `object` to the `target`.
    If the `target` property is not explicitly specified, the target would need to be
    determined implicitly by context.
    The `origin` can be used to identify the context from which the `object` originated.
    """

    type = "Add"
    required_attr = Activity.required_attrs + ["actor", "object", "target"]


class Create(Activity):
    """
    https://www.w3.org/ns/activitystreams#Create
    Indicates that the `actor` has created the `object`
    """

    type = "Create"
    required_attr = Activity.required_attrs + ["actor", "object", "target"]


class Follow(Activity):
    """
    https://www.w3.org/ns/activitystreams#Follow
    Indicates that the `actor` is "following" the `object`.
    Following is defined in the sense typically used within Social systems in which the
    actor is interested in any activity performed by or on the object.
    The `target` and `origin` typically have no defined meaning.
    """

    type = "Follow"
    required_attrs = Activity.required_attrs + ["actor", "object"]


# Actor Types


class Person(Object):
    """
    https://www.w3.org/ns/activitystreams#Person
    Represents an individual person.
    """

    type = "Person"


# Object types


class Recipe(Object):
    """
    https://schema.org/Recipe
    Represents a recipe
    """

    type = "Recipe"
    attributes = Object.attributes + [
        "cookingMethod",
        "recipeCategory",
        "recipeCuisine",
        "recipeIngredients",
        "recipeYield",
    ]


class Ingredient(Object):
    """
    Represents an ingredient
    """

    type = "Ingredient"
    attributes = Object.attributes + ["quantity"]


class Tombstone(Object):
    """
    https://www.w3.org/ns/activitystreams#Tombstone
    A Tombstone represents a content object that has been deleted.
    It can be used in Collections to signify that there used to be an object at this
    position, but it has been deleted.
    """

    type = "Tombstone"
    attributes = Object.attributes + ["formerType", "deleted"]
