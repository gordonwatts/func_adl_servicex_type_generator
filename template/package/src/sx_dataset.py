from typing import Union
from .event_collection import Event

try:
        from func_adl_servicex.ServiceX import ServiceXSourceCPPBase
        from servicex.servicex import ServiceXDataset
        from servicex.utils import DatasetType

{%- for sx_info in sx_dataset_name %}


        class {{ sx_info[0] }}(ServiceXSourceCPPBase[Event]):
        def __init__(self, sx: Union[ServiceXDataset, DatasetType], backend="{{ backend_default_name }}"):
                """
                Create a servicex dataset sequence from a servicex dataset.
                """
                super().__init__(sx, backend, item_type=Event)
{%- if sx_info[1] != '' %}
                # Do update-in-place to configure the calibration
                from .calibration_support import calib_tools
                new_sx = calib_tools.query_update(self, calib_tools.default_config("{{ sx_info[1] }}"))
                self._q_ast = new_sx._q_ast
{%- endif %}
{%- endfor %}

except ImportError:
        pass

try:
        from servicex import FuncADLQuery as sxFuncADLQuery
{%- for sx_info in sx_dataset_name %}


        class FuncADLQuery{{ sx_info[1] }}(sxFuncADLQuery[Event]):
        def __init__(self, **kwargs):
                '''Builds a `FuncADLQuery` object to work with {{ sx_info[1] }}
                datasets. Pass any argument to this function that you would normally
                pass to `FuncADLQuery`.

                Args:
                * `item_type` - The type of this object. Will default to `Event`.
                * `codegen` - This backend code-generator. Defaults to `{{ backend_default_name }}`.

                Note:
                * The current front-end ignores the `codegen` argument.
                '''
                if "item_type" not in kwargs:
                kwargs["item_type"] = Event
                if "codegen" not in kwargs:
                kwargs["codegen"] = "{{ backend_default_name }}"

                super().__init__(**kwargs)

{%- if sx_info[1] != '' %}
                # Hack to subvert the replace-in-place.
                ds = calib_tools.query_update(self, calib_tools.default_config("{{ sx_info[1] }}"))
                self._q_ast = ds._q_ast
{%- endif %}
{%- endfor %}

except ImportError:
        pass
