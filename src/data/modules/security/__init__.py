# Library import
from ...core.interfaces import ModuleInterface
from .status_function import StatusFunction
from .deviceinfo_function import DeviceInfoFunction
from .engine import SecurityEngine

# Constants definition
MODULE_NAME: str = "Security"

# Classes definition
class ModuleController(ModuleInterface):
    def __init__(self, context_manager: object) -> None:
        # Constructor hereditance
        super().__init__(context_manager)
    
    @property
    def module_name(self) -> str:
        return MODULE_NAME
    
    def start(self) -> bool:
        self._set_status_enabled()
        return True
    
    def stop(self) -> bool:
        self._set_status_disabled()
        return True
    
    def get_functions(self) -> list:
        return [
            StatusFunction(self),
            DeviceInfoFunction(self)
        ]