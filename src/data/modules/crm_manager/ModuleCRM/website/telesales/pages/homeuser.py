# Library import
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchFrameException, NoSuchElementException, ElementClickInterceptedException, StaleElementReferenceException
from selenium.webdriver.remote.webelement import WebElement
from .webpageheader import WebPageHeader

# Classes definition
class HomeUserPage(WebPageHeader):
    # Property definition
    USER_DOMAIN = "telesales.oa.wowcredito.com"
    TIEMPO_LIMITE_CARGA = 10
    CLAVE_MARCO_PAGINA_PRINCIPAL = (By.ID, "maincontent")
    ENLACE_PAGINA_PRINCIPAL = "/apps/content.html"

    TIMEOUT = 10
    TOTAL_CALLMENU_BUTTON_LOCATOR = (By.XPATH, "//a[@data-href='/apps/callout/names/home.html']")
    

    # Private methods
    def _find_callmenu_button(self) -> WebElement | None:
        try:
            # 2. Esperar a que el elemento sea localizable y esté presente en el DOM
            link_element = WebDriverWait(self.website.webbrowser.driver, self.TIMEOUT).until(
                EC.presence_of_element_located(self.TOTAL_CALLMENU_BUTTON_LOCATOR)
            )
            
            # 3. Retornar el elemento encontrado
            print("✅ Elemento encontrado. Retornando WebElement.")
            return link_element
            
        except TimeoutException:
            print(f"❌ Error: Tiempo de espera agotado ({self.TIMEOUT}s). El elemento no fue encontrado.")
            return None
        except NoSuchElementException:
            # Esto es raro si usamos presence_of_element_located, pero es una buena práctica
            print("❌ Error: El elemento no existe en el DOM.")
            return None
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
            return None

    def _click_callmenu_button(self, callmenu_button: WebElement) -> bool:
        if callmenu_button is None:
            print("❌ Error: El elemento proporcionado es None (nulo). No se puede hacer clic.")
            return False
            
        try:
            # 1. Intentar hacer clic directamente
            callmenu_button.click()
            print(f"✅ Clic exitoso en el elemento.")
            return True
            
        except StaleElementReferenceException:
            # Esto ocurre si el elemento se ha recargado o ya no está en el DOM 
            # (aunque en este caso el elemento es el resultado de una búsqueda reciente)
            print("⚠️ Advertencia: El elemento se volvió obsoleto (Stale). Intenta volver a buscarlo antes de hacer clic.")
            return False
            
        except ElementClickInterceptedException:
            # Esto sucede si otro elemento (como un overlay, modal o barra de carga) está cubriendo el botón.
            print("⚠️ Advertencia: Otro elemento interceptó el clic. Puede que haya un modal o una barra de carga activa.")
            # Opcional: Aquí podrías añadir lógica para cerrar el modal o esperar.
            return False
            
        except Exception as e:
            # Capturar cualquier otro error que impida el clic
            print(f"❌ Error al intentar hacer clic: {type(e).__name__} - {e}")
            return False

    # Public methods
    def go_to_callmenu(self) -> bool:
        # Search for the call menu button
        callmenu_button = self._find_callmenu_button()

        if callmenu_button:
            # Click the call menu button
            click_result = self._click_callmenu_button(callmenu_button)

            return click_result
        else:
            return False

    def is_current_page(self, use_javascript: bool = True) -> bool | None:
        if use_javascript:
            query_code = """// Search the frame document element
let frameDocumentElement = document.getElementById("maincontent");

// Verify the search result
if (frameDocumentElement === null){
    return null;
}

// Verify the source URL
if (frameDocumentElement.getAttribute("src")){
    if (frameDocumentElement.src.includes("/apps/content.html")){
        return true;
    } else {
        return false;
    }
}
"""

            execution_result = self.website.webbrowser.execute_javascript(query_code)
            return execution_result
        else:
            pass
        
        print(f"Buscando el iframe principal con selector: {self.CLAVE_MARCO_PAGINA_PRINCIPAL}")
        try:
            # 1. Espera explícita para que el iframe esté presente en el DOM y obtener la referencia al elemento.
            iframe_element = WebDriverWait(self.website.webbrowser.driver, self.TIEMPO_LIMITE_CARGA).until(
                # Usamos EC.presence_of_element_located para obtener el elemento.
                EC.presence_of_element_located(self.CLAVE_MARCO_PAGINA_PRINCIPAL)
            )
            
            # 2. **NUEVA VERIFICACIÓN:** Obtener y comparar el atributo 'src' del iframe.
            current_src = iframe_element.get_attribute("src")
            
            # NOTA: Uso 'in' por si el 'src' incluye la URL completa (ej: https://.../apps/content.html)
            if current_src and self.ENLACE_PAGINA_PRINCIPAL in current_src:
                print("✅ Detección exitosa: El iframe 'maincontent' está presente y el SRC es correcto.")
                is_home_page = True
            else:
                # El iframe existe, pero el src no es el esperado.
                print(f"❌ Detección fallida: Iframe encontrado, pero el SRC no coincide.")
                print(f"   SRC encontrado: '{current_src}' | SRC esperado: '{self.ENLACE_PAGINA_PRINCIPAL}'")
                is_home_page = False
                
        except TimeoutException:
            # El tiempo de espera se agotó sin encontrar el elemento.
            print(f"❌ Detección fallida: El iframe '{self.CLAVE_MARCO_PAGINA_PRINCIPAL[1]}' no fue encontrado después de {self.TIEMPO_LIMITE_CARGA} segundos.")
            is_home_page = False
                
        return is_home_page        
        
    def get_user_info(self, use_javascript: bool = True) -> str | bool:
        if use_javascript:
            query_code = """// Search the frame document element
    let frameDocumentElement = document.getElementById("maincontent");

    // Verify the search result
    if (frameDocumentElement === null){
        return null;
    }

    // Search the text content
    let textContainer = frameDocumentElement.querySelector("div.ukefu-user-index");

    // Verify the search result
    if (textContainer === null){
        return null;
    }

    // Extract the user information
    return textContainer.textContent.trim();"""

            execution_result = self.website.webbrowser.execute_javascript(query_code)
            return execution_result
        else:
            raise NotImplementedError