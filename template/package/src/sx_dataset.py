from typing import Union
from .event_collection import Event

try:
    from func_adl_servicex.ServiceX import ServiceXSourceCPPBase
    from servicex.servicex import ServiceXDataset
    from servicex.utils import DatasetType

{%- for calibration_name in calibration_types %}


    class SXDSAtlasxAODR{{ release_series }}{{ calibration_name }}(ServiceXSourceCPPBase[Event]):
        def __init__(self, sx: Union[ServiceXDataset, DatasetType], backend="{{ backend_default_name }}"):
            """
            Create a servicex dataset sequence from a servicex dataset.
            """
            super().__init__(sx, backend, item_type=Event)
{%- if calibration_name != '' %}
            # Do update-in-place to configure the calibration
            from .calibration_support import calib_tools
            new_sx = calib_tools.query_update(self, calib_tools.default_config("{{ calibration_name }}"))
            self._q_ast = new_sx._q_ast
{%- endif %}
{%- endfor %}

except ImportError:
        pass

try:
    from servicex import FuncADLQuery as sxFuncADLQuery
{%- for calibration_name in calibration_types %}


    class FuncADLQuery{{ calibration_name }}(sxFuncADLQuery[Event]):
        def __init__(self, **kwargs):
            '''Builds a `FuncADLQuery` object to work with {{ calibration_name }}
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

{%- if calibration_name != '' %}
            # Hack to subvert the replace-in-place.
            from .calibration_support import calib_tools
            ds = calib_tools.query_update(self, calib_tools.default_config("{{ calibration_name }}"))
            self._q_ast = ds._q_ast
{%- endif %}
{%- endfor %}

except ImportError:
        pass
