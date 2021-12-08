from typing import Iterable, Tuple, TypeVar
from func_adl import ObjectStream
import ast
{%- for import_line in import_statements %}
{{ import_line }}
{% endfor %}

# The map for collection definitions in ATLAS
_collection_map = {
{%- for collection in collections %}
    '{{ collection.name }}': {
        'metadata_type': 'add_atlas_event_collection_info',
        'name': '{{ collection.name }}',
        'include_files': [{%- for file in collection.cpp_include_file -%}'{{ file }}',{%- endfor -%}],
        'container_type': '{{ collection.cpp_collection_type }}',
{%- if collection.cpp_item_type != collection.cpp_collection_type %}
        'element_type': '{{ collection.cpp_item_type }}',
{%- endif %}
        'contains_collection': {{ "True" if collection.cpp_item_type != collection.cpp_collection_type else "False" }},
        'link_libraries': {{ collection.link_libraries }},
    },
{%- endfor %}
}

T = TypeVar('T')

def _add_collection_metadata(s: ObjectStream[T], a: ast.Call) -> Tuple[ObjectStream[T], ast.AST]:
    '''Add metadata for a collection to the func_adl stream if we know about it
    '''
    assert isinstance(a.func, ast.Attribute)
    if a.func.attr in _collection_map:
        s_update = s.MetaData(_collection_map[a.func.attr])
        return s_update, a
    else:
        return s, a

class Event:
    '''The top level event class. All data in the event is accessed from here
    '''

    _func_adl_type_info = _add_collection_metadata


{%- for item in collections %}
    def {{ item.name }}(self, name: str) -> {{ remove_namespaces(item.collection_type) }}:
        ...
{%- endfor -%}
