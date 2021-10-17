from dataclasses import dataclass
from typing import List, Optional


@dataclass
class collection_info:
    """Data class holds onto the info we need for
    a collection we are emitting.
    """

    # Name we should give collections
    name: str

    # Fully qualified collection type
    collection_type: str

    # Fully qualified name of the collection item
    collection_item_type: str

    # The collection item type name, with no namespace
    collection_item_type_name: str


@dataclass
class method_arg_info:
    """Holds type, etc., for a method argument"""

    # Argument name
    name: str

    # Default value
    default_value: str

    # The argument type
    arg_type: str


@dataclass
class method_info:
    """Holds data for a method attached to a list"""

    # Name of the method
    name: str

    # Return type of the method. None if no return type
    return_type: Optional[str]

    # Arguments for the method
    arguments: List[method_arg_info]


@dataclass
class class_info:
    """Holds the data for a particular class we are emitting"""

    # The fully qualified name of the class
    name: str

    # List of methods
    methods: List[method_info]
