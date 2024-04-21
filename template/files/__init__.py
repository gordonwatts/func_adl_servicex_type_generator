from typing import Any, TYPE_CHECKING
{%- if module_stub == "" %}
try:
    from .sx_dataset import {{ sx_dataset_name }}
except ImportError:
    # Servicex frontend client 3.X not loaded.
    pass

from .func_adl_iterable import FADLStream

{%- for line in base_init_lines %}
{{ line }}
{%- endfor %}

{%- for v_info in base_variables %}
{{ v_info.name }} = "{{ v_info.value }}"
{%- endfor %}
{%- endif %}

class _load_me:
    """Python's type resolution system demands that types be already loaded
    when they are resolved by the type hinting system. Unfortunately,
    for us to do that for classes with circular references, this fails. In order
    to have everything loaded, we would be triggering the circular references
    during the import process.

    This loader gets around that by delay-loading the files that contain the
    classes, but also tapping into anyone that wants to load the classes.
    """

    def __init__(self, name: str):
        self._name = name
        self._loaded = None

    def __getattr__(self, __name: str) -> Any:
        if self._loaded is None:
            import importlib

            self._loaded = importlib.import_module(self._name)
        return getattr(self._loaded, __name)


# Class loads. We do this to both enable type checking and also
# get around potential circular references in the C++ data model.
if not TYPE_CHECKING:
    {%- for class_name in class_imports %}
    {{class_name}} = _load_me("{{package_name}}{{module_stub}}.{{ class_name }}")
    {%- endfor %}
else:
    {%- for class_name in class_imports %}
    from . import {{class_name}}
    {%- endfor %}

# Include sub-namespace items
{%- for sub_namespace in sub_namespaces %}
from . import {{sub_namespace}}
{%- endfor %}
