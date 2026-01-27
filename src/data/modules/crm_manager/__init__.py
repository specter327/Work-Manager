# Library import
from ...core.interfaces import ModuleInterface
from .engine import CRMUtilities, telesales_website, admin_website
from .opencrm_function import OpenCRMFunction
from .generatecallvolume_function import GenerateCallVolumeFunctionUI
from .extracttodaycontacts_function import ExtractTodayContactsFunction
from .exportcontacts_function import ExportContactsFunction
from .userprofile_function import UserProfileFunction

# Constants definition
MODULE_NAME = "CRM Manager"

# Classes definition
class ModuleController(ModuleInterface):
    def __init__(self, context_manager: object) -> None:
        super().__init__(context_manager)

        # Instance properties definition
        self.user_website = telesales_website
        self.admin_website = admin_website
        self.engine = CRMUtilities(telesales_website)
        print("Context manager:", self.context_manager)
        print("Engine website:", self.engine.website)
        print("Engine webbrowser:", getattr(self.engine.website, 'webbrowser', None))
        
        # Context manager register
        self.context_manager.register_module(self)
        
        self.context_manager.expose(self, "UserWebsite", self.user_website)
        self.context_manager.expose(self, "AdminWebsite", self.admin_website)
        self.context_manager.expose(self, "CRMEngine", self.engine)
        
        print("ModuleController initialized for CRM Manager")
        print(self.context_manager.list_modules())
        print(self.context_manager.list_exports(MODULE_NAME))


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
            OpenCRMFunction(self),
            GenerateCallVolumeFunctionUI(self),
            ExtractTodayContactsFunction(self),
            ExportContactsFunction(self),
            UserProfileFunction(self)
        ]