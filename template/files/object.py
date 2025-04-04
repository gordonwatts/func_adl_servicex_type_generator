from __future__ import annotations
import ast
from typing import Tuple, TypeVar, Iterable
from func_adl import ObjectStream, func_adl_callback, func_adl_parameterized_call
from enum import Enum
import {{ package_name }}

_method_map = {
{%- for method in methods_info %}
    '{{ method.name }}': {
        'metadata_type': 'add_method_type_info',
        'type_string': '{{ method.fully_qualified_name }}',
        'method_name': '{{ method.name }}',
        {%- if method.return_type_element %}
        'return_type_element': '{{ method.return_type_element }}',
        'return_type_collection': '{{ method.cpp_return_type }}',
        {%- else %}
        'return_type': '{{ method.cpp_return_type }}',
        {%- endif %}
        {%- if method.deref_count %}
        'deref_count': {{ method.deref_count }}
        {%- endif %}
    },
{%- endfor %}
}

_enum_function_map = {
{%- for method_name in referenced_enums.keys() %}
    '{{ method_name }}': [
{%- for enum in referenced_enums[method_name] %}
        {
            'metadata_type': 'define_enum',
            'namespace': '{{ enum[0].name }}',
            'name': '{{ enum[1].name }}',
            'values': [
            {%- for value in enum[1].values %}
                '{{ value.name }}',
            {%- endfor %}
            ],
        },
{%- endfor %}
    ],
{%- endfor %}      
}

_defined_enums = {
{%- for enum in enums_info %}
    '{{ enum.name }}':
        {
            'metadata_type': 'define_enum',
            'namespace': '{{ full_class_name }}',
            'name': '{{ enum.name }}',
            'values': [
            {%- for value in enum.values %}
                '{{ value.name }}',
            {%- endfor %}
            ],
        },
{%- endfor %}      
}

_object_cpp_as_py_namespace="{{ cpp_as_py_namespace }}"

T = TypeVar('T')

def add_enum_info(s: ObjectStream[T], enum_name: str) -> ObjectStream[T]:
    '''Use this to add enum definition information to the backend.

    This can be used when you are writing a C++ function that needs to
    make sure a particular enum is defined.

    Args:
        s (ObjectStream[T]): The ObjectStream that is being updated
        enum_name (str): Name of the enum

    Raises:
        ValueError: If it is not known, a list of possibles is printed out

    Returns:
        ObjectStream[T]: Updated object stream with new metadata.
    '''
    if enum_name not in _defined_enums:
        raise ValueError(f"Enum {enum_name} is not known - "
                            f"choose from one of {','.join(_defined_enums.keys())}")
    return s.MetaData(_defined_enums[enum_name])

def _add_method_metadata(s: ObjectStream[T], a: ast.Call) -> Tuple[ObjectStream[T], ast.Call]:
    '''Add metadata for a collection to the func_adl stream if we know about it
    '''
    assert isinstance(a.func, ast.Attribute)
    if a.func.attr in _method_map:
        s_update = s.MetaData(_method_map[a.func.attr])
{% for i_file in include_files %}
        s_update = s_update.MetaData({
            'metadata_type': 'inject_code',
            'name': '{{ i_file }}',
            'body_includes': ["{{ i_file }}"],
        })
{% endfor %}
{% for l_file in libraries %}
        s_update = s_update.MetaData({
            'metadata_type': 'inject_code',
            'name': '{{ l_file }}',
            'link_libraries': ["{{ l_file }}"],
        })
{% endfor %}
        for md in _enum_function_map.get(a.func.attr, []):
            s_update = s_update.MetaData(md)
        return s_update, a
    else:
        return s, a


@func_adl_callback(_add_method_metadata)
class {{ class_name }}{% if inheritance_list|length > 0 %}({% for super_class in inheritance_list %}{{ super_class }}{% endfor %}){% endif %}:
    "A class"
{% for enum in enums_info %}
    class {{ enum.name }}(Enum):
{%- for value in enum.values %}
        {{ value.name }} = {{ value.value }}
{%- endfor %}
{% endfor %}
{% for method in methods_info -%}
{% if method.param_call_args|length == 0 %}
    def {{ method.name }}(self
        {%- for arg in method.arguments -%}
        , {{ arg.name }}: {{ remove_ns_stem(ns_stem, arg.arg_type)}}
        {%- endfor -%}
        ) -> {{ method.return_type }}:
{%- else %}
    @func_adl_parameterized_call({{method.param_type_cb|subrender}})
    @property
    def {{ method.name }}(self) -> {{ package_name }}.{{method.param_helper_class}}[
        {%- for arg in method.arguments -%}
        {{ remove_ns_stem(ns_stem, arg.arg_type)}}
        {%- endfor -%}
    ]:
{%- endif %}
        "A method"
        ...
{% endfor %}
