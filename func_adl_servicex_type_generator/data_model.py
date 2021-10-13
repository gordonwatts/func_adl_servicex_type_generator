from dataclasses import dataclass


@dataclass
class collection_info:
    """Data class holds onto the info we need for
    a collection we are emitting.
    """

    name: str
    collection_type: str
