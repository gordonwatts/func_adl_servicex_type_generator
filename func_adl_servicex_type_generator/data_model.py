from dataclasses import dataclass


@dataclass
class collection_info:
    """Data class holds onto the info we need for
    a collection we are emitting.
    """

    name: str
    collection_type: str
    collection_item_type: str


@dataclass
class class_info:
    """Holds the data for a particular class we are emitting"""

    # The fully qualified name of the class
    name: str
