import json
from copy import copy

ALLOWED_TYPES = []
PUBLIC_AUDIENCE = ["to", "cc", "audience"]
HIDDEN_AUDIENCE = ["bto", "bcc"]
AUDIENCE = PUBLIC_AUDIENCE + HIDDEN_AUDIENCE


def as_activitystream(obj):
    type = obj.get("type")

    if not type:
        msg = "Invalid ActivityStream object, the type is missing"
        raise Exception(msg)

    if type in ALLOWED_TYPES:
        return ALLOWED_TYPES[type](**obj)

    raise Exception("Invalid Type {}".format(type))


def encode_activitystream(obj):
    if isinstance(obj, Object):
        return obj.to_json()
    raise Exception("Unknown ActivityStream Type")


class Object:
    attributes = [
        "type",
        "id",
        "attachment",
        "attributedTo",
        "audience",
        "content",
        "context",
        "name",
        "endTime",
        "generator",
        "icon",
        "image",
        "inReplyTo",
        "location",
        "preview",
        "published",
        "replies",
        "startTime",
        "summary",
        "tag",
        "updated",
        "url",
        "to",
        "bto",
        "cc",
        "bcc",
        "mediaType",
        "duration",
    ]
    type = "Object"

    @classmethod
    def from_json(cls, json):
        return Object(**json)

    def __init__(self, obj=None, **kwargs):
        if obj:
            self.__init__(**obj.to_activitystream())
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
        to = values.get("to")
        if isinstance(to, str):
            values["to"] = [to]
        elif getattr(to, "__iter__", None):
            values["to"] = []
            for item in to:
                if isinstance(item, str):
                    values["to"].append(item)
                if isinstance(item, Object):
                    values["to"].append(item.id)

        if context:
            values["@context"] = "https://www.w3.org/ns/activitystreams"
        return values

    def to_activitystream(self):
        return self


class Activity(Object):
    """
    https://www.w3.org/ns/activitystreams#Activity
    An Activity is a subtype of Object that describes some form of action that may
    happen, is currently happening, or has already happened.
    The Activity type itself serves as an abstract base type for all types of
    activities.
    It is important to note that the Activity type itself does not carry any specific
    semantics about the kind of action being taken.
    """

    type = "Activity"
    attributes = Object.attributes + [
        "actor",
        "object",
        "target",
        "result",
        "origin",
        "instrument",
    ]
    required_attrs = []

    def get_audience(self):
        audience = []
        for attr in AUDIENCE:
            value = getattr(self, attr, None)
            if not value:
                continue
            if isinstance(value, str):
                value = [value]
            audience += value
        return set(audience)

    def strip_audience(self):
        """
        Return a copy of `self` with hidden audience removed
        """
        new = copy(self)
        for attr in HIDDEN_AUDIENCE:
            if getattr(self, attr, None):
                delattr(new, attr)
        return new

    def validate(self):
        for attr in self.required_attrs:
            if not getattr(self, attr, None):
                formatted_type = "{} activity".format(self.type)
                if self.type == Activity.type:
                    formatted_type = "Activity"
                msg = "Invalid {}, {} is missing".format(formatted_type, attr)
                Exception(msg)


class Collection(Object):
    """
    https://www.w3.org/ns/activitystreams#Collection
    A Collection is a subtype of Object that represents ordered or unordered sets of
    Object or Link instances.
    Refer to the Activity Streams 2.0 Core specification for a complete description of
    the Collection type.
    """

    type = "Collection"
    attributes = Object.attributes + ["totalItems", "current", "first", "last", "items"]

    def __init__(self, iterable=None, **kwargs):
        self._items = []

        Object.__init__(self, **kwargs)
        if iterable is None:
            return

        self.items = iterable

    @property
    def items(self):
        return self._items

    @items.setter
    def items(self, iterable):
        for item in iterable:
            if isinstance(item, Object):
                self._items.append(item)
            elif getattr(item, "to_activitystream", None):
                item = as_activitystream(item.to_activitystream())
                self._items.append(item)
            else:
                raise Exception(
                    "invalid ActivityStream object: {item}".format(item=item)
                )

    def to_json(self, **kwargs):
        json_output = super().to_json(self, **kwargs)
        items = [
            item.to_json() if isinstance(item, Object) else item for item in self.items
        ]
        json_output.update({"items": items})
        return json_output


class OrderedCollection(Collection):
    """
    https://www.w3.org/ns/activitystreams#OrderedCollection
    A subtype of Collection in which members of the logical collection are assumed to
    always be strictly ordered.
    """

    type = "OrderedCollection"

    @property
    def totalItems(self):
        return len(self.items)

    @totalItems.setter
    def totalItems(self, value):
        pass

    @property
    def orderedItems(self):
        return self.items

    @orderedItems.setter
    def orderedItems(self, iterable):
        self.items = iterable
