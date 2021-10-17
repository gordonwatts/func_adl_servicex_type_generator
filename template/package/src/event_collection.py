from typing import Iterator
{%- for import_line in import_statements %}
{{ import_line }}
{% endfor %}

class Event:
{%- for item in collections %}
    def {{ item.name }}(self, name: str) -> Iterator[{{ item.collection_item_type_name }}]:
        pass
{%- endfor -%}
