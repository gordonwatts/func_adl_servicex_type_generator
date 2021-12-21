import ast
from typing import Tuple, TypeVar
from func_adl import ObjectStream

{%- for import_line in import_statements %}
{{ import_line }}
{% endfor %}

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
        'is_pointer': '{{ method.is_pointer }}',
    },
{%- endfor %}
}


T = TypeVar('T')


def _add_collection_metadata(s: ObjectStream[T], a: ast.Call) -> Tuple[ObjectStream[T], ast.AST]:
    '''Add metadata for a collection to the func_adl stream if we know about it
    '''
    assert isinstance(a.func, ast.Attribute)
    if a.func.attr in _method_map:
        s_update = s.MetaData(_method_map[a.func.attr])
        return s_update, a
    else:
        return s, a


class {{ class_name }} {% if inheritance_list|length > 0 %}({% for super_class in inheritance_list %}{{ super_class }}{% endfor %}){% endif %}:
    "A class"

    _func_adl_type_info = _add_collection_metadata

{% for method in methods %}
    def {{ method.name }}(self
        {%- for arg in method.arguments -%}
        , {{ arg.name }}: {{ class_split_namespace(arg.arg_type)[1]}}
        {%- endfor -%}
        ) -> {% if class_name == class_split_namespace(method.return_type)[1] -%}
        '{{ class_split_namespace(method.return_type)[1] }}':
        {%- else -%}
        {{ class_split_namespace(method.return_type)[1] }}:
        {%- endif %}
        "A method"
        ...
{% endfor %}
