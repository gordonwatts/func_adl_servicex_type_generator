from .event_collection import Event

from servicex.func_adl.func_adl_dataset import FuncADLQuery as sxFuncADLQuery
{%- for calibration_name in calibration_types %}


class FuncADLQuery{{ calibration_name }}(sxFuncADLQuery[Event]):
    def __init__(self, **kwargs):
        '''Builds a `FuncADLQuery` object to work with {{ calibration_name }}
        datasets. Pass any argument to this function that you would normally
        pass to `FuncADLQuery`.

        Args:
        * `item_type` - The type of this object. Will default to `Event`.

        Note:
        * The current front-end ignores the `codegen` argument.
        '''
        if "item_type" not in kwargs:
            kwargs["item_type"] = Event

        super().__init__(**kwargs)

{%- if calibration_name != '' %}
        # Hack to subvert the replace-in-place.
        from .calibration_support import calib_tools
        ds = calib_tools.query_update(self, calib_tools.default_config("{{ calibration_name }}"))
        self._q_ast = ds._q_ast
{%- endif %}
{%- endfor %}
