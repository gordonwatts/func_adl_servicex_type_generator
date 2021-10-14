from typing import Iterable
{%- for import_line in import_statements %}
{{ import_line }}
{% endfor %}

class Event:
{%- for item in collections %}
    def {{ item.name }}(self) -> {{ item.collection_type }}:
        pass
{%- endfor -%}
