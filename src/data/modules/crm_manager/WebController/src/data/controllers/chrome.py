# Library import
import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException
from ..classes.webcontroller import BrowserController
from ..properties.constants import OPENED_STATE, CLOSED_STATE
from selenium.common.exceptions import InvalidArgumentException, NoSuchWindowException
from ..properties.exceptions import BrowserAlreadyOpenedError, BrowserNotOpenedError, HandleNotFoundError
from urllib.parse import urlparse

# Classes definition
class Controller(BrowserController):
    "Chrome browser controller implemented using Selenium WebDriver"

    def __init__(self,
        profile: str = None
    ):
        # Init hereditance
        super().__init__()

        self.profile = profile
        self.driver = None
         
    # Public methods
    def start(self, headless: bool, deactivate_security: bool, initial_url: str = None) -> bool:
        "Start a new Chrome browser instance"
        
        # 1. Opciones de Chrome
        chrome_options = Options()

        # --- 💡 Opciones Añadidas para Solucionar SessionNotCreatedException ---
        # Argumentos esenciales para evitar fallos de inicio de Chrome
        chrome_options.add_argument("--no-sandbox") # Necesario en muchos entornos (e.g., Linux/Docker)
        chrome_options.add_argument("--disable-dev-shm-usage") # Mejora la estabilidad en algunos entornos
        chrome_options.add_argument("--disable-extensions") # Evita que las extensiones interfieran

        if deactivate_security:
            chrome_options.add_argument("--disable-web-security")
        
        # ----------------------------------------------------------------------

        # Usa un perfil personalizado (o el predeterminado)
        if headless:
            chrome_options.add_argument("--headless=new")
            chrome_options.add_argument("--window-size=1920,1080")
        
        # IMPORTANTE: El valor de self.profile DEBE ser una RUTA ABSOLUTA válida,
        # y el perfil no debe estar abierto por otra instancia de Chrome.
        if self.profile:
            # Asegúrate de que 'self.profile' es el directorio **padre** de los perfiles.
            # Por ejemplo: 'C:\\Users\\Ejecutivo\\AppData\\Local\\Google\\Chrome\\User Data'
            chrome_options.add_argument(f"--user-data-dir={self.profile}")

        # 2. MEJORA DE MANTENIBILIDAD: Instala y usa el driver automáticamente
        service = Service(executable_path=ChromeDriverManager().install())
        
        print("Initial URL received:", initial_url)
        # 3. Lanza el navegador web usando el objeto Service
        # Envuelve esta llamada en un try/except para capturar y diagnosticar la SessionNotCreatedException
        try:
            #self.driver = webdriver.Chrome(service=service, options=chrome_options)

            # Si la pestaña actual es about:blank → ciérrala
            if initial_url:
                self.driver = webdriver.Chrome(service=service, options=chrome_options)

                # Guardar pestaña inicial (about:blank)
                initial_tab_id = self.driver.current_window_handle

                # Crear nueva pestaña
                self.driver.switch_to.new_window('tab')

                # Navegar en nueva pestaña
                self.driver.get(initial_url)

                # Cerrar pestaña about:blank
                self.driver.switch_to.window(initial_tab_id)
                self.driver.close()

                # Volver a la pestaña nueva
                self.driver.switch_to.window(self.driver.window_handles[-1])

        except WebDriverException as e:
            # Aquí puedes añadir logging o un mensaje de error más específico
            print(f"Error al iniciar el driver: {e}")
            print("VERIFICAR: 1. Ruta absoluta en self.profile. 2. Versión de Chrome/WebDriver. 3. Que Chrome no esté ya abierto.")
            raise # Vuelve a lanzar la excepción para que el programa falle de forma controlada
        
        # 4. Actualiza el estado del navegador (heredado)
        self._set_status_opened()

        # 5. Devuelve resultados
        return True
    
    def stop(self) -> bool:
        "Close the browser instance"
        if self.is_opened():
            self.driver.quit()
            self.driver = None
        
        # Update web browser status
        self._set_status_closed()

        # Return results
        return True
    
    def get_status(self) -> object:
        return self.state
    
    def close_tab(self, handle: str = None) -> bool:
        """Cierra una pestaña específica en segundo plano, sin alterar el foco actual."""
        if self.is_closed():
            raise BrowserNotOpenedError

        driver = self.driver
        current_handle = driver.current_window_handle
        handles = driver.window_handles

        # Validar que la pestaña a cerrar exista
        if handle not in handles:
            raise ValueError(f"Handle '{handle}' not found among open tabs")

        # Si el handle actual es el mismo, no podemos cerrarlo "en background"
        if handle == current_handle:
            raise RuntimeError("Cannot close the current active tab in background")

        # Cambiar temporalmente al tab objetivo y cerrarlo
        try:
            driver.switch_to.window(handle)
            driver.close()
        except Exception as e:
            raise RuntimeError(f"Error closing background tab: {e}")

        # Restaurar el foco original (si aún existe)
        remaining = driver.window_handles
        if current_handle in remaining:
            driver.switch_to.window(current_handle)
        elif remaining:
            driver.switch_to.window(remaining[-1])

        return True


    def open_tab(self,
        url: str,
        focus_new_tab=True
    ) -> object:
        # Save the actual handles
        existing_tabs = set(self.driver.window_handles)

        # Execute JavaScript to open a new tab
        try:
            self.driver.execute_script(f"window.open('{url}', '_blank');")
        except WebDriverException as Exception:
            raise RuntimeError(f"Error opening tab ({url}): {Exception.msg}")
        
        # Wait until appears the new tab
        timeout = 5
        start_time = time.time()
        new_tab = None

        while time.time() - start_time < timeout:
            current_tabs = set(self.driver.window_handles)
            new_handles = current_tabs - existing_tabs

            if new_handles:
                new_tab = new_handles.pop()
                break
            
            time.sleep(0.1)
        
        if not new_tab:
            raise TimeoutError(f"Failed to detect new tab after opening: {url}")
        
        if focus_new_tab:
            # Switch to the new tab
            self.driver.switch_to.window(new_tab)
        else:
            pass
    
        # Return results
        return new_tab
        

    def query_tabs(self) -> list:
        if self.is_opened():
            return self.driver.window_handles
        else:
            raise BrowserNotOpenedError

    def query_actual_tab(self) -> object:
        if self.is_opened():
            return self.driver.current_window_handle
        else:
            raise BrowserNotOpenedError

    def get_current_url(self) -> str:
        return self.driver.current_url

    def is_opened(self) -> bool:
        return self.state == OPENED_STATE
    
    def is_closed(self) -> bool:
        return self.state == CLOSED_STATE
    
    def refresh(self, handle: object) -> bool:
        current_handle = self.driver.current_window_handle

        if handle and handle in self.driver.window_handles:
            self.driver.switch_to.window(handle)
        
        self.driver.refresh()

        # Restablish the original tab if it was different
        if handle and handle != current_handle:
            self.driver.switch_to.window(current_handle)
        
        return True
    
    def get_driver(self) -> object:
        return self.driver
    
    def get_cookies(self) -> list:
        if self.is_opened():
            return self.driver.get_cookies()
        else:
            # Usa tu excepción personalizada
            raise BrowserNotOpenedError
    
    def add_cookies(self, cookies: list[dict], session_data: dict, target_url: str) -> bool:
        raise NotImplementedError
        """Inyecta cookies, local/session storage y verifica la autenticación."""
        if not self.is_opened():
            raise BrowserNotOpenedError

        # 1. Navegar al dominio objetivo (Obligatorio para que las cookies sean válidas)
        self.driver.get(target_url)

        # 2. Inyectar cookies (Tu lógica robusta existente, no la modificamos)
        for cookie in cookies:
            # ... (Tu lógica de limpieza de cookies va aquí, tal cual la tienes) ...
            try:
                pass
                #self.driver.add_cookie(cookie_clean)
            except InvalidArgumentException as e:
                # ... (Manejo de excepciones) ...
                continue
            except Exception as e:
                # ... (Manejo de excepciones) ...
                continue

        # >>> AÑADIR ESTE BLOQUE PARA INYECTAR LOCAL/SESSION STORAGE <<<
        if session_data and session_data.get('local_storage'):
            print("💉 Inyectando Local Storage...")
            # Iterar sobre las claves/valores guardados y reinyectarlos vía JS
            for key, value in session_data['local_storage'].items():
                # Usamos json.dumps para manejar valores complejos si los hubiera
                js_value = json.dumps(value) 
                script = f"window.localStorage.setItem('{key}', {js_value});"
                self.driver.execute_script(script)
                
        if session_data and session_data.get('session_storage'):
            print("💉 Inyectando Session Storage...")
            for key, value in session_data['session_storage'].items():
                js_value = json.dumps(value) 
                script = f"window.sessionStorage.setItem('{key}', {js_value});"
                self.driver.execute_script(script)

        # 3. Refrescar para aplicar los tokens
        self.driver.refresh()
        # ... (El resto de tu lógica de verificación es perfecta y se mantiene) ...
        # ... (self.driver.get(target_url), time.sleep(3), verificación de admin.oa.wowcredito.com) ...

        return True
    
    def execute_javascript(self, code: str, *args) -> str:
        return self.driver.execute_script(code, *args)
    
    def switch_focus_tab(self, handle: str) -> bool:
        try:
            self.driver.switch_to.window(handle)
            return True
        except NoSuchWindowException:
            raise HandleNotFoundError(f"El handle '{handle}' no existe o la ventana fue cerrada.")
            return False