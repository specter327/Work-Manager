# Library import
from .properties import Contact
from .properties import DiscountCoupon
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, NoSuchFrameException
from selenium.common.exceptions import TimeoutException
from .webpageheader import WebPageHeader
from typing import Any, Dict, List, Tuple
import time

# Classes definition
class ContactProfilePage(WebPageHeader):
    # Property definition
    CONTACT_PROFILE_SOURCE: str = "/apps/callout/names/preview.html"
    CALL_CONSOLE_LOCATOR: Tuple[str, str] = (By.ID, "outboundCallConsole")
    CONTACT_INFO_LOCATOR: Tuple[str, str] = (By.ID, "contactsConsole")
    INFO_LIST_CONTAINER: Tuple[str, str] = (By.ID, "ukefu_contacts_info")
    INFO_LIST_ITEMS: Tuple[str, str] = (By.CSS_SELECTOR, "#ukefu_contacts_info ul.info-list li")
    CLOSE_PROFILE_BUTTON: Tuple[str, str] = (By.CSS_SELECTOR, "li[lay-id='outboundCallConsole'] i.layui-tab-close")
    CALL_BUTTON_LOCATOR: Tuple[str, str] = (By.CSS_SELECTOR, "#softphone-callout .soft-function.outboundcall")
    PREVIEW_CALL_BUTTON_LOCATOR: Tuple[str, str] = (By.CSS_SELECTOR, "#softphone-callout .soft-function.preview")
    HANGUP_BUTTON_LOCATOR: Tuple[str, str] = (By.CSS_SELECTOR, "#softphone-hungup") 

    
    TIMEOUT: int = 10
    
    # Private methods
    def _search_hangup_button(self) -> WebElement | None:
        try:
            button = WebDriverWait(self.website.webbrowser.driver, self.TIMEOUT).until(
                EC.presence_of_element_located(self.HANGUP_BUTTON_LOCATOR)
            )
            print("🔍 Botón 'Colgar' localizado.")
            return button
        except:
            print("❌ No se pudo localizar el botón 'Colgar'")
            return None
        
    def _click_hangup_button(self, hangup_button: WebElement) -> bool:
        # Verify that the button is not disabled
        try:
            classes = hangup_button.get_attribute("class")
            if "disabled" in classes.lower():
                return None
        except:
            return False
        
        # Try to click the element
        try:
            hangup_button.click()
            return True
        except:
            return False
        
    def _search_preview_call_button(self) -> WebElement | None:
        try:
            button = WebDriverWait(self.website.webbrowser.driver, self.TIMEOUT).until(
                EC.presence_of_element_located(self.PREVIEW_CALL_BUTTON_LOCATOR)
            )
            print("🔍 Botón 'Previsualizar' localizado exitosamente.")
            return button
        except:
            return None
    
    def _search_call_button(self) -> WebElement | None:
        try:
            button = WebDriverWait(self.website.webbrowser.driver, self.TIMEOUT).until(
                EC.presence_of_element_located(self.CALL_BUTTON_LOCATOR)
            )
            print("🔍 Botón 'Llamar' localizado exitosamente.")
            return button
        except Exception as e:
            print(f"❌ No se pudo localizar el botón 'Llamar': {e}")
            return None
    
    def _click_call_button(self, call_button: WebElement) -> bool:
        try:
            # Validar si el botón está habilitado
            is_disabled = call_button.get_attribute("class").find("disabled") != -1
            if is_disabled:
                print("⚠️ Botón 'Llamar' está deshabilitado actualmente.")
                print("OMISION ANULADA")
                #return False

            call_button.click()
            print("📞 Acción de llamada ejecutada correctamente.")
            return True

        except Exception as e:
            print(f"❌ Error al hacer clic en el botón 'Llamar': {e}")
            return False
        
    def _search_maincontact_frame(self) -> WebElement:
        try:
            self._unfocus_maincontact_frame()
            
            # Esperamos la presencia del elemento en el DOM (hasta 10 segundos)
            iframe_element = WebDriverWait(self.website.webbrowser.driver, self.TIMEOUT+30).until(
                EC.presence_of_element_located(self.CALL_CONSOLE_LOCATOR)
            )
            
            return iframe_element
        except TimeoutException:
            # Si el elemento no aparece en el tiempo de espera
            print(f"❌ La página NO es la esperada: iframe con segmento '{self.CALL_CONSOLE_LOCATOR}' no se encontró en el DOM después de 10 segundos.")
            return False
        except Exception as e:
            # Manejo de cualquier otro error de Selenium o Python
            print(f"💥 Error inesperado al verificar la página: {e}")
            return False
    
    def _focus_maincontact_frame(self, iframe: WebElement) -> bool:
        try:
            self.website.webbrowser.driver.switch_to.frame(iframe)
            print("✅ Foco del driver cambiado exitosamente al iframe.")
            return True
        except NoSuchFrameException:
            print("❌ ERROR: El elemento proporcionado no parece ser un iframe válido o ya no está presente en el DOM.")
            return False
        except Exception as e:
            print(f"💥 Error inesperado al cambiar el foco al iframe: {e}")
            return False
    
    def _unfocus_maincontact_frame(self) -> bool:
        try:
            self.website.webbrowser.driver.switch_to.default_content()
            return True
        except:
            return False
    
    def _search_contactinfo_frame(self) -> WebElement | None:
        try:
            iframe = WebDriverWait(self.website.webbrowser.driver, self.TIMEOUT).until(
                EC.presence_of_element_located(self.CONTACT_INFO_LOCATOR)
            )
            return iframe

        except (TimeoutException, NoSuchElementException):
            print("[WARN] No se encontró el iframe 'contactsConsole'")
            return None
    
    def _focus_contactinfo_frame(self, iframe: WebElement) -> bool:
        try:
            self.website.webbrowser.driver.switch_to.frame(iframe)
            return True
        except:
            return False
        
    def _unfocus_contactinfo_frame(self) -> bool:
        try:
            self.website.webbrowser.driver.switch_to.parent_frame()
            return True
        except:
            return False
        
    def _search_close_profile_button(self) -> WebElement | None:
        try:
            button = WebDriverWait(self.website.webbrowser.driver, self.TIMEOUT).until(
                EC.presence_of_element_located(self.CLOSE_PROFILE_BUTTON)
            )
            print("🔍 Botón 'Cerrar perfil' localizado exitosamente.")
            return button
        except Exception as e:
            print(f"❌ No se pudo localizar el botón 'Cerrar perfil': {e}")
            return None
    
    def _click_close_profile_button(self, button: WebElement) -> bool:
        try:
            button.click()
            return True
        except:
            return False
    
    # Public methods
    def extract_contact_information(self, use_javascript: bool = True) -> dict:
        if use_javascript:
            query_code = """// Functions definition
function convertMapToJson(data) {
    // Caso base: Si el dato no es un objeto que necesite ser procesado, se devuelve.
    if (data === null || typeof data !== 'object') {
        return data;
    }

    // Caso 1: Si es un Map (el problema principal)
    if (data instanceof Map) {
        // Convertimos el Map en un objeto JavaScript plano ({ key: value })
        const obj = {};
        for (const [key, value] of data.entries()) {
            // Llamamos recursivamente para manejar valores anidados (como Arrays o Maps)
            obj[key] = convertMapToJson(value);
        }
        return obj;
    }

    // Caso 2: Si es un Array (necesitamos procesar sus elementos recursivamente)
    if (Array.isArray(data)) {
        // Mapeamos cada elemento del array y lo convertimos
        return data.map(item => convertMapToJson(item));
    }

    // Caso 3: Si es un objeto plano (Object), procesamos sus propiedades recursivamente
    // Esto es útil si hay objetos planos en la estructura, aunque en tu caso principal no los hay.
    if (data.constructor === Object) {
        const obj = {};
        for (const key in data) {
            if (Object.prototype.hasOwnProperty.call(data, key)) {
                obj[key] = convertMapToJson(data[key]);
            }
        }
        return obj;
    }

    // Si es otro tipo de objeto (Date, RegExp, etc.), lo devolvemos tal cual.
    return data;
}

function getContactProfile(){
    // search the titles elements
    let titleElements = document.querySelectorAll("div.el-form-item__label");

    // Verify the search result
    if (titleElements.length === 0){
        return null;
    }

    // Search the value elements
    let valueElements = document.querySelectorAll("div.el-form-item__content");

    // Verify the search result
    if (valueElements.length === 0){
        return null;
    }

    // Process the data
    let indexs = Array.from({ length: titleElements.length }, (v, i) => i);

    let contactProfile = new Map();

    for (let index of indexs){
        // Set title and value
        contactProfile.set(titleElements[index].textContent.trim(), valueElements[index].textContent.trim());
    }

    // Return contact profile
    return contactProfile;
}

// Use
let contactProfile = getContactProfile();

// Convert the contact profile
let JSONContactProfile = convertMapToJson(contactProfile);

return JSONContactProfile;"""
            contact_profile = self.website.webbrowser.execute_javascript(query_code)
            processed_contact_profile = {}

            if contact_profile:
                for key in contact_profile:
                    new_key = key.replace(":", "")
                    processed_contact_profile[new_key] = contact_profile[key]
            
            return processed_contact_profile
        else:
            pass
        
        """
        Extrae la información del perfil del contacto dentro del iframe `contactsConsole`.
        Requiere que el frame principal y el secundario hayan cargado correctamente.
        Retorna un diccionario con pares clave:valor.
        """

        # Buscar y enfocar el frame principal
        maincontact_frame = self._search_maincontact_frame()
        if not maincontact_frame or not self._focus_maincontact_frame(maincontact_frame):
            print("❌ No se pudo enfocar el FRAME de CONTACTO (main).")
            return {}

        # Buscar y enfocar el frame donde está la información
        contactinfo_frame = self._search_contactinfo_frame()
        if not contactinfo_frame or not self._focus_contactinfo_frame(contactinfo_frame):
            print("❌ No se pudo enfocar el FRAME de INFORMACIÓN DEL CONTACTO (secondary).")
            self._unfocus_maincontact_frame()
            return {}

        data = {}

        try:
            # Esperar presencia de elementos de detalle
            WebDriverWait(self.website.webbrowser.driver, self.TIMEOUT + 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".el-form-item"))
            )

            # Extraer elementos de la página
            items = self.website.webbrowser.driver.find_elements(By.CSS_SELECTOR, ".el-form-item")

            for item in items:
                try:
                    label = item.find_element(By.CSS_SELECTOR, ".el-form-item__label").text.strip().replace(":", "")
                    value = item.find_element(By.CSS_SELECTOR, ".el-form-item__content").text.strip()

                    if label:
                        data[label] = value
                except:
                    continue

            print(f"📦 Datos del perfil extraídos: {len(data)} campos")
            contact = Contact(data)
        except Exception as e:
            print(f"💥 Error extrayendo datos del perfil: {e}")

        finally:
            # Salir correctamente de los iframes
            self._unfocus_contactinfo_frame()
            self._unfocus_maincontact_frame()

        return contact

    def extract_call_details(self, use_javascript: bool = True) -> dict | bool:
        if use_javascript:
            query_code = """// Functions definition
function convertMapToJson(data) {
    // Caso base: Si el dato no es un objeto que necesite ser procesado, se devuelve.
    if (data === null || typeof data !== 'object') {
        return data;
    }

    // Caso 1: Si es un Map (el problema principal)
    if (data instanceof Map) {
        // Convertimos el Map en un objeto JavaScript plano ({ key: value })
        const obj = {};
        for (const [key, value] of data.entries()) {
            // Llamamos recursivamente para manejar valores anidados (como Arrays o Maps)
            obj[key] = convertMapToJson(value);
        }
        return obj;
    }

    // Caso 2: Si es un Array (necesitamos procesar sus elementos recursivamente)
    if (Array.isArray(data)) {
        // Mapeamos cada elemento del array y lo convertimos
        return data.map(item => convertMapToJson(item));
    }

    // Caso 3: Si es un objeto plano (Object), procesamos sus propiedades recursivamente
    // Esto es útil si hay objetos planos en la estructura, aunque en tu caso principal no los hay.
    if (data.constructor === Object) {
        const obj = {};
        for (const key in data) {
            if (Object.prototype.hasOwnProperty.call(data, key)) {
                obj[key] = convertMapToJson(data[key]);
            }
        }
        return obj;
    }

    // Si es otro tipo de objeto (Date, RegExp, etc.), lo devolvemos tal cual.
    return data;
}

// Search the frame document element
let frameDocumentElement = document.getElementById("outboundCallConsole");
console.log("Frame document:", frameDocumentElement);

// Verify the search result
if (frameDocumentElement === null){ return null; }

// Search the information container
let informationStructure = frameDocumentElement.contentDocument.querySelectorAll("ul.info-list li");

// Verify the search result
if (informationStructure === null || informationStructure.length === 0){ return null; }

// Process all the data structure
let informationFields = new Map();

for (let informationField of informationStructure){
    // Extract the field text
    if (informationField.textContent.trim().length === 0){ continue; }

    informationFields.set(informationField.textContent.trim().split(":")[0], informationField.textContent.trim().split(":")[1]);
}

// Return results
return convertMapToJson(informationFields);"""

            return self.website.webbrowser.execute_javascript(query_code)
        else:
            pass
        # Search main contact frame
        maincontact_frame = self._search_maincontact_frame()
        
        if not maincontact_frame:
            print("Frame de contacto NO ENCONTRADO") 
            return False
        
        # Switch the focus to the contact frame
        if not self._focus_maincontact_frame(maincontact_frame):
            print("Error al ENFOCAR AL FRAME de CONTACTO") 
            return False
        
        # Search and extract all the information
        call_details = {}
        try:
            print("Iniciando extracción de detalles de la llamada dentro del iframe...")
            
            # Esperar a que los elementos de la lista estén visibles dentro del iframe
            WebDriverWait(self.website.webbrowser.driver, self.TIMEOUT).until(
                EC.visibility_of_element_located(self.INFO_LIST_ITEMS)
            )
            
            # 2. Encontrar todos los elementos <li>
            info_items = self.website.webbrowser.driver.find_elements(*self.INFO_LIST_ITEMS)
            
            # 3. Iterar y extraer clave-valor
            for item in info_items:
                text = item.text.strip()
                
                # Intentamos dividir por el colon ancho ('：') o el colon estándar (':')
                if '：' in text:
                    key, value = text.split('：', 1)
                elif ':' in text:
                    key, value = text.split(':', 1)
                else:
                    # Saltar líneas que no contienen el par clave-valor esperado (como el último <li> vacío)
                    continue 

                # Limpiamos y almacenamos
                key = key.strip()
                # Eliminamos la última línea vacía y el valor de un solo caracter
                value = value.strip()
                if key and value != "：":
                    call_details[key] = value
                
        except Exception as e:
            print(f"💥 Error al extraer los detalles de la llamada dentro del iframe: {e}")
        finally:
            # 4. Siempre regresar el foco al contenido principal
            self._unfocus_maincontact_frame()
            
        print(f"✅ Extracción de detalles finalizada. Se encontraron {len(call_details)} pares clave-valor.")
        return call_details

    def close_profile(self, use_javascript: bool = True) -> bool:
        if use_javascript:
            pass
        else:
            pass
        
        # Search the close button
        close_button = self._search_close_profile_button()
        
        if close_button: pass
        else:
            print("Error finding the close button")
            return False
        
        # Click the close button
        if self._click_close_profile_button(close_button): return True
        else: return False
                
    def is_current_page(self, use_javascript: bool = True) -> bool:
        if use_javascript:
            query_code = """function isCurrentPage(){
    // Search the contact profile
    let contactProfileConsole = document.getElementById("outboundCallConsole");

    // Verify the search result
    if (contactProfileConsole === null){ return null; }

    // Verify the URL
    if (contactProfileConsole.src.includes("/apps/callout/names/preview.html")){
        return true;
    } else {
        return false;
    }
}

return isCurrentPage();"""

            return self.website.webbrowser.execute_javascript(query_code)
        else:
            pass

        search_result = self._search_maincontact_frame()
        
        if search_result: return True
        else: return False