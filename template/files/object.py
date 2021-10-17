
from func_adl_servicex_type_generator.data_model import method_info


class {{ class_name }}:
    "A class"
{% for method in methods %}
    def {{ method.name }}(self) -> {{ method.return_type }}:
        "A method"
        ...
{% endfor %}
