# Library import
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import TimeoutException, NoSuchElementException, NoSuchFrameException
from bs4 import BeautifulSoup
from typing import Tuple, List, Dict, Literal, Any
from urllib.parse import urlparse
import re
import json
import time
from .contactslistsheader import ContactsList
from .webpageheader import WebPageHeader
from .properties import Contact
from .properties import DiscountCoupon
from .properties import serialize_object
from datetime import datetime

# Property definition
GENRES = Literal["MASCULINO", "FEMENINO"]
USER_STATUSES = Literal["APROBADO"]

# Functions definition
def date_to_epoch(date_time: str, format: str = None) -> int:
    """
    Convierte una cadena de fecha y hora en formato 'YYYY-MM-DD HH:MM:SS'
    a un timestamp Epoch (segundos desde 1970-01-01 00:00:00 UTC).

    Args:
        date_string: La cadena de fecha y hora a convertir (ej: '2025-11-24 07:50:09').

    Returns:
        El timestamp Epoch como un entero, o None si la cadena es inválida o vacía.
    """
    if not date_time:
        return None

    # Formato de la cadena de entrada: YYYY-MM-DD HH:MM:SS
    # %Y: Año con siglo (2025)
    # %m: Mes como número (11)
    # %d: Día del mes (24)
    # %H: Hora (24 horas) (07)
    # %M: Minuto (50)
    # %S: Segundo (09)
    if format:
        date_format = format
    else:
        date_format = "%Y-%m-%d %H:%M:%S"
    
    try:
        # 1. Parsear la cadena a un objeto datetime
        datetime_object = datetime.strptime(date_time, date_format)
        
        # 2. Obtener el timestamp Epoch (que es un float)
        # Nota: Python asume que la hora es local si no se especifica la zona horaria.
        epoch_float = datetime_object.timestamp()
        
        # 3. Convertir a entero (como generalmente se usa el Epoch)
        return int(epoch_float)
    
    except ValueError:
        # Manejar errores si el formato de la cadena no coincide
        print(f"Error: La cadena de fecha '{date_time}' no coincide con el formato '{date_format}'.")
        return None

# Classes definition
class TotalContactsPage(ContactsList, WebPageHeader):
    # Property definition
    QUERY_PARAMETERS = {
        "p":int
    }

    CALL_MENU_LOCATOR: Tuple[str, str] = (By.ID, "maincontent")
    CALL_MENU_ROUTE = "/apps/callout/names/home.html"

    TOTAL_CONTACTS_LOCATOR: Tuple[str, str] = (By.ID, "maincontent")
    TOTAL_CONTACTS_ROUTE = "/apps/callout/names/index.html"
    TOTAL_CONTACTS_TITLE: Tuple[str, str] = (
        By.XPATH, 
        "//h3[@class='box-title' and contains(text(), 'Todas mis listas')]"
    )
    
    PREVIOUS_PAGE_LOCATOR: Tuple[str, str] = (By.CSS_SELECTOR, "a.layui-laypage-prev")
    CURRENT_PAGE_LOCATOR: Tuple[str, str] = (By.CSS_SELECTOR, "span.layui-laypage-curr")
    
    NEXT_PAGE_LOCATOR: Tuple[str, str] = (By.CSS_SELECTOR, "a.layui-laypage-next")
    FIRST_CONTACT_LINK_LOCATOR: Tuple[str, str] = (By.CSS_SELECTOR, "a[data-href*='preview.html']")

    TIMEOUT_LIMIT = 10

    #CONTACTS_TABLE_LOCATOR = (By.XPATH, "//table[@class='layui-table']/tbody/tr[contains(@style, 'height')]")
    DATA_ROWS_LOCATOR: Tuple[str, str] = (By.XPATH, "//div[@class='row']/table[1]/tbody/tr")
    ACTION_ROWS_LOCATOR: Tuple[str, str] = (By.XPATH, "//div[@class='row']/table[2]/tbody/tr")
    HEADER_LOCATOR: Tuple[str, str] = (By.XPATH, "//div[@class='row']/table[1]/thead/tr/th")

    CONTACTS_TABLE_LOCATOR: Tuple[str, str] = (
        By.XPATH, 
        "//table[@class='layui-table']/tbody/tr[./td[1]/input and not(contains(@style, 'display: none'))]"
    )
    #CONTACTS_TABLE_LOCATOR: Tuple[By, str] = (By.ID, "contacts-grid")
    #CONTACT_LOCATOR: Tuple[By, str] = (By.XPATH, "//div[contains(text(), 'No hay registros')]")
    #PAGINATION_CONTAINER_LOCATOR: Tuple[By, str] = (By.CLASS_NAME, "layui-laypage-curr")

    # Private method
    def _identify_call_menu(self) -> bool:
        try:
            # Identify call menu iframe page
            iframe_element = WebDriverWait(self.website.webbrowser.driver, self.TIMEOUT_LIMIT).until(
                EC.presence_of_element_located(self.CALL_MENU_LOCATOR)
            )
            
            # Verify iframe URL source
            print("IFRAME ELEMENT MENU LLAMADAS:", iframe_element)
            print("SOURCE:", iframe_element.get_attribute("src"))
            print("CALL MENU ROUTE:", self.CALL_MENU_ROUTE)
            
            src_value = iframe_element.get_attribute("src")

# Se utiliza endswith para asegurar que la ruta sea la correcta,
            # ignorando el dominio o posibles parámetros GET al inicio.
            if src_value and self.CALL_MENU_ROUTE in src_value:
                return True
            else:
                return False
                
        except (TimeoutException, NoSuchElementException):
            # El iframe no fue encontrado o no existe en el DOM.
            return False
        except Exception:
            # Manejo de otros errores del driver
            return False
    
    def _identify_totalcontacts_page(self) -> bool:
        if self._identify_call_menu():
            print("MENU DE LLAMADAS DETECTADO! 1.1")
            # Change focus to iframe element
            is_index_content = False

            try:
                iframe_element = WebDriverWait(self.website.webbrowser.driver, self.TIMEOUT_LIMIT).until(
                    EC.presence_of_element_located(self.TOTAL_CONTACTS_LOCATOR)
                )
                
                # 2. Cambiar el foco al IFRAME
                print("IFRAME TOTAL CONTACTS ELEMENT:", iframe_element)
                print("IFRAME TOTAL CONTACTS SOURCE:", iframe_element.get_attribute("src"))
                
                self.website.webbrowser.driver.switch_to.frame(iframe_element)

                # 3. Verificar la presencia del elemento único de la página de contactos
                WebDriverWait(self.website.webbrowser.driver, 5).until(
                    EC.presence_of_element_located(self.TOTAL_CONTACTS_TITLE)
                )
                
                # Si la espera es exitosa, el contenido ha cargado y la página es la correcta
                is_index_content = True

            except (TimeoutException, NoSuchElementException, NoSuchFrameException):
                # No se encontró el iframe o falló el cambio de foco
                is_index_content = False
            except Exception:
                # Captura de errores inesperados
                is_index_content = False
                
            finally:
                # 4. ¡MUY IMPORTANTE! Regresar el foco al contenido principal
                self.website.webbrowser.driver.switch_to.default_content()
            
            return is_index_content
        else:
            self.website.webbrowser.driver.switch_to.default_content()
            return False

    def _focus_contactspage_frame(self) -> bool:
        # Obtenemos el tipo de selector y el valor (el ID o nombre del iframe)
        locator_type, iframe_id = self.TOTAL_CONTACTS_LOCATOR
        
        try:
            # 1. Esperar a que el iframe esté presente en el DOM principal
            # Usamos el localizador completo (By.ID, "maincontent") para la espera.
            WebDriverWait(self.website.webbrowser.driver, 20).until(
                EC.presence_of_element_located(self.TOTAL_CONTACTS_LOCATOR)
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


    def _unfocus_contactspage_frame(self) -> bool:
        try:
            self.website.webbrowser.driver.switch_to.default_content()
        except Exception as e:
            print(f"⚠️ Advertencia: Fallo al intentar salir del foco del iframe. {e}")
            return False
        
        return True # Retorna la instancia de la página para encadenamiento

    def __extract_contact_actions(self, action_row: WebElement) -> List[WebElement]:
        try:
            # Busca todos los enlaces <a> que contienen las acciones (Vista previa, Llamar, etc.)
            action_links = action_row.find_elements(By.TAG_NAME, "a")
            return action_links
        except Exception as e:
            print(f"❌ Error al extraer acciones de la fila: {e}")
            return []

    def __extract_contact_data(self) -> List[str]:
        try:
            header_elements = self.website.webbrowser.driver.find_elements(*self.HEADER_LOCATOR)
            # Limpia los encabezados (quita espacios extra) y asegura que no haya elementos vacíos
            headers = [
                h.text.strip().replace('\n', ' ') 
                for h in header_elements if h.text.strip()
            ]
            print(f"Encabezados encontrados: {headers}")
            return headers
        except Exception as e:
            print(f"❌ Error al obtener los encabezados de la tabla: {e}")
            return []

    # Public methods
    def open_contactstable_page(self, page_index: int) -> bool:
        try:
            self.website.webbrowser.open_tab(self.website.base_url + self.TOTAL_CONTACTS_ROUTE + f"?p={page_index}")
            return True
        except:
            return False
    
    def get_contacts(self, use_javascript: bool = True) -> list:
            if use_javascript:
                query_code = """function findContactTables(){
        // PROTOTYPE FUNCTION
        // Search the frame document element
        const frameDocument = document.getElementById("maincontent");

        // Search the frame document content
        const frameContent = frameDocument.contentDocument; 

        // Obtain the tables allocated in the content
        var tablesContent = frameContent.querySelectorAll("div.col-lg-12 table.layui-table");

        // Extract the data and action tables
        var dataTable = tablesContent[0];
        var actionTable = tablesContent[1];

        return [dataTable, actionTable];
    }

    function findDataHeadersTable(dataTable){
        // Search the header fields
        const headersElements = dataTable.querySelectorAll("thead tr th");

        // Extract the header fields text
        const headers = [];

        for (let headerElement of headersElements){
            // Extract the header text
            let headerText = headerElement.textContent.trim();

            headers.push(headerText);
        }
        
        // Remove the first element (always none)
        headers.shift();
        
        // Insert contact identification data
        headers.unshift("identification");
        
        // Remove the last element (always none)
        headers.pop();
        
        // Return results
        return headers;
    }

    function findDataContactsTable(dataTable){
        // Property definition
        const TSOregex = /namesid=([^&]+)/;

        // Search for contacts
        const contactsRows = dataTable.querySelectorAll("tbody tr");

        // Process every contact (extracting his data)
        const contactsList = [];

        for (let contact of contactsRows){
            // Search the contact data fields
            let contactFields = contact.querySelectorAll("th, td");

            // Process every data field of the contact
            let contactDataFields = [];
            for (let field of contactFields){
                // Verify the field
                if (field.querySelector('input[type="checkbox"]')) {
                    continue; 
                }

                if (field.querySelector('a')){
                    const match = field.querySelector("a").getAttribute("href").match(TSOregex);
                    contactDataFields.unshift(match ? match[1]: null);
                }

                // Save the contact data field
                contactDataFields.push(field.textContent.trim());        
            }
            
            // Remove the last element (always none)
            console.log("Actual contact data fields:", contactDataFields);
            contactDataFields.pop();
            console.log("New contact data fields:", contactDataFields);

            // Save contact
            contactsList.push(contactDataFields);
        }

        // Return results
        return contactsList;
    }

    function findActionHeadersTable(actionTable){
        // Search the headers fields
        const headersElements = actionTable.querySelectorAll("thead tr th");

        // Extract fields text
        const headers = [];

        for (let field of headersElements){
            headers.push(field.textContent.trim());
        }

        return headers;
    }
    function findActionButtonsTable(actionTable){
        // Search contact action buttons rows
        const contactActionButtonsElements = actionTable.querySelectorAll("tbody tr");

        // Extract buttons fields
        const contactsActionButtons = [];

        for (let button of contactActionButtonsElements){
            // Search the link button element
            let contactButtons = button.querySelectorAll("td a");
            
            // Save the extracted buttons
            contactsActionButtons.push(contactButtons);
        }

        // Return results
        return contactsActionButtons;
    }

    // Use
    tables = findContactTables();
    dataTable = tables[0];
    actionTable = tables[1];
    contactsData = findDataContactsTable(dataTable);
    dataHeaders = findDataHeadersTable(dataTable);

    return [contactsData, dataHeaders];
    """
                
                execution_result = self.website.webbrowser.execute_javascript(query_code)

                if execution_result:
                    # Extract contact data
                    contactsData, dataHeaders = execution_result
                    contacts_table = [
                        dict(
                            zip(dataHeaders, contact)
                        ) for contact in contactsData
                    ]
                    contacts_object_list = []

                    # Query the current page number
                    current_page_number = self.identify_current_page_number()
                    
                    # Process the contacts
                    for contact_profile in contacts_table:
                        print("[Total contacts page] Profile contact:")
                        print(json.dumps(contact_profile, indent=4, ensure_ascii=False))

                        # Rename fields
                        if "uid" in contact_profile:
                            contact_profile["UID"] = contact_profile.pop("uid")
                        
                        if "customerName" in contact_profile:
                            contact_profile["NAME"] = contact_profile.pop("customerName")
                        
                        if "customerMobile" in contact_profile:
                            contact_profile["PHONE_NUMBER"] = contact_profile.pop("customerMobile")
                        
                        if "customerGroupType" in contact_profile:
                            contact_profile["GROUP_TYPE"] = contact_profile.pop("customerGroupType")
                        
                        if "productType" in contact_profile:
                            contact_profile["PRODUCT_TYPE"] = contact_profile.pop("productType")

                        if "email" in contact_profile:
                            contact_profile["EMAIL"] = contact_profile.pop("email")

                        if "identification" in contact_profile:
                            contact_profile["TSO"] = contact_profile.pop("identification")
                        
                        if "Tiempo de asignación" in contact_profile:
                            contact_profile["ASSIGNATION_TIME"] = date_to_epoch(contact_profile.pop("Tiempo de asignación"))

                        if "Tarea" in contact_profile:
                            contact_profile["TASK"] = contact_profile.pop("Tarea")
                        
                        if "Asignar ejecutor" in contact_profile:
                            contact_profile["CALL_OPERATOR"] = contact_profile.pop("Asignar ejecutor")
                        
                        if "Carteras de clientes" in contact_profile:
                            contact_profile["CLIENT_BASE"] = contact_profile.pop("Carteras de clientes")

                        # Create a contact profile object
                        contact = Contact(contact_profile)
                        
                        # Incrust the current page number
                        if current_page_number:
                            contact.page_number = current_page_number

                        # Save the contact profile
                        contacts_object_list.append(contact)
                
                    #print(json.dumps(contacts_table, indent=4))
                    return contacts_object_list
                else:
                    return None
            else:
                raise NotImplementedError

    def get_contact(self, contact: object) -> object:
        # Query the current tab
        current_tab = self.website.webbrowser.query_current_tab()
        print("CURRENT TAB:", current_tab)
        print("="*20)
        #time.sleep(5)
        
        # Open admin domain query page
        # Create a temporary contact profile object
        #if "uid" in contact_profile: contact_profile["UID"] = contact_profile.pop("uid")
        
        #temporal_contact = Contact(contact_profile)
        new_tab = self.website.webbrowser.open_tab(contact.url_query, focus_new_tab=True)
        print("New tab:", new_tab)

        if new_tab:
            # Verify the tab disponibility
            #while not self.website.get_page("contactpreview").is_loaded: print("Waiting until the contact profile page is ready...")
            print("Waiting until the contact profile page is ready...")
            time.sleep(1.5)

            print("Page ready")

            # Extract the complete contact data
            contact_profile = self.website.get_page("contactpreview").extract_contact_information()
            #contact_call_details = self.website.get_page("contactpreview").extract_call_details()

            print("Initial contact profile:")
            print("="*20)
            print(json.dumps(contact_profile, indent=4, ensure_ascii=False))

            if "APP" in contact_profile: 
                print("APP present!")
                contact_profile["APPLICATION"] = contact_profile.pop("APP")
            if "Buzón" in contact_profile:
                print("Buzón present!")
                contact_profile["EMAIL"] = contact_profile.pop("Buzón")
            if "Estado del usuario" in contact_profile: contact_profile["USER_STATUS"] = contact_profile.pop("Estado del usuario")
            if "Fecha de registro" in contact_profile: contact_profile["TIME_REGISTRED"] = date_to_epoch(contact_profile.pop("Fecha de registro"), format="%Y/%m/%d")
            if "Género" in contact_profile: contact_profile["GENRE"] = contact_profile.pop("Género")
            if "Plazo opcional" in contact_profile: contact_profile["TERM"] = contact_profile.pop("Plazo opcional")
            if "UID" in contact_profile: contact_profile["UID"] = contact_profile.pop("UID")
            if "Número de teléfono del usuario" in contact_profile: contact_profile["PHONE_NUMBER"] = contact_profile.pop("Número de teléfono del usuario")
            if "Nombre de usuario" in contact_profile: contact_profile["NAME"] = contact_profile.pop("Nombre de usuario")
            if "Crédito disponible" in contact_profile: contact_profile["AMOUNT_AVAILABLE"] = contact_profile.pop("Crédito disponible")
            if "Monto de crédito concedido" in contact_profile: contact_profile["AMOUNT_LIMIT"] = contact_profile.pop("Monto de crédito concedido")
            if "Última fecha de la aprobación de crédito" in contact_profile: contact_profile["LAST_AMOUNT_TIME_APPROBED"] = date_to_epoch(contact_profile.pop("Última fecha de la aprobación de crédito"), format="%Y/%m/%d")
            if "Carteras de clientes" in contact_profile:
                print("Carteras de clientes is present!")
                contact_profile["CLIENT_BASE"] = contact_profile.pop("Carteras de clientes")

            #contact_profile["CALL_OPERATOR"] = contact_call_details["operador"]
            #contact_profile["CALL_UUID"] = contact_call_details["UUID"]

            print("Complete contact profile:")
            print(json.dumps(contact_profile, indent=4, ensure_ascii=False, default=serialize_object))

            # Close the contact profile page
            # Change focus tab
            print("Changing the focus tab to the previous page:", current_tab)
            self.website.webbrowser.switch_focus_tab(current_tab)

            print("Closing contact profile page tab...")
            self.website.webbrowser.close_tab(new_tab)
            print("Tab closed sucessfully")

            # Create a contact profile object
            contact = Contact(contact_profile)
            
            return contact
        else:
            return False
    

    def extract_all_contacts_page(self, use_javascript: bool = True, get_details: bool = False) -> List[Dict[str, Any]]:
        if use_javascript:
            query_code = """function findContactTables(){
    // PROTOTYPE FUNCTION
    // Search the frame document element
    const frameDocument = document.getElementById("maincontent");

    // Search the frame document content
    const frameContent = frameDocument.contentDocument; 

    // Obtain the tables allocated in the content
    var tablesContent = frameContent.querySelectorAll("div.col-lg-12 table.layui-table");

    // Extract the data and action tables
    var dataTable = tablesContent[0];
    var actionTable = tablesContent[1];

    return [dataTable, actionTable];
}

function findDataHeadersTable(dataTable){
    // Search the header fields
    const headersElements = dataTable.querySelectorAll("thead tr th");

    // Extract the header fields text
    const headers = [];

    for (let headerElement of headersElements){
        // Extract the header text
        let headerText = headerElement.textContent.trim();

        headers.push(headerText);
    }
    
    // Remove the first element (always none)
    headers.shift();
    
    // Insert contact identification data
    headers.unshift("identification");
    
    // Remove the last element (always none)
    headers.pop();
    
    // Return results
    return headers;
}

function findDataContactsTable(dataTable){
    // Property definition
    const TSOregex = /namesid=([^&]+)/;

    // Search for contacts
    const contactsRows = dataTable.querySelectorAll("tbody tr");

    // Process every contact (extracting his data)
    const contactsList = [];

    for (let contact of contactsRows){
        // Search the contact data fields
        let contactFields = contact.querySelectorAll("th, td");

        // Process every data field of the contact
        let contactDataFields = [];
        for (let field of contactFields){
            // Verify the field
            if (field.querySelector('input[type="checkbox"]')) {
                continue; 
            }

            if (field.querySelector('a')){
                const match = field.querySelector("a").getAttribute("href").match(TSOregex);
                contactDataFields.unshift(match ? match[1]: null);
            }

            // Save the contact data field
            contactDataFields.push(field.textContent.trim());        
        }
        
        // Remove the last element (always none)
        console.log("Actual contact data fields:", contactDataFields);
        contactDataFields.pop();
        console.log("New contact data fields:", contactDataFields);

        // Save contact
        contactsList.push(contactDataFields);
    }

    // Return results
    return contactsList;
}

function findActionHeadersTable(actionTable){
    // Search the headers fields
    const headersElements = actionTable.querySelectorAll("thead tr th");

    // Extract fields text
    const headers = [];

    for (let field of headersElements){
        headers.push(field.textContent.trim());
    }

    return headers;
}
function findActionButtonsTable(actionTable){
    // Search contact action buttons rows
    const contactActionButtonsElements = actionTable.querySelectorAll("tbody tr");

    // Extract buttons fields
    const contactsActionButtons = [];

    for (let button of contactActionButtonsElements){
        // Search the link button element
        let contactButtons = button.querySelectorAll("td a");
        
        // Save the extracted buttons
        contactsActionButtons.push(contactButtons);
    }

    // Return results
    return contactsActionButtons;
}

// Use
tables = findContactTables();
dataTable = tables[0];
actionTable = tables[1];
contactsData = findDataContactsTable(dataTable);
dataHeaders = findDataHeadersTable(dataTable);

return [contactsData, dataHeaders];
"""
            execution_result = self.website.webbrowser.execute_javascript(query_code)
            
            if execution_result:
                # Extract contact data
                contactsData, dataHeaders = execution_result
                contacts_table = [
                    dict(
                        zip(dataHeaders, contact)
                    ) for contact in contactsData
                ]
                contacts_object_list = []
                
                # Query the current page number
                current_page_number = self.identify_current_page_number()
                
                # Process table
                for contact_profile in contacts_table:     
                    print(contact_profile)                                   
                    if get_details:
                        # Query the current tab
                        current_tab = self.website.webbrowser.query_current_tab()
                        print("CURRENT TAB:", current_tab)
                        print("="*20)
                        #time.sleep(5)
                        
                        # Open admin domain query page
                        # Create a temporary contact profile object
                        if "uid" in contact_profile: contact_profile["UID"] = contact_profile.pop("uid")
                        
                        temporal_contact = Contact(contact_profile)
                        new_tab = self.website.webbrowser.open_tab(temporal_contact.url_query, focus_new_tab=True)
                        print("New tab:", new_tab)

                        if new_tab:
                            # Verify the tab disponibility
                            
                            #while not self.website.get_page("contactpreview").is_loaded: print("Waiting until the contact profile page is ready...")
                            print("Waiting until the contact profile page is ready...")
                            time.sleep(1.5)

                            print("Page ready")

                            # Extract the complete contact data
                            contact_profile = self.website.get_page("contactpreview").extract_contact_information()
                            
                            if "APP" in contact_profile: contact_profile["APPLICATION"] = contact_profile.pop("APP")
                            if "Buzón" in contact_profile: contact_profile["EMAIL"] = contact_profile.pop("Buzón")
                            if "Estado del usuario" in contact_profile: contact_profile["USER_STATUS"] = contact_profile.pop("Estado del usuario")
                            if "Fecha de registro" in contact_profile: contact_profile["TIME_REGISTRED"] = date_to_epoch(contact_profile.pop("Fecha de registro"))
                            if "Género" in contact_profile: contact_profile["GENRE"] = contact_profile.pop("Género")
                            if "Plazo opcional" in contact_profile: contact_profile["TERM"] = contact_profile.pop("Plazo opcional")
                            if "UID" in contact_profile: contact_profile["UID"] = contact_profile.pop("UID")
                            if "Número de teléfono del usuario" in contact_profile: contact_profile["PHONE_NUMBER"] = contact_profile.pop("Número de teléfono del usuario")
                            if "Nombre de usuario" in contact_profile: contact_profile["NAME"] = contact_profile.pop("Nombre de usuario")
                            if "Crédito disponible" in contact_profile: contact_profile["AMOUNT_AVAILABLE"] = contact_profile.pop("Crédito disponible")
                            if "Monto de crédito concedido" in contact_profile: contact_profile["AMOUNT_LIMIT"] = contact_profile.pop("Monto de crédito concedido")
                            
                            print("Complete contact profile:")
                            print(json.dumps(contact_profile, indent=4, ensure_ascii=False))

                            # Close the contact profile page
                            # Change focus tab
                            print("Changing the focus tab to the previous page:", current_tab)
                            self.website.webbrowser.switch_focus_tab(current_tab)

                            print("Closing contact profile page tab...")
                            self.website.webbrowser.close_tab(new_tab)
                            print("Tab closed sucessfully")
                    else:
                        # Rename fields
                        if "uid" in contact_profile:
                            contact_profile["UID"] = contact_profile.pop("uid")
                        
                        if "customerName" in contact_profile:
                            contact_profile["NAME"] = contact_profile.pop("customerName")
                        
                        if "customerMobile" in contact_profile:
                            contact_profile["PHONE_NUMBER"] = contact_profile.pop("customerMobile")
                        
                        if "email" in contact_profile:
                            contact_profile["EMAIL"] = contact_profile.pop("email")

                        if "identification" in contact_profile:
                            contact_profile["TSO"] = contact_profile.pop("identification")
                        
                        if "Tiempo de asignación" in contact_profile:
                            contact_profile["ASSIGNATION_TIME"] = date_to_epoch(contact_profile.pop("Tiempo de asignación"))


                    # Create a contact profile object
                    contact = Contact(contact_profile)
                    
                    # Incrust the current page number
                    if current_page_number:
                        contact.page_number = current_page_number

                    # Save the contact profile
                    contacts_object_list.append(contact)
                
                #print(json.dumps(contacts_table, indent=4))
                return contacts_object_list
        else:
            pass
        
        contact_objects_list: List[Contact] = []
        self._focus_contactspage_frame()
        try:
            # 2. Esperar a que al menos una fila de datos esté presente
            WebDriverWait(self.website.webbrowser.driver, 30).until(
                EC.presence_of_element_located(self.DATA_ROWS_LOCATOR)
            )
            
            # 3. Obtener los WebElements de ambas subtablas
            data_rows: List[WebElement] = self.website.webbrowser.driver.find_elements(*self.DATA_ROWS_LOCATOR)
            action_rows: List[WebElement] = self.website.webbrowser.driver.find_elements(*self.ACTION_ROWS_LOCATOR)
            
            print(f"Filas de datos encontradas: {len(data_rows)}. Filas de acciones: {len(action_rows)}.")
            print("Data rows:")
            print(data_rows)
            print("Action rows:")
            print(action_rows)

            if len(data_rows) != len(action_rows):
                print("❌ Error: El número de filas de datos y acciones no coincide. Revisar la estructura HTML.")
                return False
                
            # 4. Obtener los encabezados (una sola vez)
            headers = self.__extract_contact_data()

            # 5. Iterar sobre las filas de forma relacional usando zip()
            for index, (data_row, action_row) in enumerate(zip(data_rows, action_rows)):
                try:
                    # Construir el objeto Contact, pasándole las dos filas correspondientes
                    new_contact = Contact(
                        data_row=data_row, 
                        action_row=action_row, 
                        headers=headers, 
                        row_index=index
                    )
                    contact_objects_list.append(new_contact)
                except Exception as e:
                    print(f"❌ Error al construir el objeto Contact (Fila {index}): {e}")
                    continue
            
            print(f"✅ Extracción completada. {len(contact_objects_list)} objetos Contacto/Tarea procesados.")
            return contact_objects_list
            
        except TimeoutException:
            print("❌ Error: Las filas de contacto no aparecieron dentro del tiempo límite.")
            return False
        except Exception as Error:
            print(f"❌ Error general durante la extracción: {Error}")
            return False
        
        finally:
            # 6. Regresar el foco al contenido principal
            pass
            #self._unfocus_contactspage_frame()

    def extract_all_contacts_pages(self, start_page: int, end_page: int) -> list:
        # Verify start/end page
        print("EXTRACTING CONTACTS FROM THE PAGE:", start_page, "TO THE PAGE:", end_page)
        
        if start_page > end_page:
            raise ValueError("The specified start page is greater than the end page")

        # Search the start page
        search_result = self.search_page(start_page)

        if search_result: pass
        else: raise ValueError("We cant find the specified start page")

        # Start extraction process
        page_index = start_page
        page_table = {}

        for index in list(range(page_index, end_page)):
            # Extract contacts list
            page_table[index] = []       
            all_contacts_page = self.extract_all_contacts_page()

            # Verify extraction result
            if all_contacts_page: pass
            else: raise ValueError("Error extracting contacts on the page:", index)

            # Append new contacts page
            page_table[index] = all_contacts_page

            # Go to the previous/next page
            if start_page < end_page:
                change_result = self.go_to_next_page()

            # Verify movement result
            if change_result: pass
            else: raise ValueError("Error changing the page:", index)

        return page_table

    def is_current_page(self, use_javascript: bool = True) -> int:
        if use_javascript:
            query_code = """function isCurrentPage(){
    // Search the frame document element
    let frameDocumentElement = document.getElementById("maincontent");

    // Verify the search result
    if (frameDocumentElement === null){
        return null;
    }

    // Verify the internal content URL
    if (frameDocumentElement.contentDocument.URL.includes("/apps/callout/names/index.html")){
        return true;
    } else {
        return false;
    }
}

// Use
return isCurrentPage();"""

            return self.website.webbrowser.execute_javascript(query_code)
        else:
            pass

        print("CURRENT MENU PAGE:", self._identify_call_menu())
        print("CURRENT TOTALCONTACTS FRAME:", self._identify_totalcontacts_page())

        if self._identify_call_menu() and self._identify_totalcontacts_page():
            return True
        else:
            return False
    
    def identify_current_page_number(self, use_javascript: bool = True) -> int | bool:
        """
        Devuelve el número de página actual visible en el componente LayUI.
        Prueba CSS y usa un fallback de JavaScript para mayor robustez.
        """
        #if not self.is_current_page():
        #    print("❌ Error: La página actual no es la esperada.")
        #    return None
            
        # 1. Enfocar el iframe
        start_time = time.time()
        if use_javascript:
            query_sentence = """// Search the frame document element
const frameDocument = document.getElementById("maincontent");

// Verify the search result
if (frameDocument === null){
    return null;
}

// Verify the frame document content
if (frameDocument.contentDocument === null){
    return null;
}

// Search the actual page button
var actualPageButton = frameDocument.contentDocument.querySelector("span.layui-laypage-curr em");

// Verify the search result
if (actualPageButton === null){
    return null;
}

// Extract the actual page button text
var actualPageButtonText = actualPageButton.nextElementSibling.textContent;

return actualPageButtonText;"""
            
            execution_result = self.website.webbrowser.execute_javascript(query_sentence)

            print("RESULTADO DE CONSULTA:", execution_result, type(execution_result))
            finish_time = time.time()
            print("Total time:", finish_time - start_time)

            try:
                return int(execution_result)
            except:
                return False
        else:
            pass


        if not self._focus_contactspage_frame():
            return None
            
        page_num = None

        try:
            # 🎯 Intento 1: CSS Selector directo (más rápido si funciona)
            element = WebDriverWait(self.website.webbrowser.driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "span.layui-laypage-curr em:nth-of-type(2)"))
            )
            page_text = element.text.strip()
            if page_text and page_text.isdigit():
                page_num = int(page_text)
                print(f"📄 Página actual detectada (CSS): {page_num}")
                finish_time = time.time()
                print("Total time:", finish_time - start_time)
                return page_num
        except (TimeoutException, NoSuchElementException):
            pass # Si falla el CSS, intentamos con JS

        try:
            # 🎯 Intento 2: Fallback de JavaScript (más robusto contra nodos vacíos)
            script = """
                var el = document.querySelector('span.layui-laypage-curr');
                if(!el) return '';
                // Buscamos el segundo <em>, que generalmente contiene el número.
                var ems = el.getElementsByTagName('em');
                if(ems.length >= 2) return ems[1].innerText || ems[1].textContent || '';
                return '';
            """
            page_text = self.website.webbrowser.driver.execute_script(script)
            page_text = (page_text or "").strip()
            
            if page_text.isdigit():
                page_num = int(page_text)
                print(f"📄 Página actual detectada (JS): {page_num}")
            else:
                print(f"⚠️ Página actual no numérica (JS): '{page_text}'")
        except Exception as e:
            print(f"⚠️ No se pudo determinar la página actual: {e}")
        
        finally:
            # 2. Regresar el foco al contenido principal (MUY IMPORTANTE)
            self._unfocus_contactspage_frame()
            
        return page_num
    
    def go_to_previous_page(self, use_javascript: bool = True) -> bool:
        if use_javascript:
            query_code = """// Search the frame document element
const frameDocument = document.getElementById("maincontent");
console.info("Frame document:", frameDocument);

// Verify the search result
if (frameDocument === null){
    console.error("Error. The frame can not be founded");
    return null;
}

// Verify if the frame has been loaded sucessfully
if (frameDocument.contentDocument === null){
    console.error("Error. The frame has no content");
    return null;
}

// Search the previous page button
var buttonPrevPage = frameDocument.contentDocument.querySelector("a.layui-laypage-prev");

console.info("Button previous page:", buttonPrevPage);

// Verify the search result
if (buttonPrevPage === null){
    console.error("Error. The button can not be founded");
    return null;
}

// Verify if the button is enabled or disabled
if (buttonPrevPage.classList.contains("layui-disabled")){
    console.error("Error. The button is disabled");
    return false;
}

// Make a click on the previous page button
try{
    buttonPrevPage.click();
    console.log("The button has been clicked sucessfully");
    return true;
} catch (Exception){
    console.error("There was an error on clicking the button", Exception);
    return false;
}"""

            execution_result = self.website.webbrowser.execute_javascript(query_code)
            print("EXECUTION RESULT PREVIOUS PAGE:", execution_result)
            return execution_result
        else:
            pass

        success = False
        self._unfocus_contactspage_frame()

        try:
            # 1. Enfocar el iframe para interactuar con los elementos
            self._focus_contactspage_frame()

            # Guardar el estado actual antes de la acción
            #page_before = self.identify_current_page_number()
            #first_contact_before = None
            #try:
            #    first_contact_before = self.website.webbrowser.driver.find_element(*self.FIRST_CONTACT_LINK_LOCATOR).get_attribute("data-href")
            #except Exception:
            #    pass

            #print(f"Going to previous page... (Página actual: {page_before})")

            # 2. Localizar y hacer clic en el botón 'Anterior'
            previous_button = self.website.webbrowser.driver.find_element(*self.PREVIOUS_PAGE_LOCATOR)
            
            class_attribute = previous_button.get_attribute("class")
            if "layui-disabled" in class_attribute:
                print("BOTON DE PAGINA PREVIA DESHABILITADO")
                return None
        
            print("🖱️ Clic en 'Anterior'...")
            previous_button.click()

            # 3. Esperar a que el contenido de la página cambie
            #for i in range(3): # Reintentar hasta 3 veces
            #    time.sleep(1) # Pequeña espera entre chequeos

                # Detección por cambio en el primer contacto
            #    try:
            #        first_contact_after = self.website.webbrowser.driver.find_element(*self.FIRST_CONTACT_LINK_LOCATOR).get_attribute("data-href")
            #        if first_contact_before and first_contact_after and first_contact_after != first_contact_before:
            ##            print(f"✅ Cambio de página detectado por primer contacto (Intento {i+1}).")
            # #           success = True
            #            break
            #    except Exception:
            #        pass

                # Fallback: detectar el cambio por número de página
               # page_after = self.identify_current_page_number()
                # Verifica si el número de página ha disminuido
            #    if page_before is not None and page_after is not None and page_after < page_before:
            #        print(f"✅ Cambio de página detectado por número (Intento {i+1}, antes={page_before} ahora={page_after}).")
            #        success = True
            #        break

            #if not success:
             #    print("⚠️ No se detectó cambio de página tras varios intentos.")
            
            return True

        except NoSuchElementException:
            print("💥 Error: No se encontró el botón de paginación 'Anterior'.")
            return False
        except Exception as e:
            print(f"💥 Error al intentar retroceder página: {e}")
            return False
        finally:
            # 4. Regresar el foco al contenido principal
            self._unfocus_contactspage_frame()

        return success
    
    def go_to_next_page(self, page_before: int | None = None, use_javascript: bool = True) -> bool:
        """
        Avanza a la siguiente página de contactos utilizando el botón de paginación.
        
        Args:
            page_before (int | None): Número de página anterior, si se conoce, para validar el cambio.

        Returns:
            bool: True si el cambio de página fue exitoso o se detectó, False en caso contrario.
        """
        if use_javascript:
            query_code = """// Search the frame document element
const frameDocument = document.getElementById("maincontent");
console.info("Frame element:", frameDocument);

// Verify the search result
if (frameDocument === null){
    console.error("Error. The frame element was not found");
    return null;
}

// Verify if the frame has been loaded sucessfully
if (frameDocument.contentDocument === null){
    console.error("Error. The frame has no content");
    return null;
}

// Search the previous page button
var buttonNextPage = frameDocument.contentDocument.querySelector("a.layui-laypage-next");
console.info("Next page button:", buttonNextPage);

// Verify the search result
if (buttonNextPage === null){
    console.error("Error. The next page button was not found");
    return null;
}

// Verify if the button is enabled or disabled
if (buttonNextPage.classList.contains("layui-disabled")){
    console.error("Error. The next page button is disabled");
    return false;
}

// Make a click on the previous page button
try{
    buttonNextPage.click();
    console.info("Next page button clicked sucessfully");
    return true;
} catch (Exception){
    console.error("Error. There was an error on clicking the next page button");
    return false;
}
"""
            execution_result = self.website.webbrowser.execute_javascript(query_code)
            print("EXECUTION NEXT PAGE RESULT:", execution_result)
            return execution_result
        else:
            pass

        success = False
        
        try:
            # 1. Enfocar el iframe
            start_time = int(time.time())
            timeout = 10
            while int(time.time()) - start_time < timeout:
                if self._focus_contactspage_frame():
                    break
                
                time.sleep(1)
            
            # Obtener el atributo data-href del primer contacto antes de hacer clic (para validación)
            first_contact_before = None
            try:
                first_contact_before = self.website.webbrowser.driver.find_element(*self.FIRST_CONTACT_LINK_LOCATOR).get_attribute("data-href")
            except Exception:
                # No es un error crítico si no se encuentra, solo un método de validación menos
                pass

            # 2. Hacer clic en el botón 'Siguiente'
            next_page_button = WebDriverWait(self.website.webbrowser.driver, 20).until(
                EC.element_to_be_clickable(self.NEXT_PAGE_LOCATOR)
            )
            
            class_attribute = next_page_button.get_attribute("class")
            
            # Verify button status
            if "layui-disabled" in class_attribute:
                print("BOTON SIGUIENTE DESHABILITADO!")
                return None
            
            next_page_button.click()
            print("🖱️ Clic en 'Siguiente'...")
            
            # 3. Esperar y validar el cambio de página
            # Se hacen varios intentos para dar tiempo a la recarga del contenido AJAX
            #for i in range(5): 
            #    time.sleep(1) # Pequeña espera entre reintentos
                
                # Intentar detectar el cambio por el link del primer contacto
            #    try:
            #        first_contact_after = self.website.webbrowser.driver.find_element(*self.FIRST_CONTACT_LINK_LOCATOR).get_attribute("data-href")
            #        if first_contact_before and first_contact_after and first_contact_after != first_contact_before:
            #            print(f"✅ Cambio de página detectado por primer contacto (Intento {i+1}).")
            #            success = True
            #            break
            #    except Exception:
            #        pass
                
                # Fallback: detectar el cambio por número de página
                #page_after = self.identify_current_page_number()
                # Si identify_current_page_number devuelve None, el _unfocus_contactspage_frame() en identify_current_page_number
                # causa que el driver esté en el contenido principal. Necesitamos re-enfocar el iframe.
                #self._focus_contactspage_frame() 

                #if page_before is not None and page_after is not None and page_after > page_before:
                #    print(f"✅ Cambio de página detectado por número (Intento {i+1}, antes={page_before} ahora={page_after}).")
                #    success = True
                #    break
            
            #if not success:
            #     print("⚠️ No se detectó cambio de página tras varios intentos.")

            return True


        except NoSuchElementException:
            print("💥 Error: No se encontró el botón de paginación 'Siguiente'.")
            return False
        except Exception as e:
            print(f"💥 Error al intentar avanzar página: {e}")
            return False
        finally:
            # 4. Regresar el foco al contenido principal
            self._unfocus_contactspage_frame()
            
        return success

    def search_page(self, page_number: int) -> bool:
        # Identify the actual page (start page)
        actual_page = int(self.identify_current_page_number())

        if actual_page: pass
        else:
            print("NO PUDIMOS DETECTAR LA PAGINA ACTUAL")
            return None
    
        if actual_page == page_number: return True
        
        for page in list(range(0, page_number)):
            # Query for the actual page
            if page_number < page:
                # Go back
                load_previous = self.go_to_previous_page()
                actual_page -= 1
                if load_previous: pass
                else:
                    print("ERROR AL CARGAR LA PAGINA ANTERIOR")
                    return None
                
            elif page_number > page:
                load_next = self.go_to_next_page()
                actual_page += 1
                if load_next: pass
                else:
                    print("ERROR AL CARGAR LA PAGINA SIGUIENTE")
                    return None
                
            # Verify the actual page
            if actual_page == page_number:
                print("PAGINA BUSCADA ENCONTRADA!")
                return True
            
            if actual_page == 1:
                print("DETENIENDO PROCESO. NO LOCALIZAMOS LA PAGINA Y NO HAY MENOS")
                return None
                
        
        print("PAGINA NO ENCONTRADA")
        return None

    def open_contact(self, contact: Contact, use_javascript: bool = True) -> object:
        if use_javascript:
            query_code = """// Functions definition
function findContactTables(){
    // PROTOTYPE FUNCTION
    // Search the frame document element
    const frameDocument = document.getElementById("maincontent");

    // Search the frame document content
    const frameContent = frameDocument.contentDocument; 

    // Obtain the tables allocated in the content
    var tablesContent = frameContent.querySelectorAll("div.col-lg-12 table.layui-table");

    // Extract the data and action tables
    var dataTable = tablesContent[0];
    var actionTable = tablesContent[1];

    return [dataTable, actionTable];
}

function findDataContactsTable(dataTable){
    // Property definition
    const TSOregex = /namesid=([^&]+)/;

    // Search for contacts
    const contactsRows = dataTable.querySelectorAll("tbody tr");

    // Process every contact (extracting his data)
    const contactsList = [];

    for (let contact of contactsRows){
        // Search the contact data fields
        let contactFields = contact.querySelectorAll("th, td");

        // Process every data field of the contact
        let contactDataFields = [];
        for (let field of contactFields){
            // Verify the field
            if (field.querySelector('input[type="checkbox"]')) {
                continue; 
            }

            if (field.querySelector('a')){
                const match = field.querySelector("a").getAttribute("href").match(TSOregex);
                contactDataFields.unshift(match ? match[1]: null);
            }

            // Save the contact data field
            contactDataFields.push(field.textContent.trim());        
        }
        
        // Remove the last element (always none)
        console.log("Actual contact data fields:", contactDataFields);
        contactDataFields.pop();
        console.log("New contact data fields:", contactDataFields);

        // Save contact
        contactsList.push(contactDataFields);
    }

    // Return results
    return contactsList;
}

function findActionButtonsTable(actionTable){
    // Search contact action buttons rows
    const contactActionButtonsElements = actionTable.querySelectorAll("tbody tr");

    // Extract buttons fields
    const contactsActionButtons = [];

    for (let button of contactActionButtonsElements){
        // Search the link button element
        let contactButtons = button.querySelectorAll("td a");
        
        // Save the extracted buttons
        contactsActionButtons.push(contactButtons);
    }

    // Return results
    return contactsActionButtons;
}

// Use
const tables = findContactTables();
const dataTable = tables[0];
const actionTable = tables[1];
const contactsData = findDataContactsTable(dataTable);
const buttonsTable = findActionButtonsTable(actionTable);

// Data processing
const CONTACT_IDENTIFICATION = arguments[0];
let CONTACT_PREVIEW_BUTTON = undefined;
let index_list = Array.from({ length: contactsData.length }, (v, i) => i);

for (let index of index_list){
    // Get indexed data and action buttons
    let contactRow = contactsData[index];
    let buttonsRow = buttonsTable[index];

    // Get preview button
    let previewButton = buttonsRow[0];

    // Verify the contact identification
    if (previewButton.getAttribute("data-href").includes(CONTACT_IDENTIFICATION)){
        CONTACT_PREVIEW_BUTTON = previewButton;
        break
    }
}

// Verify search results
if (CONTACT_PREVIEW_BUTTON === null){
    console.log("Button not finded"); //return null;
} else{
    // Execute click interaction
    try{
        CONTACT_PREVIEW_BUTTON.click();
        console.log("Button sucessfully pressed");//return true;
    } catch(error){
        console.log("There was an error on pressing the button");//return false;
    }
}"""
            execution_result = self.website.webbrowser.execute_javascript(query_code, contact.tso_id)
            return execution_result
        else:
            raise NotImplementedError
        
        
    def query_last_menu_page(self, use_javascript: bool = True) -> str | bool:
        if use_javascript:
            query_code = """function getLastPageNumber(){
        // Search the frame document element
        let frameDocumentElement = document.getElementById("maincontent");

        // Verify the search result
        if (frameDocumentElement === null){
            return null;
        }

        // Search the last page button
        let lastPageButton = frameDocumentElement.contentDocument.querySelector("a.layui-laypage-last");

        // Verify the search result
        if (lastPageButton === null){
            return null;
        }

        // Return the page number
        return lastPageButton.textContent.trim();
    }

    // Use
    return getLastPageNumber();
    """

            execution_result = self.website.webbrowser.execute_javascript(query_code)

            try:
                execution_result = int(execution_result)
                return execution_result
            except:
                return False
        else:
            raise NotImplementedError