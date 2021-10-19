{%- for import_line in import_statements %}
{{ import_line }}
{% endfor %}

class {{ class_name }}:
    "A class"
{% for method in methods %}
    def {{ method.name }}(self
        {%- for arg in method.arguments -%}
        , {{ arg.name }}: {{ class_split_namespace(arg.arg_type)[1]}}
        {%- endfor -%}
        ) -> {{ class_split_namespace(method.return_type)[1] }}:
        "A method"
        ...
{% endfor %}
