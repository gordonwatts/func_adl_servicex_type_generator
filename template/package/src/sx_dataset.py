from typing import Union
from func_adl_servicex.ServiceX import ServiceXSourceCPPBase
from servicex.servicex import ServiceXDataset
from servicex.utils import DatasetType
from .event_collection import Event


class {{ sx_dataset_name }}(ServiceXSourceCPPBase[Event]):
    def __init__(self, sx: Union[ServiceXDataset, DatasetType], backend="{{ backend_default_name }}"):
        """
        Create a servicex dataset sequence from a servicex dataset.
        """
        super().__init__(sx, backend)
