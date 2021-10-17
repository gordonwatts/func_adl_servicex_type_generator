{%- for import_line in import_statements %}
{{ import_line }}
{% endfor %}

class {{ class_name }}:
    "A class"
{% for method in methods %}
    def {{ method.name }}(self) -> {{ class_split_namespace(method.return_type)[1] }}:
        "A method"
        ...
{% endfor %}
