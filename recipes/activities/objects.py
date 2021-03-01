import json

from recipes.activities import errors


class Object:
    attributes = ["type", "id", "name", "to"]
    type = "Object"

    @classmethod
    def from_json(cls, obj_json):
        return Object(**obj_json)

    def __init__(self, **kwargs):
        for key in self.attributes:
            if key == "type":
                continue
            value = kwargs.get(key)
            if value is None:
                continue
            if isinstance(value, dict) and value.get("type"):
                value = as_activitystream(value)
            self.__setattr__(key, value)

    def __str__(self):
        content = json.dumps(self, default=encode_activitystream)
        return "<{type}: {content}>".format(type=self.type, content=content)

    def to_json(self, context=False):
        values = {}
        for attribute in self.attributes:
            value = getattr(self, attribute, None)
            if value is None:
                continue
            if isinstance(value, Object):
                value = value.to_json()
                values[attribute] = value
            to_value = values.get("to")
            if isinstance(to_value, str):
                values["to"] = [to_value]
            elif getattr(to_value, "__iter__", None):
                values["to"] = []
                for item in to_value:
                    if isinstance(item, str):
                        values["to"].append(item)
                    if isinstance(item, Object):
                        values["to"].append(item.id)
            if context:
                values["@context"] = "https://www.w3.org/ns/activitystreams"
            return values

    def to_activitysream(self):
        return self


ALLOWED_TYPES = {
    "Object": Object,
    # "Actor": Actor,
    # "Person": Person,
    # "Note": Note,
    # "Collection": Collection,
    # "OrderedCollection": OrderedCollection,
}


def as_activitystream(obj):
    """
    Construct an activity stream representation of dictionary "obj"
    """
    obj_type = obj.get("type")

    if not obj_type:
        msg = "Invalid ActivityStream object, the type is missing"
        raise errors.ASDecodeError(msg)

    if type in ALLOWED_TYPES:
        return ALLOWED_TYPES[type](**obj)

    raise errors.ASDecodeError("Invalid Type {0}".format(type))


def encode_activitystream(obj):
    if isinstance(obj, Object):
        return obj.to_json()
    raise errors.ASTypeError("Unknown ActivityStream Type")
