# Library import
from __future__ import annotations
from urllib.parse import urlencode

# Classes definition
class WebPage:
    "This class provides a simple representation and abstraction of a web page, including all its functions and data"

    def __new__(cls, *args, **kwargs):
        
        # Extrae la clase de página específica del kwargs. Por defecto, usa WebPage (cls)
        page_class = kwargs.get('page_class', cls)

        # Si la clase de página proporcionada es diferente a WebPage:
        if page_class is not cls:
            
            # 1. Define el nombre de la nueva clase compuesta para facilitar la depuración
            new_class_name = f"Composite{page_class.__name__}"
            
            # 2. Define la cadena de herencia: 
            #    (La clase específica primero para que sus métodos sobreescriban a WebPage, WebPage segunda)
            bases = (page_class, cls)
            
            # 3. Crea la nueva clase compuesta dinámicamente
            # type(name, bases, dict) es el constructor de clases en Python
            new_cls = type(new_class_name, bases, {})
            
            # 4. Crea y devuelve una instancia de la NUEVA clase.
            # **Importante:** Pasamos todos los argumentos a super().__new__
            return super().__new__(new_cls)

        # Si no se pasó 'page_class', crea una instancia normal de WebPage.
        return super().__new__(cls)

    def __init__(self,
        website: website.WebSite, # type: ignore
        name: str,
        folder_parent: webfolder.WebFolder = None, # type: ignore
        parameters: dict = None,
        page_class: type = None
    ):
        """Parameters example:
            website: WebSite object instance
            name: login.html
            folder_parent: WebFolder object instance (only if has a web folder parent) | None
            parameters: {'client_id': '2504242246490008519680', 'response_type': 'code'}
        """

        # Property definition
        self.website = website
        self.folder_parent = folder_parent
        self.name = name
        self.parameters = parameters
        self.page_class = page_class

        # Internal state
        self.handle = None
        self.is_focus = None
        self.is_open = None
    
    @property
    def full_path(self) -> str:
        folder_path = ""
        if self.folder_parent:
            folder_path = self.folder_parent.path.rstrip("/")
        
        base_path = self.name
        
        if folder_path:
            return f"{folder_path}/{base_path}"
        
        return base_path

    @property
    def url(self) -> str:
        base_url = f"{self.website.base_url}{self.full_path}"

        if self.parameters:
            query_string = urlencode(self.parameters)
            return f"{base_url}?{query_string}"
        else:
            return base_url
    
    # Private methods
    def _set_status_opened(self) -> bool:
        self.is_open = True
        return True
    
    def _set_status_closed(self) -> bool:
        self.is_open = False
        return True
    
    def _set_status_focused(self) -> bool:
        self.is_focus = True
        return True
    
    def _set_status_unfocused(self) -> bool:
        self.is_focus = False
        return True
    
    # Public methods
    def is_current_page(self) -> bool:
        raise NotImplementedError

    def is_opened(self) -> bool:
        return self.is_open

    def is_closed(self) -> bool:
        return self.is_open == False
    
    def is_focused(self) -> bool:
        return self.is_focus

    def is_unfocused(self) -> bool:
        return self.is_focus == False

    def open_page(self, focus_new_tab=True) -> bool:
        "This function opens in the browser the current web page"

        if not self.website or not self.website.webbrowser:
            raise RuntimeError("No WebBrowser instance associated with this WebPage")
        
        # Verify actual status
        if self.is_opened(): return True
        else: pass

        handle = self.website.webbrowser.open_tab(self.url, focus_new_tab)
        self.handle = handle

        self._set_status_opened()
        
        if focus_new_tab:
            self._set_status_focused()
        
        print(f"Handle of page: {self.name}: {self.handle}")
        return handle
    
    def close_page(self) -> bool:
        "This function closes in the browser the current web page"

        if not self.website or not self.website.webbrowser:
            raise RuntimeError("No WebBrowser instance associated with this WebPage")
        
        if not self.handle:
            raise RuntimeError("This page does not have an open tab assigned")
        
        # Verify actual status
        if self.is_opened(): pass
        else: return True
    
        # Close the actual tab
        self.website.webbrowser.close_tab(self.handle)

        # Update page status
        self._set_status_closed()
        self._set_status_unfocused()

        # Return results
        return True
    
    def reload_page(self) -> bool:
        "This functions reloads the current web page"

        if not self.website or not self.website.webbrowser:
            raise RuntimeError("No WebBrowser instance associated with this WebPage")
        
        # Verify status
        if self.is_opened(): pass
        else: return False

        self.website.webbrowser.refresh(self.handle)
    
        return True
    
    def check_focus(self) -> bool:
        "This functions retrieves a boolean value that specify if the current page is focused"

        if not self.website or not self.website.webbrowser:
            return False
        
        # Verify status
        if self.is_opened(): pass
        else: return False
        
        current_tab = self.website.webbrowser.query_actual_tab()
        
        if self.handle == current_tab:
            self.__set_status_focused()
        else:
            self.__set_status_unfocused()
        
        return self.is_focus
    
    def go_back(self) -> bool:
        try:
            self.driver.back()
            return True
        except:
            return False
        
    def go_forward(self) -> bool:
        try:
            self.driver.forward()
            return True
        except:
            return False