# Library import
from selenium.common.exceptions import TimeoutException, NoSuchFrameException, NoSuchElementException, ElementClickInterceptedException, StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webelement import WebElement
from typing import Tuple


# Classes definition
class ContactsList:
    # Property definition
    MAIN_CONTENT_IDENTIFIER: Tuple[str, str] = (By.ID, "maincontent")
    TOTAL_CONTACTS_LINK_LOCATOR: Tuple[str, str] = (By.XPATH, "//a[@href='/apps/callout/names/index.html']")

    TIMEOUT = 10
    PAGE_TYPE: str = "CALL_LIST"

    # Private methods
    def _focus_main_contacts_frame(self) -> bool:
        # Obtenemos el tipo de selector y el valor (el ID o nombre del iframe)
        locator_type, iframe_id = self.MAIN_CONTENT_IDENTIFIER
        
        try:
            # 1. Esperar a que el iframe esté presente en el DOM principal
            # Usamos el localizador completo (By.ID, "maincontent") para la espera.
            WebDriverWait(self.website.webbrowser.driver, 20).until(
                EC.presence_of_element_located(self.MAIN_CONTENT_IDENTIFIER)
            )
            
            # 2. Cambiar al iframe usando el ID/Name (el segundo elemento del localizador)
            self.website.webbrowser.driver.switch_to.frame(iframe_id)
            print(f"✅ Foco cambiado al iframe: '{iframe_id}'.")
            return True
        except (TimeoutException, NoSuchFrameException):
            # Impresión de error sin usar colorama.
            print(f"❌ Error: No se pudo localizar el iframe '{iframe_id}' o falló el cambio de foco.")
            return False
        except Exception as e:
            # Impresión de error sin usar colorama.
            print(f"❌ Error desconocido al enfocar el iframe '{iframe_id}': {e}")
            return False

    def _unfocus_main_contacts_frame(self) -> bool:
        try:
            self.website.webbrowser.driver.switch_to.default_content()
        except Exception as e:
            print(f"⚠️ Advertencia: Fallo al intentar salir del foco del iframe. {e}")
            return False
        
        return True # Retorna la instancia de la página para encadenamiento

    def _find_all_contacts_list_button(self) -> WebElement | None:
        try:
            # Esperar a que el elemento esté presente en el DOM
            link_element = WebDriverWait(self.website.webbrowser.driver, self.TIMEOUT).until(
                EC.presence_of_element_located(self.TOTAL_CONTACTS_LINK_LOCATOR)
            )
            
            return link_element
            
        except TimeoutException:
            # Captura si el elemento no aparece en el DOM a tiempo
            print(f"❌ Error: Tiempo de espera agotado. El enlace '{self.TOTAL_CONTACTS_LINK_LOCATOR[1]}' no fue encontrado.")
            return None
        except Exception as e:
            # Captura cualquier otro error inesperado
            print(f"❌ Error inesperado al buscar el enlace: {type(e).__name__} - {e}")
            return None
    
    def _click_all_contacts_list_button(self, all_contacts_list_button: WebElement) -> bool:
        if all_contacts_list_button is None:
            print("❌ Error: El elemento proporcionado es None (nulo). No se puede hacer clic.")
            return False
            
        try:
            # 1. Intentar hacer clic directamente
            all_contacts_list_button.click()
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
    def go_to_all_contacts_menu(self, use_javascript: bool = True) -> bool:
        if use_javascript:
            query_code = """// Search the frame document element
let frameDocumentElement = document.getElementById("maincontent");

// Verify the search result
if (frameDocumentElement === null){
    return null;
}

// Search the "all contacts" button
let allContactsMenuButton = frameDocumentElement.contentDocument.querySelector("a[href='/apps/callout/names/index.html']");

// Verify the search result
if (allContactsMenuButton === null){
    return null;
}

try {
    // Execute the clic button interaction
    allContactsMenuButton.click();
    return true;
} catch (error) {
    return false;
}"""

            execution_result = self.website.webbrowser.execute_javascript(query_code)
            return execution_result
        else:
            pass
            
        # Cambiar foco a foco general
        print("ESTO SE ESTA EJECUTANDO")
        self._unfocus_main_contacts_frame()
        
        switch_focus_result = self._focus_main_contacts_frame()

        if switch_focus_result:
            print("CAMBIAMOS DE FOCO EXITOSAMENTE")
            pass
        else:
            print("ERROR AL CAMBIAR DE FOCO")
            return False
        
        # Search the all contacts list button
        all_contacts_list_button = self._find_all_contacts_list_button()
        print("BOTON ENCONTRADO:", all_contacts_list_button)

        # Click the button
        if all_contacts_list_button:
            click_result = self._click_all_contacts_list_button(all_contacts_list_button)

            print("SALIENDO DEL FOCO DEL FRAME...")
            self._unfocus_main_contacts_frame()
            return click_result
        else:
            self._unfocus_main_contacts_frame()
            return False
        

    def go_to_patrol_tasks(self, use_javascript: bool = True) -> bool | None:
        if use_javascript:
            query_code = """// Search the frame document element
    let frameDocumentElement = document.getElementById("maincontent");

    // Verify the search result
    if (frameDocumentElement === null){ return null; }

    // Search the button element
    let buttonPatrolTasksElement = frameDocumentElement.contentDocument.querySelector("li.layui-nav-item a[href='/apps/callout/cruisingtasks/index.html']");

    // Verify the search result
    if (buttonPatrolTasksElement === null){ return null; }

    // Execute the click interaction
    try {
        buttonPatrolTasksElement.click();
        return true;
    } catch (error) {
        return false;
    }"""

            return self.website.webbrowser.execute_javascript(query_code)
        else:
            raise NotImplementedError
        

    def go_to_task_allocation_activities(self, use_javascript: bool = True) -> bool:
        if use_javascript:
            query_code = """// Search the frame document element
    let framedocumentElement = document.getElementById("maincontent");

    // Verify the search result
    if (framedocumentElement === null){ return null; }

    // Search the button element
    let taskAllocationButton = framedocumentElement.contentDocument.querySelector("li.layui-nav-item a[href='/apps/callout/cruisingtasks/dis/index.html']");

    // Verify the search result
    if (taskAllocationButton === null){ return null;}

    // Execute the click interaction
    try {
        taskAllocationButton.click();
        return true;
    } catch (error) {
        return false;
    }"""

            return self.website.webbrowser.execute_javascript(query_code)
        else:
            raise NotImplementedError