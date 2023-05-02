from typing import Union
from func_adl_servicex.ServiceX import ServiceXSourceCPPBase
from servicex.servicex import ServiceXDataset
from servicex.utils import DatasetType
from .event_collection import Event
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