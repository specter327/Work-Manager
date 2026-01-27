# Library import
from abc import ABC, abstractmethod
from PyQt5.QtWidgets import QWidget

# Classes definition
class ModuleInterface(ABC):
    "This class represents a uniform interface that complies with a standard contract for each embeddable module"

    # General properties definition
    MODULE_STATUS_ENABLED: str = "ENABLED"
    MODULE_STATUS_DISABLED: str = "DISABLED"
    
    # Private methods
    def _set_status_enabled(self) -> bool:
        self.status = self.MODULE_STATUS_ENABLED
        return True
    
    def _set_status_disabled(self) -> bool:
        self.status = self.MODULE_STATUS_DISABLED
        return True

    def _get_current_status(self) -> str:
        return self.status
    
    def __init__(self, context_manager: "ContextManager") -> None:
        # Instance properties definition
        self.status = self.MODULE_STATUS_DISABLED
        
        # Instance properties assignment
        self.context_manager = context_manager
    
    @property
    @abstractmethod
    def module_name(self) -> str:
        pass

    def get_current_status(self) -> str:
        "This method allows you to know the current state of the module"
        return self._get_current_status()

    @abstractmethod
    def start(self) -> bool:
        "Initialize the module"
        pass

    @abstractmethod
    def stop(self) -> bool:
        "The module ends"
        pass

    @abstractmethod
    def get_functions(self) -> list:
        "This method allows you to obtain the list of functions implemented by the module that are enabled for integration with the application"
        pass

class ProcessInterface(ABC):
    "This class represents a general process. It allows for the storage of dynamic or static data, and interaction functions"

    # General property definition
    EXECUTING_STATUS: str = "EXECUTING" # This status define when a process is executing
    FINISHED_STATUS: str = "FINISHED" # This status define when a process has finished
    CANCELED_STATUS: str = "CANCELED" # This status define when a process has been canceled before start
    ABORTED_STATUS: str = "ABORTED" # This status define when a process has been forzed to stop
    PAUSED_STATUS: str = "PAUSED" # This status define when a process is temporaly stopped
    UNDETERMINED_STATUS: str = "UNDETERMINED" # This status define when a process is in a undetermined status

    FINISH_RESULT_SUCCESS: str = "SUCCESS" # This result specify that the process finished with success
    FINISH_RESULT_ERROR: str = "ERROR"
    FINISH_RESULT_UNDETERMINED: str = "UNDETERMINED"

    STATUS_CODE_TABLE = {
        0:"Undefined",
        1:"Any error",
        2:"Undetermined error"
    }

    def __init__(self) -> None:
        # Instance property definition
        self.status: str = self.UNDETERMINED_STATUS
        self.finish_result: str = self.FINISH_RESULT_UNDETERMINED
        self.status_code: int = 0
        self._progress: int | bool = None

    @property
    def status_code_description(self) -> str:
        return self.STATUS_CODE_TABLE[self.status_code]
    
    @property
    @abstractmethod
    def current_progress(self) -> int | float: pass

    @property
    @abstractmethod
    def current_process(self) -> dict: pass
    
    def _set_status_executing(self) -> bool:
        self.status = self.EXECUTING_STATUS
        return True
    
    def _set_status_finished(self, sucess_result: bool, status_code: int = 2) -> bool:

        self.status = self.FINISHED_STATUS
        if sucess_result: self.finish_result = self.FINISH_RESULT_SUCCESS
        else: self.finish_result = self.FINISH_RESULT_ERROR

        self.status_code = status_code

        return True
    
    def _set_status_canceled(self) -> bool:
        self.status = self.CANCELED_STATUS
        return True
    
    def _set_status_aborted(self) -> bool:
        self.status = self.ABORTED_STATUS
        self.finish_result = self.FINISH_RESULT_ERROR

        return True
    
    def _set_status_paused(self) -> bool:
        self.status = self.PAUSED_STATUS

        return True
    
    def _set_status_undetermined(self) -> bool:
        self.status = self.UNDETERMINED_STATUS
        return True
    
    @abstractmethod
    def start(self) -> bool: pass

    @abstractmethod
    def pause(self) -> bool: pass

    @abstractmethod
    def resume(self) -> bool: pass

    @abstractmethod
    def cancel(self) -> bool: pass

    @abstractmethod
    def stop(self) -> bool: pass

    @abstractmethod
    def abort(self) -> bool: pass

class FunctionInterface(ABC):
    "This class represents a function specific to a module, enabled for integration with the application"

    def __init__(self, parent_module: ModuleInterface) -> None:
        # Instance properties definition
        self.process: ProcessInterface = None
        self.widget: QWidget = QWidget()
        self.parent_module = parent_module
    
    @property
    @abstractmethod
    def function_name(self) -> str: pass

    @abstractmethod
    def execute(self, *args, **kwargs) -> ProcessInterface:
        raise NotImplementedError

    @abstractmethod
    def get_widget(self) -> QWidget: pass

class ContextManager:
    """This class provides a context manager for sharing elements between modules"""
    
    def __init__(self) -> None:
        # Instance property definition
        self.__modules = {}
    
    # Public methods
    def register_module(self, module: ModuleInterface) -> str | bool:
        "This function registers a module in the context manager. It will be accesible to all the elements with access to the context"
        
        # Get the module name
        name = module.module_name
        
        # Verify the current module regist existence
        if name in self.__modules: raise ValueError(f"The module: {name} is already registered")
        
        # Regist the new module
        self.__modules[name] = {
            "controller":module,
            "exports":{}
        }
        
        # Return results
        return name

    def expose(self, module: ModuleInterface, key: str, value: object) -> bool:
        "This function exposes an element from a module to the context manager, making it accessible to other modules with access to the context"
        
        # Verify the module existence
        if module.module_name not in self.__modules: raise KeyError(f"The module: {module.module_name} is not registered")
        
        # Expose the new element
        self.__modules[module.module_name]["exports"][key] = value
        
        # Return results
        return True

    def list_modules(self) -> list:
        "This function returns a list of all registered modules in the context manager"
        return list(self.__modules.keys())
    
    def list_exports(self, module_name: str) -> list:
        "This function returns a list of all exposed elements from a specific module"
        
        # Verify the module existence
        if module_name not in self.__modules: raise KeyError(f"The module: {module_name} is not registered")
        
        # Return the list of exposed elements
        return list(self.__modules[module_name]["exports"].keys())

    def has(self, module_name: str, key: str) -> bool:
        "This function verifies if a specific module has exposed a specific element"
        
        # Verify the module existence
        if module_name not in self.__modules: return False
        
        # Verify the exposed element existence
        if key not in self.__modules[module_name]["exports"]: return False
        
        # Return results
        return True
    
    def get(self, module_name: str, key: str) -> object:
        "This function retrieves an exposed element from a specific module"
        
        # Verify the module existence
        if module_name not in self.__modules: raise KeyError(f"The module: {module_name} is not registered")
        
        # Verify the exposed element existence
        if key not in self.__modules[module_name]["exports"]: raise KeyError(f"The key: {key} is not exposed by the module: {module_name}")
        
        # Return the exposed element
        return self.__modules[module_name]["exports"][key]