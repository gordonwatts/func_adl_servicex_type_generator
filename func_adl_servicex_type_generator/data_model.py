from dataclasses import dataclass
from typing import List, Optional


@dataclass
class collection_info:
    """Data class holds onto the info we need for
    a collection we are emitting.
    """

    # Name we should give collections ("Jets")
    name: str

    # Fully qualified collection type (Iterable[xAOD.Jet_v1])
    collection_type: str

    # Fully qualified python name of the collection item (xAOD.Jet_v1)
    collection_item_type: str

    # The collection item python type name, with no namespace (Jet_v1)
    # TODO: Get rid of this, and calc this on the fly when needed
    collection_item_type_name: str

    # Collection item type (xAOD::Jet_v1)
    cpp_item_type: str

    # Collection item (DataVector<xaod::Jet_v1>)
    cpp_collection_type: str

    # List of include files needed for this
    # collection (['xAODMuon/SlowMuonContainer.h'])
    cpp_include_file: List[str]

    # The name of the library (['xAODMuon'])
    link_libraries: List[str]


@dataclass
class method_arg_info:
    """Holds type, etc., for a method argument"""

    # Argument name
    name: str

    # Default value
    default_value: Optional[str]

    # The argument type
    arg_type: str


@dataclass
class method_info:
    """Holds data for a method attached to a list"""

    # Name of the method
    name: str

    # C++ return type of the method. None if no return type.
    return_type: Optional[str]

    # Arguments for the method
    arguments: List[method_arg_info]


@dataclass
class class_info:
    """Holds the data for a particular class we are emitting"""

    # The fully qualified name of the class (python)
    name: str

    # The fully qualified name of the class (cpp)
    cpp_name: str

    # List of methods
    methods: List[method_info]

    # C++ Container object type, None if this is not a container
    cpp_container_type: Optional[str]

    # Python container object type, None if this is not a container
    python_container_type: Optional[str]

    # The include file that needs to be loaded for this class
    include_file: str

    # If this is an alias marker or not
    is_alias: bool = False
