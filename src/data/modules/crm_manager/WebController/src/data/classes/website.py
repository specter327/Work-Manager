# Library import
from __future__ import annotations

# Constants definition
SUPPORTED_PROTOCOLS = ("HTTP", "HTTPS")

# Classes definition
class WebSite:
    "This class provides an abstract method of a web site. Provides a simple way of organization and structure"

    def __init__(self,
        domain: str,
        webbrowser: webbrowser.WebBrowser, # pyright: ignore[reportUndefinedVariable]
        protocol: str,
        port: int,
        session_data: dict = None
        #cookies: list = None
    ):
        """Parameters example:
        domain: google.com
        webbrowser: WebBrowser object instance
        protocol: https
        port: 443
        """

        # Property assign
        self.domain = domain
        self.webbrowser = webbrowser

        # Verify protocol value
        if protocol.upper() in SUPPORTED_PROTOCOLS: pass
        else: raise ValueError(f"Invalid protocol: {protocol}. Available protocols: {SUPPORTED_PROTOCOLS}")

        self.protocol = protocol
        self.port = port
        self.session_data = session_data # Nuevo atributo para guardar todos los datos
        self.cookies = session_data.get('cookies', []) if session_data else []
        self.authenticated = None

        # Internal structures
        self.folders = {}
        self.pages = {}

    @property
    def base_url(self) -> str:
        return f"{self.protocol}://{self.domain}:{self.port}/"

    # Private methods
    def _set_authenticated(self) -> bool:
        self.authenticated = True
        return True

    def _set_deauthenticated(self) -> bool:
        self.authenticated = False
        return True

    # Public methods
    def authenticate_browser(self) -> bool:
        "This function authenticates the current domain and all their pages, only if theres cookies specified"

        if not self.cookies:
            print(f"No hay cookies de sesión en {self.domain} para inyectar.")
            return False

        if not self.webbrowser.is_opened():
            raise RuntimeError("El navegador debe estar abierto (WebBrowser.open_browser) antes de la autenticación.")
        
        
        # Llama al método del controlador que sabe cómo interactuar con Selenium
        print(f"🔑 Intentando inyectar {len(self.cookies)} cookies y storage en: {self.base_url}")
            
        # Llama al método del controlador, pasando el diccionario de sesión completo
        success = self.webbrowser.controller.add_cookies(
            self.cookies, 
            self.session_data, # <<< ¡PASAMOS EL DICCIONARIO COMPLETO AQUÍ!
            self.base_url
        )
        
        if success:
            print(f"✅ Autenticación exitosa para {self.domain}.")
            self._set_authenticated()
        else:
            print(f"❌ Autenticación fallida para {self.domain}. El servidor no validó la sesión.")
    
        return success

    def register_folder(self, name: str, folder: webfolder.WebFolder) -> bool: # type: ignore
        "This function appends a new WebFolder object instance to the current domain folders"
        self.folders[name] = folder

        return True
    
    def register_page(self, name: str, page: webpage.WebPage) -> bool: # type: ignore
        "This function appends a new WebPage object instance to the current domain pages"
        self.pages[name] = page

        return True
    
    def get_page(self, name: str) -> webpage.WebPage | None: # type: ignore # type: ignore
        "This function gets and retrieves a specified page by its name"
        return self.pages.get(name, False)
    
    def get_folder(self, name: str) -> webfolder.WebFolder | None: # type: ignore
        "This function gets and retrieves a specified folder by its names"
        return self.folders.get(name, False)

    def identify_current_page(self) -> object | None:
        for webpage_name in self.pages:
            # Get page
            webpage = self.get_page(webpage_name)

            # Identify if is the current page
            is_current_page = webpage.is_current_page()

            if is_current_page:
                return webpage
        
        return None