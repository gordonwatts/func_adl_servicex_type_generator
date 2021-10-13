from typing import Iterable

class Event:
{%- for item in collections %}
    def {{ item.name }}(self) -> {{ item.collection_type }}:
        pass
{%- endfor -%}
