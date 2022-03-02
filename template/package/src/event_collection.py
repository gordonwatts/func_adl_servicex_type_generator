from __future__ import annotations
from typing import Any, Dict, Iterable, List, Tuple, TypeVar, Union, Optional
from func_adl import ObjectStream, func_adl_callback
import ast
import copy
import {{ package_name }}

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

_param_metadata : Dict[str, Dict[str, Any]] = {
{%- for n_md in metadata.keys() %}
    '{{ n_md }}': {
    {%- for md_key in metadata[n_md].data[0].keys() %}
        '{{ md_key }}': 
            {%- if metadata[n_md].data[0][md_key] is string -%}
            "{{ metadata[n_md].data[0][md_key] }}",
            {%- else -%}
            [
                {%- for ln in metadata[n_md].data[0][md_key] %}
                "{{ ln }}",
                {%- endfor %}
            ],
            {%- endif -%}
    {%- endfor %}
    },
{%- endfor %}
}

PType = TypeVar('PType')


def _get_param(call_ast: ast.Call, arg_index: int, arg_name: str, default_value: PType) -> PType:
    'Fetch the argument from the arg list'
    # Look for it as a positional argument
    if len(call_ast.args) > arg_index:
        return ast.literal_eval(call_ast.args[arg_index])

    # Look for it as a keyword argument
    kw_args = [kwa for kwa in call_ast.keywords if kwa.arg == arg_name]
    if len(kw_args) > 0:
        return ast.literal_eval(kw_args[0].value)
    
    # We can't find it - return the default value.
    return default_value


MDReplType = TypeVar('MDReplType', bound=Union[str, List[str]])



def _replace_md_value(v: MDReplType, p_name: str, new_value: str) -> MDReplType:
    'Replace one MD item'
    if isinstance(v, str):
        return v.replace('{' + p_name + '}', str(new_value))
    else:
        return [x.replace('{' + p_name + '}', str(new_value)) for x in v]


def _replace_param_values(source: MDReplType, param_values: Dict[str, Any]) -> MDReplType:
    'Replace parameter types in a string or list of strings'
    result = source
    for k, v in param_values.items():
        result = _replace_md_value(result, k, v)
    return result


def _resolve_md_params(md: Dict[str, Any], param_values: Dict[str, Any]):
    'Do parameter subst in the metadata'
    for k, v in param_values.items():
        result = {}
        for mk_key, mk_value in md.items():
            new_value = _replace_md_value(mk_value, k, v)
            if new_value != mk_value:
                result[mk_key] = new_value
        if len(result) > 0:
            md = dict(md)
            md.update(result)
            md['name'] = f"{md['name']}_{v}"
    return md

T = TypeVar('T')


def match_param_value(value, to_match) -> bool:
    'Match a parameter with special values'
    if isinstance(to_match, str):
        if to_match == "*None*":
            return value is None
        if to_match == "*Any*":
            return True
    
    return value == to_match


class _process_extra_arguments:
    'Static class that will deal with the extra arguments for each collection'

{%- for item in collections %}{% if item.extra_parameters|length > 0 %}
    @staticmethod
    def process_{{ item.name }}(bank_name: str, s: ObjectStream[T], a: ast.Call) -> Tuple[str, ObjectStream[T], ast.AST]:
        param_values = {}
        i_param = 0
        {%- for p in item.extra_parameters %}
        i_param += 1
        param_values['{{ p.name }}'] = _get_param(a, i_param, "{{ p.name }}", {{ p.default_value }})
        # assert isinstance(param_values['{{ p.name }}'], {{ p.type }}), f'Parameter {{ p.name }} must be of type {{ p.type }}, not {type(param_values["{{ p.name }}"])}'
        {%- endfor %}
        param_values['bank_name'] = bank_name

        md_name_mapping: Dict[str, str] = {}
        md_list: List[Dict[str, Any]] = []
        {%- for p in item.extra_parameters %}
        p_matched = False
        last_md_name = None
        {%- for a in p.actions %}
        if not p_matched and match_param_value(param_values['{{ p.name }}'], {{ a.value }}):
            p_matched = True
            {%- for md in a.md_names %}
            old_md = _param_metadata['{{ md }}']
            md = _resolve_md_params(old_md, param_values)
            if 'depends_on' in md:
                if '*PREVIOUS*' in md['depends_on']:
                    md = dict(md)
                    md['depends_on'] = [x for x in md['depends_on'] if x != '*PREVIOUS*']
                    if last_md_name is not None:
                        md['depends_on'].append(last_md_name)
            last_md_name = md['name']
            md_list.append(md)
            md_name_mapping[old_md['name']] = md['name']
            {%- endfor %}
            bank_name = _replace_param_values('{{a.bank_rename}}', param_values)
        {%- endfor %}
        {%- endfor %}

        for md in md_list:
            if 'depends_on' in md:
                md = dict(md) # Make a copy so we don't mess up downstream queries
                md['depends_on'] = [(md_name_mapping[x] if x in md_name_mapping else x) for x in md['depends_on']]
            s = s.MetaData(md)

        return bank_name, s, a
{%- endif %}{% endfor %}


def _add_collection_metadata(s: ObjectStream[T], a: ast.Call) -> Tuple[ObjectStream[T], ast.Call]:
    '''Add metadata for a collection to the func_adl stream if we know about it
    '''
    # Unpack the call as needed
    assert isinstance(a.func, ast.Attribute)
    collection_name = a.func.attr
    # collection_bank = ast.literal_eval(a.args[0])

    # # If it has extra arguments, we need to process those.
    # arg_processor = getattr(_process_extra_arguments, f'process_{collection_name}', None)
    # if arg_processor is not None:
    #     new_a = copy.deepcopy(a)
    #     new_bank, s, a = arg_processor(collection_bank, s, new_a)
    #     a.args = [ast.Constant(new_bank)]


    # Finally, add the collection defining metadata so the backend
    # knows about this collection and how to access it.
    if collection_name in _collection_map:
        s_update = s.MetaData(_collection_map[collection_name])
        return s_update, a
    else:
        return s, a


@func_adl_callback(_add_collection_metadata)
class Event:
    '''The top level event class. All data in the event is accessed from here
    '''

{% for item in collections %}
{% if item.method_callback|length > 0 %}
    @func_adl_callback({{item.method_callback|subrender }}){% endif %}
    def {{ item.name }}(self
{%- for arg in item.parameters %}, {{ arg.name }}: {{ arg.type }}{% if arg.default_value != None %} = {{ arg.default_value }}{% endif %}{% endfor -%}
{%- for arg in item.extra_parameters %}, {{ arg.name }}: {{ arg.type }} = {{ arg.default_value }}{% endfor -%}
    ) -> {{ item.collection_type }}:
        ...

{%- endfor -%}
