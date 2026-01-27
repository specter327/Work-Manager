# Library import
from abc import ABC, abstractmethod
from ..properties.constants import OPENED_STATE, CLOSED_STATE
from ..properties.exceptions import BrowserAlreadyOpenedError, BrowserNotOpenedError

# Classes definition
class BrowserController(ABC):
    "Web browser basic data and functions definition"

    def __init__(self) -> None:
        # Property definition
        self.state = CLOSED_STATE
    
    # Private functions
    def _set_status_opened(self) -> bool:
        self.state = OPENED_STATE
        return True
    
    def _set_status_closed(self) -> bool:
        self.state = CLOSED_STATE
        return True
    
    # Public methods
    @abstractmethod
    def get_driver(self) -> object: pass

    @abstractmethod
    def start(self, headless: bool, deactivate_security: bool, initial_url: str = None): pass

    @abstractmethod
    def stop(self): pass

    @abstractmethod
    def open_tab(self, url: str, focus_new_tab: bool) -> object: pass

    @abstractmethod
    def close_tab(self, handle=None) -> object: pass

    @abstractmethod
    def get_status(self): pass

    @abstractmethod
    def query_tabs(self) -> list: pass

    @abstractmethod
    def query_actual_tab(self) -> object: pass

    @abstractmethod
    def is_opened(self) -> bool: pass

    @abstractmethod
    def is_closed(self) -> bool: pass

    @abstractmethod
    def refresh(self, handle) -> bool: pass

    @abstractmethod
    def get_cookies(self) -> list: pass

    @abstractmethod
    def add_cookies(self, cookies: list, target_url: str) -> bool: pass
    
    @abstractmethod
    def execute_javascript(self, code: str, *args) -> str: pass

    @abstractmethod
    def switch_focus_tab(self, handle: str) -> bool: pass