# Library import
from .webcontroller import BrowserController
from ..properties.exceptions import BrowserAlreadyOpenedError, BrowserNotOpenedError
from  typing import Type

# Classes definition
class WebBrowser:
    "High level controller for a instance of a web browser"

    def __init__(self,
        controller: Type[BrowserController]
    ) -> None:
        self.controller = controller()
        self.state = self.controller.get_status()

    @property
    def driver(self) -> object:
        return self.controller.get_driver()
    
    # Public functions
    def open_browser(self, headless: bool = False, deactivate_security: bool = True, initial_url: str = None) -> bool:
        "Open a new web browser instance"
        # Verify if the web browser is actually opened
        if self.controller.is_closed():
            # Open the web browser
            self.controller.start(headless, deactivate_security, initial_url)

            # Return results
            return True
        else:
            # Raise exception (the browser is already opened)
            raise BrowserAlreadyOpenedError
    
    def close_browser(self) -> bool:
        "Close the web browser instance"
        # Verify the current web browser status
        if self.controller.is_opened():
            # Stop the web browser instance
            self.controller.stop()

            # Return results
            return True
        else:
            # Raise exception (the browser is already closed)
            raise BrowserNotOpenedError

    # Public methods
    def open_tab(self, url: str, focus_new_tab: bool) -> object:
        "Open a new tab"
        return self.controller.open_tab(url, focus_new_tab)
    
    def close_tab(self, handle=None) -> object:
        "Close a existent tab"
        return self.controller.close_tab(handle)
    
    def get_current_url(self) -> object:
        "Return the actual URL tab"
        return self.controller.get_current_url()
    
    def query_tabs(self) -> list:
        "Query for the actual opened tabs"
        return self.controller.query_tabs()
    
    def query_current_tab(self) -> object:
        "Query for the handle of the current focused tab"
        return self.controller.query_actual_tab()
    
    def is_opened(self) -> bool:
        "Verify if the web browser instance is opened"
        return self.controller.is_opened()
    
    def is_closed(self) -> bool:
        "Verify if the web browser instance is closed"
        return self.controller.is_closed()
    
    def get_status(self) -> object:
        "Retrieve the actual web browser status"
        return self.controller.get_status()
    
    def refresh_tab(self, handle=None) -> bool:
        "Refresh the current or specified tab"
        return self.controller.refresh_tab(handle)
    
    def get_cookies(self) -> list:
        "Get all the available cookies"
        return self.controller.get_cookies()
    
    def add_cookies(self, cookies: dict, target_url: str) -> bool:
        "Set a group of cookies"
        return self.controller.add_cookies(cookies)
    
    def execute_javascript(self, code: str, *args) -> str:
        "Execute a specified JavaScript code on the web browser instance"
        return self.controller.execute_javascript(code, *args)
    
    def switch_focus_tab(self, handle: str) -> bool:
        "Switch the focus of the tab to the specified tab handle"
        return self.controller.switch_focus_tab(handle)