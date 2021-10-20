from typing import Iterator
{%- for import_line in import_statements %}
{{ import_line }}
{% endfor %}

class Event:
{%- for item in collections %}
    def {{ item.name }}(self, name: str) -> {{ remove_namespaces(item.collection_type) }}:
        pass
{%- endfor -%}
