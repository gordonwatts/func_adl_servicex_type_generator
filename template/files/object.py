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


T = TypeVar('T')


def _add_method_metadata(s: ObjectStream[T], a: ast.Call) -> Tuple[ObjectStream[T], ast.Call]:
    '''Add metadata for a collection to the func_adl stream if we know about it
    '''
    assert isinstance(a.func, ast.Attribute)
    if a.func.attr in _method_map:
        s_update = s.MetaData(_method_map[a.func.attr])
{%- if include_file != "" %}
        s_update = s_update.MetaData({
            'metadata_type': 'inject_code',
            'name': '{{ include_file }}',
            'body_includes': ["{{ include_file }}"],
        })
{%- endif %}
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
