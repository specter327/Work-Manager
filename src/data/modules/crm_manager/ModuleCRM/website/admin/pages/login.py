# Library import
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait # Clase principal para la espera
from selenium.webdriver.support import expected_conditions as EC # Módulos de condiciones
from selenium.common.exceptions import JavascriptException, WebDriverException
from typing import Tuple, List, Dict, Any
import json
from urllib.parse import urlparse

# Classes definition
class LoginPage:
    # Property definition
    TARGET_LOGIN_DOMAIN = "telesales.oa.wowcredito.com"
    USERNAME_FIELD: Tuple[By, str] = (By.XPATH, "//input[@placeholder='Please enter account']")
    PASSWORD_FIELD: Tuple[By, str] = (By.CSS_SELECTOR, "input[placeholder='Password']")
    LOGIN_PAGE = "login"
    LOGIN_PAGE_ROUTE = "passport"
    ADMIN_WEBSITE = "admin.oa.wowcredito.com"

    @property
    def driver(self) -> object:
        return self.website.webbrowser.driver
    
    # Private methods
    def _wait_for_element(self, locator: Tuple[By, str]) -> WebElement:
        wait = WebDriverWait(self.driver, 20)

        return wait.until(EC.presence_of_element_located(locator))
            
    def _find_username_field(self) -> object:
        return self._wait_for_element(self.USERNAME_FIELD)

    def _find_password_field(self) -> object:
        return self._wait_for_element(self.PASSWORD_FIELD)

    def _write_username(self, username: str, username_field: object) -> bool:
        username_field.clear() # Limpiar antes de escribir es una buena práctica
        username_field.send_keys(username)

        return True

    def _write_password(self, password: str, password_field: object) -> bool:
        password_field.clear() # Limpiar antes de escribir es una buena práctica
        password_field.send_keys(password)

        return True

    def _capture_session_data(self) -> dict:
        """
        Función auxiliar para extraer todos los datos de sesión relevantes 
        (Cookies, Local Storage, Session Storage, User-Agent, Token).
        """
        
        # 1. Extraer Cookies
        cookies = self.website.webbrowser.controller.driver.get_cookies()

        # 2. Extraer Local Storage
        local_storage_raw = self.website.webbrowser.controller.driver.execute_script(
            "return Object.keys(localStorage).reduce((obj, key) => { obj[key] = localStorage.getItem(key); return obj; }, {});"
        )
        # Intentar parsear a JSON si el valor es una cadena JSON
        local_storage = {}
        for k, v in local_storage_raw.items():
            try:
                local_storage[k] = json.loads(v)
            except (json.JSONDecodeError, TypeError):
                local_storage[k] = v
        
        # 3. Extraer Session Storage
        session_storage_raw = self.website.webbrowser.controller.driver.execute_script(
            "return Object.keys(sessionStorage).reduce((obj, key) => { obj[key] = sessionStorage.getItem(key); return obj; }, {});"
        )
        session_storage = {}
        for k, v in session_storage_raw.items():
            try:
                session_storage[k] = json.loads(v)
            except (json.JSONDecodeError, TypeError):
                session_storage[k] = v

        # 4. Intentar determinar la fuente principal del token (para logging)
        token_source = None
        main_token = None

        if "access_token" in local_storage:
            token_source = "Local Storage (access_token)"
            main_token = local_storage["access_token"]
        elif "token" in local_storage:
            token_source = "Local Storage (token)"
            main_token = local_storage["token"]
        elif "token" in session_storage:
            token_source = "Session Storage (token)"
            main_token = session_storage["token"]
        # Buscar token en cookies (ej. 'am_session')
        elif any("session" in cookie.get("name", "").lower() for cookie in cookies):
            token_source = "Cookies (am_session/otros)"

        # 5. Extraer User-Agent
        user_agent = self.website.webbrowser.controller.driver.execute_script("return navigator.userAgent")

        return {
            "token_source": token_source,
            "token": main_token,
            "cookies": cookies,
            "local_storage": local_storage,
            "session_storage": session_storage,
            "user_agent": user_agent,
            "current_url": self.website.webbrowser.controller.driver.current_url
        }
        
    # Public methods
    def is_current_page(self) -> bool:
        current_url = self.website.webbrowser.get_current_url()

        # 2. Parsear la URL actual
        parsed_url = urlparse(current_url)
            
        # Dominio esperado (sin puerto, para comparación)
        current_domain = parsed_url.netloc.split(':')[0]
        # Ruta esperada (ej: /passport/login)
        current_path = parsed_url.path
        
        # 3. Realizar la verificación de Dominio y Ruta
        domain_match = current_domain == self.ADMIN_WEBSITE
        path_match = current_path.startswith("/" + self.LOGIN_PAGE_ROUTE + "/" + self.LOGIN_PAGE)
        
        if domain_match and path_match:
            # Opcional: Agregar una verificación de presencia de elemento crítico (username field) 
            # para mayor robustez, si el método no es demasiado lento.
            return True
        else:
            # DEBUG: Útil para ver por qué falló la verificación
            # print(f"DEBUG: Dominio: {current_domain} ({domain_match}). Ruta: {current_path} ({path_match}).")
            return False

    def write_username(self, username: str) -> bool:
        # Find username field
        username_field = self._find_username_field()

        # Write username
        return self._write_username(username, username_field)

    def write_password(self, password: str) -> bool:
        # Find password field
        password_field = self._find_password_field()

        # Write password
        return self._write_password(password, password_field)

    def verify_login(self) -> bool:
        current_url = self.website.webbrowser.get_current_url()

        if not current_url:
            return False
        
        parsed_url = urlparse(current_url)
        current_domain = parsed_url.hostname

        if not current_domain:
            return False
        
        return current_domain.lower() == self.TARGET_LOGIN_DOMAIN.lower()

    def login(self, username: str, password: str) -> bool:
        # Write username
        self.write_username(username)

        # Write password
        self.write_password(password)

        # Capture session 
        while True:
            print("Waiting for log in...")
            if self.verify_login():
                break
        
        print("Session data:")
        session_data = self._capture_session_data()
        print(session_data)

        # Return results
        return session_data