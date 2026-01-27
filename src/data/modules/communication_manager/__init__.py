# Library import
from ...core.interfaces import ModuleInterface
from . import communication_system
import time

# Constants definition
MODULE_NAME = "Communication Manager"

# Classes definition
class ModuleController(ModuleInterface):
    def __init__(self, context_manager: object) -> None:
        # Constructor hereditance
        super().__init__(context_manager)
        
        # Instance property assignment
        self.CRMEngine = self.context_manager.get("CRM Manager", "CRMEngine")
        self.user_website = self.context_manager.get("CRM Manager", "UserWebsite")
        self.admin_website = self.context_manager.get("CRM Manager", "AdminWebsite")
        print("Admin Website:", self.admin_website)
        
        # Instance property definition
        self.CaptureEngine = communication_system.CaptureEngine.CaptureEngine(
            root_path=self.CRMEngine.RESOURCES_TABLE["contacts_information"],
            folder_name=f"Contacts [{time.localtime().tm_mday}-{time.localtime().tm_mon}-{time.localtime().tm_year}]",
            admin_website=self.admin_website,
            user_website=self.user_website
        )
        self.PriorizerEngine = communication_system.PriorizerEngine.PriorizerEngine(
            self.CaptureEngine.storage_center.base_full_path
        )
        
        print("Capture Engine:", self.CaptureEngine)
        print("Priorizer Engine:", self.PriorizerEngine)
        print("Priorizer Engine database file:", self.PriorizerEngine.priorizer_database.database_filepath)
        
        self.PriorizerEngine.start()
        
    @property
    def module_name(self) -> str:
        return MODULE_NAME
    
    def start(self) -> bool:
        self.CaptureEngine.start()
        
        self._set_status_enabled()
        return True
    
    def stop(self) -> bool:
        self._set_status_disabled()
        return True
    
    def get_functions(self) -> list:
        return []