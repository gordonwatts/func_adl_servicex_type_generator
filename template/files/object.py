

class {{ class_name }}:
    "A class"
{% for method in methods %}
    def {{ method.name }}(self) -> {{ method.return_type }}:
        "A method"
        ...
{% endfor %}
