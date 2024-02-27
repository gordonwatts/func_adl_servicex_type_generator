from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class parameter_action:
    # The value that triggers this action
    value: str

    # The list of metadata to load
    md_names: List[str]

    # How to rename the bank we are looking at
    bank_rename: str


@dataclass
class extra_parameter:
    """Extra parameters for the class"""

    # The name of the extra parameter
    name: str

    # The type of the extra parameter
    type: str

    # Default value for the extra parameter
    default_value: str

    # Actions to run for values of this parameter
    actions: List[parameter_action]


@dataclass
class normal_parameter:
    """Extra parameters for the class"""

    # The name of the extra parameter
    name: str

    # The type of the extra parameter
    type: str

    # Default value for the extra parameter
    # If it is "None" then there is no default
    default_value: Optional[str]


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

    # Regular, expected, parameters
    parameters: List[normal_parameter]

    # Extra parameters to control other actions we code in here
    extra_parameters: List[extra_parameter]

    # If there is a particular collection callback for this method.
    method_callback: str


@dataclass
class method_arg_info:
    """Holds type, etc., for a method argument"""

    # Argument name
    name: str

    # Default value
    default_value: Optional[str]

    # The Python argument type
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

    # Parameterized function arguments
    param_arguments: List[method_arg_info]

    # param helper object when we are a parameterized function.
    param_helper: Optional[str]

    # The parameter helper object for a callback
    param_type_cb: Optional[str] = None


@dataclass
class enum_value_info:
    """Holds the data for an enum value"""

    # The name of the enum value
    name: str

    # The value of the enum
    value: int


@dataclass
class enum_info:
    """Holds the data for an enum we are emitting"""

    # The fully qualified name of the enum (python)
    name: str

    # Values
    values: List[enum_value_info]


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

    # Other classes we emulate
    behaviors: List[str] = field(default_factory=list)

    # The list of enums we have
    enums: List[enum_info] = field(default_factory=list)


@dataclass
class metadata_info:
    """Holds the data for a metadata item"""

    data: Dict[str, List[str]]


@dataclass
class file_info:
    # The output name to write the file to
    file_name: str

    # Init lines to add to the __init__.py file at top level
    init_lines: List[str]

    # The lines to dump into the file
    contents: List[str]
