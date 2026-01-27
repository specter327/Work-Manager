# Library import
# Private libraries
from .ModuleCRM.website.telesales.pages.properties import serialize_object
from .ModuleCRM.data.classes.calllogdatabase import CallLogDataBase
from .WebController.src.data.classes.webbrowser import WebBrowser
from .WebController.src.data.classes.website import WebSite
from .WebController.src.data.classes.webfolder import WebFolder
from .WebController.src.data.classes.webpage import WebPage
from .WebController.src.data.controllers.chrome import Controller
from .ModuleCRM.website.admin.pages.login import LoginPage
from .ModuleCRM.website.telesales.pages.totalcontacts import TotalContactsPage
from .ModuleCRM.website.telesales.pages.homeuser import HomeUserPage
from .ModuleCRM.website.telesales.pages.userstatistics import UserStatisticsPage
from .ModuleCRM.website.telesales.pages.totalcontacts import TotalContactsPage
from .ModuleCRM.website.telesales.pages.bussinessummary import BussinesSummaryPage
from .ModuleCRM.website.telesales.pages.contactprofile import ContactProfilePage
from ...core.interfaces import ProcessInterface

# External libraries
import time
import pandas
import os
import json
import tkinter
import random
import threading
from tkinter import filedialog, messagebox
import logging

# CRM Configuration
# Create a web browser instance
webbrowserGUI = WebBrowser(controller=Controller)

# Create a web site instance
admin_website = WebSite(domain="admin.oa.wowcredito.com", webbrowser=webbrowserGUI, protocol="https", port=443)

# Create a web folder
passport_folder = WebFolder(name="passport", website=webbrowserGUI, folder_parent=None)

# Create a web page
login_page = WebPage(
    name="login", 
    website=admin_website, 
    folder_parent=passport_folder,
    parameters={
        "client_id": "2504242246490008519680",
        "redirect_uri": "https://telesales.oa.wowcredito.com/apps/callcenter/agent/callback/9c25965a32574be3bfa69e859f08bf5b.html",
        "response_type": "code",
        "scope": "simple_user",
        "state": "123",
        "type": "oauth2"
    },
    page_class=LoginPage
)

# Register login page
admin_website.register_page(name="login", page=login_page)

telesales_website = WebSite(
    domain="telesales.oa.wowcredito.com",
    webbrowser=webbrowserGUI,
    protocol="https",
    port=443,
    session_data=None
)

# Create webpages objects
homeuser_page = WebPage(
    name="home",
    website=telesales_website,
    folder_parent=None,
    page_class=HomeUserPage
)

apps_folder = WebFolder(
    name="apps",
    website=telesales_website,
    folder_parent=None
)

callcenter_folder = WebFolder(
    name="callcenter",
    website=telesales_website,
    folder_parent=apps_folder
)

callout_folder = WebFolder(
    name="callout",
    website=telesales_website,
    folder_parent=apps_folder
)

names_folder = WebFolder(
    name="names",
    website=telesales_website,
    folder_parent=callout_folder
)

service_folder = WebFolder(
    name="service",
    website=telesales_website,
    folder_parent=callcenter_folder
)

owner_folder = WebFolder(
    name="owner",
    website=telesales_website,
    folder_parent=service_folder
)


userstatistics_page = WebPage(
    name="userstatistics",
    website=telesales_website,
    folder_parent=None,
    page_class=UserStatisticsPage
)

totalcontacts_page = WebPage(
    name="totalcontacts",
    website=telesales_website,
    folder_parent=names_folder,
    page_class=TotalContactsPage
)

bussinessummary_page = WebPage(
    name="bussinessummary",
    website=telesales_website,
    folder_parent=names_folder,
    page_class=BussinesSummaryPage
)

contactpreview_page = WebPage(
    name="contactpreview",
    website=telesales_website,
    folder_parent=names_folder,
    page_class=ContactProfilePage
)

# Register folders
telesales_website.register_folder(name="apps", folder=apps_folder)
telesales_website.register_folder(name="callout", folder=callout_folder)
telesales_website.register_folder(name="names", folder=callout_folder)

# Register pages
# - Home user
telesales_website.register_page(name="homeuser", page=homeuser_page)
# - User statistics
telesales_website.register_page(name="userstatistics", page=userstatistics_page)
# - Total contacts
telesales_website.register_page(name="totalcontacts", page=totalcontacts_page)
# - Bussiness summary
telesales_website.register_page(name="bussinessummary", page=bussinessummary_page)
# - Contact preview
telesales_website.register_page(name="contactpreview", page=contactpreview_page)


# Classes definition
class CallLogger:
    def __init__(self, website: object, call_log_database: object) -> None:
        # Property definition
        self.is_enabled: bool = False
        self.monitor_thread: object = None
        self.website = website
        self.call_log_database = call_log_database
        self.call_flag: bool = False
    
    # Private methods
    def _get_contact_uid(self, use_javascript: bool = True) -> dict | None:
        if use_javascript:
            query_code = """// Functions definition
function getContactProfile(frame){
    // search the titles elements
    let titleElements = frame.contentDocument.querySelectorAll("div.el-form-item__label");

    // Verify the search result
    if (titleElements.length === 0){
        return null;
    }

    // Search the value elements
    let valueElements = frame.contentDocument.querySelectorAll("div.el-form-item__content");

    // Verify the search result
    if (valueElements.length === 0){
        return null;
    }

    // Process the data
    let indexs = Array.from({ length: titleElements.length }, (v, i) => i);
    let contactProfile = new Map();

    for (let index of indexs){
        // Set title and value
        contactProfile.set(titleElements[index].textContent.trim().split(':')[0], valueElements[index].textContent.trim());
    }

    // Return contact profile
    return contactProfile;
}

function captureContactUID(){
    // Search the frame document element
    let frameDocumentElement = document.getElementById("outboundCallConsole");

    // Verify the search result
    if (frameDocumentElement === null){ return null; }

    // Search the contact document element
    let contactDocumentElement = frameDocumentElement.contentDocument.getElementById("contactsConsole");

    // Verify the search result
    if (contactDocumentElement === null){ return null; }

    // Get the contact data fields
    let contactProfile = getContactProfile(contactDocumentElement);

    // Verify the result
    if (!contactProfile){ return null;}

    // Return results
    return contactProfile.get("UID");
}

// Insert the web function hook (to capture the call event)
console.log = function(...args) {
    // Ejecutar la función original para que la consola siga funcionando
    window.crmCallTracker.originalConsoleLog.apply(console, args); 

    // Convertir los argumentos a una sola cadena para buscar el patrón
    const logMessage = args.map(arg => String(arg)).join(' ');

    // El patrón a buscar: RTPSession , new ringing:remote
    if (logMessage.includes("RTPSession , new ringing:remote")) {
        // Evento de llamada detectado
        window.crmCallTracker.callDetected = true;
        
        // Extraer el UID del contacto en ese momento
        window.crmCallTracker.contactUID = captureContactUID();
        
        // Esto es solo un log de nuestro script, no del CRM
        window.crmCallTracker.originalConsoleLog(
            "%c[CRM Tracker]%c Llamada detectada para UID:", 
            "background: #1e90ff; color: white; padding: 2px 5px; border-radius: 3px;",
            "color: #1e90ff; font-weight: bold;",
            window.crmCallTracker.contactUID
        );
    }
};

// Use
return captureContactUID();"""

            return self.website.webbrowser.execute_javascript(query_code)
        else:
            raise NotImplementedError
    
    def _inject_javascript_logger(self) -> bool:
        javascript_code = """// Functions definition
// Support function to get contact profile data
function getContactProfile(frame) {
    try {
        const frameDocument = frame.contentDocument;
        if (!frameDocument) { 
            console.error("[getContactProfile] No se pudo acceder a contentDocument del iframe.");
            return null;
        }

        const titleElements = frameDocument.querySelectorAll("div.el-form-item__label");
        const valueElements = frameDocument.querySelectorAll("div.el-form-item__content");

        if (titleElements.length === 0 || valueElements.length === 0 || titleElements.length !== valueElements.length) {
            return null;
        }

        let contactProfile = new Map();

        // Procesa los datos
        titleElements.forEach((titleElement, index) => {
            // Limpiar la clave (e.g., "UID:" -> "UID")
            const title = titleElement.textContent.trim().split(':')[0];
            // Limpiar el valor
            const value = valueElements[index].textContent.trim();
            contactProfile.set(title, value);
        });

        return contactProfile;
    } catch (error) {
        console.error("[getContactProfile] Fallo al procesar el iframe:", error);
        return null;
    }
}

// Main function to capture contact UID
function captureContactUID() {
    try {
        // Buscar el iframe principal
        const outboundFrame = document.getElementById("outboundCallConsole");
        if (!outboundFrame || !outboundFrame.contentDocument) { return null; }

        // Buscar el iframe anidado de contacto
        const contactFrame = outboundFrame.contentDocument.getElementById("contactsConsole");
        if (!contactFrame || !contactFrame.contentDocument) { return null; }

        // Obtener el perfil completo y luego el UID
        const contactProfile = getContactProfile(contactFrame);

        return contactProfile ? contactProfile.get("UID") : null;
    } catch (error) {
        console.error("[captureContactUID] Fallo en la navegación de iframes:", error);
        return null;
    }
}

// Support function to create the log
function createCallLog(contactUID) {
    return {
        contactUID: contactUID,
        timestamp: new Date().toISOString()
    };
}

// Main function to log call event
function logCall() {
    console.log("%c[Logger] 📞 Iniciando extracción de datos...", "color: #ff9900");
    
    // 1. Obtener el UID del contacto
    const contactUID = captureContactUID();

    // Verificar el resultado y salir si no hay UID
    if (!contactUID) { 
        console.warn("[Logger] ⚠️ No se pudo obtener el UID del contacto. No se registrará el log.");
        return null; 
    }

    // 2. Crear el objeto de log
    const callLog = createCallLog(contactUID);
    
    // 3. Almacenar el log en el contexto global
    globalContext[callLoggerIndex].push(callLog);

    console.log(`%c[Logger] ✅ Log de llamada creado y almacenado (UID: ${contactUID})`, "color: #00cc66", callLog);
    return callLog;
}


// Creation of global storage for logs
const globalContext = window.top;
const callLoggerIndex = "crmCallLoger"; // Clave donde se almacenarán los logs

// Inicializar el array de logs en el contexto global si no existe
if (!globalContext[callLoggerIndex]) {
    globalContext[callLoggerIndex] = [];
    console.log(`[Logger] Inicializado el array de logs en window.top['${callLoggerIndex}'].`);
}

// Intercept wrapper function
function interceptClick(selector) {
    console.log(`[Interceptador] Buscando elemento con selector: ${selector}`);

    try {
        const targetElement = document.querySelector(selector);

        if (!targetElement) {
            console.error(`[Interceptador] Error: No se encontró ningún elemento con el selector '${selector}'.`);
            return false;
        }

        // 2. Guardar la función de click original (si existe en la propiedad onclick)
        const originalClickHandler = targetElement.onclick;

        // 3. Crear nuestra función de manejo del evento (el Wrapper)
        targetElement.onclick = function(event) {
            
            // --- CÓDIGO DE INTERCEPCIÓN (Integrando logCall()) ---
            console.log(`%c[Interceptador] CLICK DETECTADO en ${selector}`, "background: #1084d0; color: white; padding: 2px 5px; border-radius: 3px;");
            
            // **Ejecución de la lógica de logueo**
            logCall();
            
            // -------------------------------------------------------------------

            // 4. Ejecutar la función original guardada, si es que existía en 'onclick'.
            if (originalClickHandler && typeof originalClickHandler === 'function') {
                originalClickHandler.call(this, event);
                console.log("[Interceptador] Función 'onclick' original ejecutada (Si existía).");
            } 
            
            // El manejador real de la aplicación (vía addEventListener) se ejecuta
            // después de que este wrapper termina, garantizando la llamada.
        };

        console.log(`[Interceptador] Hook aplicado exitosamente al elemento: ${selector}.`);
        return true;

    } catch (error) {
        console.error(`[Interceptador] Fallo durante la aplicación del hook: ${error.message}`);
        return false;
    }
}


// Execution
// Selector del botón de llamada
const CALL_BUTTON_SELECTOR = 'div.soft-function.outboundcall'; 
const PREVIEW_BUTTON_SELECTOR = 'div.soft-function.preview';

// Llama a la función de intercepción para iniciar todo
let callButtonIntercept = interceptClick(CALL_BUTTON_SELECTOR);
let previewButtonIntercept = interceptClick(PREVIEW_BUTTON_SELECTOR);

return [callButtonIntercept, previewButtonIntercept];"""

        return self.website.webbrowser.execute_javascript(javascript_code)


    def _set_active(self) -> bool:
        self.is_enabled = True
        return True
    
    def _set_inactive(self) -> bool:
        self.is_enabled = False
        return True
    
    def _set_call_flag(self) -> bool:
        self.call_flag = True
        return True
    
    def _unset_call_flag(self) -> bool:
        self.call_flag = False
        return True
    
    def _query_call_logs(self) -> list:
        # Query the call logs from the global context
        query_code = """// Define la clave de la variable global que contiene el array de logs
const CALL_LOG_KEY = "crmCallLoger";

try {
    // Accede a la variable en el contexto superior (donde se almacenó)
    const logs = window.top[CALL_LOG_KEY];

    // Verifica que sea un array y devuélvelo como una cadena JSON
    if (Array.isArray(logs)) {
        // Devuelve la cadena JSON para que Python la pueda deserializar fácilmente
        return JSON.stringify(logs);
    } else {
        // En caso de que la variable no esté inicializada o no sea un array
        const errorMsg = `La variable '${CALL_LOG_KEY}' no es un array o no se encontró en window.top.`;
        console.error(errorMsg);
        // Devuelve un error serializado en JSON
        return JSON.stringify({ error: errorMsg, logs_found: logs });
    }
} catch (e) {
    // Manejo de errores generales durante la ejecución
    console.error("Error al intentar serializar los logs de llamada:", e);
    return JSON.stringify({ error: "Fallo de ejecución de script JS", details: e.message });
}"""
        query_result = self.website.webbrowser.execute_javascript(query_code)
        
        if query_result:
            try:
                call_logs = json.loads(query_result)
                return call_logs
            except Exception as Error:
                print("Error en la decodificación;", Error)
                return False
        else:
            return False
    
    def _monitor_process(self) -> None:
        contact_page = self.website.get_page("contactpreview")
        
        # Inject the JavaScript logger
        injection_result = self._inject_javascript_logger()
        
        if injection_result:
            print("JavaScript logger injected successfully:", injection_result)
        else:
            print("There was an error injecting the JavaScript logger.")
            raise Exception("JavaScript injection failed.")
        
        while True:
            # Verify the current monitor status
            if not self.is_active(): 
                print("Stopping process. The monitor is inactive")
                break
             
            # Verify if is the current page
            if not contact_page.is_current_page():
                print("Skipping process. Is not the current page")
                continue # Is not the current page

            call_logs = self._query_call_logs()
            print("Type:", type(call_logs), "Length:", len(call_logs), "Call log:", call_logs)
            #print("Query call logs:", self._query_call_logs())
            continue
        
            # Verify if the user agent is on wait
            current_agent_status = contact_page.query_current_agent_status().upper()
            print("CURRENT STATUS:", current_agent_status)
            time.sleep(1)

            if "NÚMERO" in current_agent_status and "DURACIÓN" in current_agent_status and "WAIT" not in current_agent_status:
                # Call detected. Set flag
                self._set_call_flag()
                print("NEW CALL DETECTED")
                #time.sleep(300)
            else:
                # Call not detected. Remove flag
                #self._unset_call_flag()
                pass
            
            # Log the current call
            if self.call_flag:
                # Get the current UID
                current_contact_uid = self._get_contact_uid()

                # Log new call
                print("CONTACT UID:", current_contact_uid)
                self.call_log_database.log_call(current_contact_uid)
                print("NEW CALL LOGGED")

                # Remove the used flag
                self._unset_call_flag()
            else:
                pass
            


    # Public methods
    def is_active(self) -> bool:
        return self.is_enabled
    
    def start(self) -> bool:
        # Set the monitor status ACTIVE
        self._set_active()

        # Create and launch the monitor process
        print("Starting the monitor process...")
        monitor_thread = threading.Thread(target=self._monitor_process, args=[])
        monitor_thread.start()
        
        self.monitor_thread = monitor_thread

        return True

    def stop(self) -> bool:
        # Set the monitor status INACTIVE
        self._set_inactive()

        return True

class GenerateCallVolumeFunction(ProcessInterface):
    def __init__(
        self,
        CRMUtilities: object,
        total_objective_calls: int,
        total_calls_per_contact: int,
        start_page: int
    ) -> None:

        super().__init__()

        # Dependencies
        self.CRMUtilities = CRMUtilities

        # Input parameters
        self.total_objective_calls = total_objective_calls
        self.total_calls_per_contact = total_calls_per_contact
        self.start_page = start_page

        # Tracking
        self.total_processed_contacts = 0
        self.total_current_calls = 0
        self.total_processed_pages = 0
        self.current_page = 0
        self.total_contacts = 0
        self.total_today_contacts = 0

        # Folder name
        lt = time.localtime()
        self.today_contacts_folder: str = f"Contacts [{lt.tm_mday}-{lt.tm_mon}-{lt.tm_year}]"
        self.today_contacts_folder_path: str = self.CRMUtilities.RESOURCES_TABLE["contacts_information"] + "/" + self.today_contacts_folder

    # ------------------------------------------------------------------
    def current_progress(self) -> float:
        if self.total_objective_calls == 0:
            return 0.0
        return (self.total_current_calls / self.total_objective_calls) * 100

    def current_process(self) -> dict:
        return {
            "TOTAL_PROCESSED_CONTACTS":self.total_processed_contacts,
            "TOTAL_CURRENT_CALLS":self.total_current_calls,
            "TOTAL_PROCESSED_PAGES":self.total_processed_pages,
            "CURRENT_PAGE_NUMBER":self.current_page,
            "TOTAL_CONTACTS":self.total_contacts,
            "TOTAL_TODAY_CONTACTS":self.total_today_contacts
        }

    # ------------------------------------------------------------------
    def start(self) -> bool:
        self.process_thread = threading.Thread(target=self._run, args=[])
        self.process_thread.start()
        return True

    def pause(self) -> bool: raise NotImplementedError
    def resume(self) -> bool: raise NotImplementedError
    def cancel(self) -> bool: raise NotImplementedError

    def stop(self) -> bool:
        self._set_status_finished(sucess_result=False)
        return True

    def abort(self) -> bool: raise NotImplementedError

    # ------------------------------------------------------------------
    def _signal_progress_changed(self):
        """Opcional: hook para que la UI consulte el progreso."""
        pass

    def _run(self) -> None:
        # Set status
        self._set_status_executing()

        # Ensure folder exists
        if not os.path.exists(self.today_contacts_folder_path):
            try:
                os.mkdir(self.today_contacts_folder_path)
                self.CRMUtilities.logger.info("Successfully created the today contacts folder.")
            except:
                self.CRMUtilities.logger.error("Unable to create the today contacts folder!")
                self._set_status_finished(success_result=False)
                return
        else:
            self.CRMUtilities.logger.info("Today contacts folder already exists.")

        # ------------------------------------------------------------------
        # Load total contacts page
        totalcontacts_page = self.CRMUtilities.website.get_page("totalcontacts")
        if not totalcontacts_page:
            self.CRMUtilities.logger.error("Error loading total contacts page.")
            self._set_status_finished(success_result=False)
            return

        # Navigate inside the CRM interface
        self.CRMUtilities.logger.info("Going to the calls menu...")
        totalcontacts_page.go_to_callmenu_page()
        while not totalcontacts_page.is_loaded:
            time.sleep(0.2)

        self.CRMUtilities.logger.info("Going to the 'all contacts' menu...")
        totalcontacts_page.go_to_all_contacts_menu()
        while not totalcontacts_page.is_loaded:
            time.sleep(0.2)

        # Identify last page number
        last_contacts_page = int(totalcontacts_page.query_last_menu_page())
        self.CRMUtilities.logger.info(f"Last contacts page: {last_contacts_page}")

        # Start extraction logic
        lt = time.localtime()
        actual_year = lt.tm_year
        actual_month = lt.tm_mon
        actual_day = lt.tm_mday

        # MAIN LOOP
        for page in range(self.start_page, last_contacts_page + 1):

            self.current_page = page
            self.total_processed_pages += 1

            self.CRMUtilities.logger.info(f"Processing page {page}/{last_contacts_page}...")

            # Load page
            totalcontacts_page.search_page(page)
            while not totalcontacts_page.is_loaded:
                time.sleep(0.2)

            # Extract contacts from the page
            contacts = totalcontacts_page.get_contacts()

            for contact in contacts:
                totalcontacts_page.open_contact(contact)
                profilecontact_page = self.CRMUtilities.website.get_page("contactpreview")
                print("Contact page:", profilecontact_page)
                time.sleep(1.5)

                for _ in range(1, self.total_calls_per_contact + 1):
                    print("Call:", _)
                    # Start call
                    self.CRMUtilities.logger.info(f"Making call: {_} to contact: {contact.uid}")
                    profilecontact_page.call()
                    time.sleep(4)
                    
                    # Hang up call
                    self.CRMUtilities.logger.info(f"Hanging up call for contact: {contact.uid}")
                    profilecontact_page.hangup()
                    time.sleep(2)

                # Close contact profile
                profilecontact_page.close_profile()

                time.sleep(1)

                if self.status == "FINISHED":
                    return

        # Finished successfully
        self._set_status_finished(success=True)

class ExtractTodayContactsProcess(ProcessInterface):
    def __init__(self,
        CRMUtilities: object
    ) -> None:
        # Constructor hereditance
        super().__init__()
        
        # Instance property assigment
        self.CRMUtilities = CRMUtilities

        # Process information
        self.current_page_number: int = 0
        self.total_contacts: int = 0
        self.last_contacts_page: int = 0
        self.total_today_contacts: int = 0
        self.total_processed_pages: int = 0
    
    @property
    def today_contacts_folder(self) -> str:
        return f"Contacts [{time.strftime('%d-%m-%Y')}]"
    
    @property
    def today_contacts_folder_path(self) -> str:
        return f"{self.CRMUtilities.RESOURCES_TABLE['contacts_information']}/{self.today_contacts_folder}"

    @property
    def current_progress(self) -> int | float:
        if self.current_page_number == 0 or self.last_contacts_page == 0:
            return 0.0
        else: return (self.current_page_number / self.last_contacts_page) * 100

    @property
    def current_process(self) -> dict:
        return {
            "CURRENT_PAGE_NUMBER":self.current_page_number,
            "LAST_PAGE_NUMBER":self.last_contacts_page,
            "TOTAL_CONTACTS":self.total_contacts,
            "TOTAL_TODAY_CONTACTS":self.total_today_contacts,
            "TOTAL_PROCESSED_PAGES":self.total_processed_pages
        }

    def start(self) -> bool:
        self.process_thread = threading.Thread(target=self._run, args=[])
        self.process_thread.start()
        return True

    def _run(self) -> None:
        # Set status executing
        self._set_status_executing()

        # Create the today contacts folder
        if not os.path.exists(self.today_contacts_folder_path):
            os.mkdir(self.today_contacts_folder_path)

            if not os.path.exists(self.today_contacts_folder_path):
                self.CRMUtilities.logger.error(f"We cant create the today contacts folder: {self.today_contacts_folder_path}")
                return None
            else:
                self.CRMUtilities.logger.info(f"Sucessfully created the today contacts folder: {self.today_contacts_folder_path}")
        else:
            self.CRMUtilities.logger.info(f"The today contacts folder already exists: {self.today_contacts_folder_path}. Skipping creation process")
        

        # Get the totalcontacts page
        totalcontacts_page = self.CRMUtilities.website.get_page("totalcontacts")

        if totalcontacts_page: pass
        else:
            self.CRMUtilities.logger.error("Error getting the total contacts page")
            return None
        
        # Go to the calls menu
        totalcontacts_page.go_to_callmenu_page()
        self.CRMUtilities.logger.info("Going to the calls menu...")
        while not totalcontacts_page.is_loaded: time.sleep(0.2)
        self.CRMUtilities.logger.info("Calls menu is ready")

        # Go to the "all contacts" page
        self.CRMUtilities.logger.info("Going to the \"all contacts\" menu...")
        totalcontacts_page.go_to_all_contacts_menu()
        while not totalcontacts_page.is_loaded: time.sleep(0.2)
        self.CRMUtilities.logger.info("All contacts menu is ready")

        # Search the start page
        while not totalcontacts_page.is_loaded: time.sleep(0.2)

        # Identify the last page
        self.last_contacts_page = totalcontacts_page.query_last_menu_page()

        self.CRMUtilities.logger.info(f"Last contacts page: {self.last_contacts_page}")
        
        # Set the initial information
        contacts_table = {}
        actual_year = time.localtime().tm_year
        actual_month = time.localtime().tm_mon
        actual_day = time.localtime().tm_mday

        while True:
            # Verify the current process status
            if self.status == self.FINISHED_STATUS: return None

            # Query the current page number
            print(totalcontacts_page)
            print(totalcontacts_page.identify_current_page_number)

            self.current_page_number = totalcontacts_page.identify_current_page_number()
            print(self.current_page_number)

            # Append data
            if self.current_page_number in contacts_table: pass
            else: contacts_table[self.current_page_number] = []

            # Verify the current-last page
            if self.current_page_number >= self.last_contacts_page: break

            # Extract the page contacts
            current_contacts = totalcontacts_page.get_contacts()
            self.total_contacts += len(current_contacts)

            # Process every contact (to get detailed information)
            for contact in current_contacts:
                # Verify the current process status
                if self.status == self.FINISHED_STATUS: return None
                
                # Verify the current existence of the contact information
                if os.path.exists(f"{self.today_contacts_folder_path}/{contact.uid}.json"):
                    self.CRMUtilities.logger.info(f"Contact information for UID: {contact.uid}, already exists. Skipping...")
                    continue

                # Verify the assignation date
                assignation_year = time.localtime(contact.time_assignated).tm_year
                assignation_month = time.localtime(contact.time_assignated).tm_mon
                assignation_day = time.localtime(contact.time_assignated).tm_mday

                if assignation_year == actual_year and assignation_month == actual_month and assignation_day == actual_day:
                    self.CRMUtilities.logger.info(f"Today contact: {contact.uid} | {contact.name} | {contact.phone_number}")

                    # Get the detailed contact profile
                    contact_detailed = totalcontacts_page.get_contact(contact)

                    # Insert new detailed data (hybrid profile)
                    contact_detailed.tso_id = contact.tso_id
                    contact_detailed.phone_number = contact.phone_number
                    contact_detailed.task = contact.task
                    contact_detailed.group_type = contact.group_type
                    contact_detailed.product_type = contact.product_type
                    contact_detailed.time_assignated = contact.time_assignated
                    contact_detailed.call_operator = contact.call_operator
                    contact_detailed.page_number = self.current_page_number
                    contact_detailed.call_executor = contact.call_executor

                    self.total_today_contacts += 1
                    
                    # Save the detailed contact extracted
                    contacts_table[self.current_page_number].append(contact_detailed)

                    # Save the contact information
                    try:
                        contact_info_file = open(
                            file=self.today_contacts_folder_path + "/" + f"{contact.uid}.json",
                            mode='w',
                            encoding="UTF-8"
                        )

                    except:
                        self.CRMUtilities.logger.error(f"There was an error creating the contact information file: {contact.uid}")
                        continue

                    try:
                        # Dumps the contact profile
                        contact_info_file.write(
                            json.dumps(contact_detailed.to_dict(), indent=4, ensure_ascii=False, default=serialize_object)
                        )

                    except:
                        self.CRMUtilities.logger.error(f"There was an error writting the contact information: {contact.uid}")
                        continue

                    try:
                        # Close the file
                        contact_info_file.close()
                    except:
                        self.CRMUtilities.logger.error(f"There was an error closing the contact information field: {contact.uid}")
                        continue

            
            # Go to the next contacts page
            self.CRMUtilities.logger.info("Going to next contacts page...")
            totalcontacts_page.go_to_next_page()
            while not totalcontacts_page.is_loaded: time.sleep(0.2)
            self.CRMUtilities.logger.info("New contacts page is ready")
        
        self.CRMUtilities.logger.info(f"Process finished. Total contacts: {self.total_contacts} | Total today contacts: {self.total_today_contacts}")

        # Set finished status
        self._set_status_finished(sucess_result=True, status_code=0)

        # Return results
        return None
        

    def pause(self) -> bool: raise NotImplementedError
    def resume(self) -> bool: raise NotImplementedError
    def cancel(self) -> bool: raise NotImplementedError
    def stop(self) -> bool:
        self._set_status_finished(sucess_result=False)
        return True

    def abort(self) -> bool: raise NotImplementedError

class ExportContactsProcess(ProcessInterface):
    def __init__(self,
        CRMUtilities: object
    ) -> None:
        # Constructor hereditance
        super().__init__()
        
        # Instance property assigment
        self.CRMUtilities = CRMUtilities

        # Process information
        self.total_contacts: int = 0
        self.total_processed_contacts: int = 0
        self.exported_file_result: str = None
    
    @property
    def current_progress(self) -> int | float:
        if self.total_contacts == 0:
            return 0.0
        
        return (self.total_processed_contacts / self.total_contacts) * 100

    @property
    def file_contacts(self) -> str:
        return f"Contacts [{time.strftime('%d-%m-%Y')}].xlsx"
    
    @property
    def file_contacts_path(self) -> str:
        return f"{self.CRMUtilities.RESOURCES_TABLE.get('contacts_excel_format', './')}/{self.file_contacts}"
    
    @property
    def current_process(self) -> dict:
        return {
            "TOTAL_CONTACTS":self.total_contacts,
            "TOTAL_PROCESSED_CONTACTS":self.total_processed_contacts,
            "EXPORTED_FILE_RESULT":os.path.abspath(self.exported_file_result)
        }
    
    def start(self) -> bool:
        self.process_thread = threading.Thread(target=self._run, args=[])
        self.process_thread.start()
        return True
    
    def _get_contactsinfo_files(self, folder_container: str) -> list:
        # Get every file in the contacts information folder
        all_files = os.listdir(folder_container)
        
        # Verify the query result
        if not all_files: return False
        if len(all_files) == 0: return False
        
        contacts_list = []
        
        for file_name in all_files:
            file_path = folder_container + "/" + file_name
            
            # Verify the file extension
            if not file_path.endswith("json"):
                print("Bad file extension detected:", file_path)
                continue
            
            # Open the file
            file_handler = open(file=file_path, mode='r', encoding="UTF-8")
            
            # Verify the open result
            if not file_handler:
                print("Error opening contact information file:", file_path)
                continue
            
            # Read the file content
            try:
                file_content = file_handler.read()
                contact_info = json.loads(file_content)
                
                # Make a contact object
                #contact_object = Contact(contact_info)
                contacts_list.append(contact_info)
            except KeyboardInterrupt:
                print("Error reading or parsing contact information file:", file_path)
            finally:
                try:
                    file_handler.close()
                except:
                    print("There was an error closing the contact information file:", file_path)
        
        # Return results
        return contacts_list

    def _get_folder_container(self):
        SELECTOR_CONTAINER_CONTROLLER = tkinter.Tk()
        SELECTOR_CONTAINER_CONTROLLER.withdraw()
        
        folder_path = filedialog.askdirectory(
            initialdir=os.getcwd(),
            title="Select the container folder of the contact data files"
        )
        
        return folder_path

    def _run(self) -> None:
        # Set status executing
        self._set_status_executing()

        # Get the folder container of contacts
        folder_container = self._get_folder_container()

        if folder_container == "": 
            messagebox.showerror(
                title="Error selecting folder container",
                message="You must select a valid folder container to save the contacts Excel file"
            )

            # Set status finished
            self._set_status_finished(success_result=False)

            return None
        
        # Get the contacts from the information files
        contacts = self._get_contactsinfo_files(folder_container)

        all_contacts = []
        for contact in contacts:
            # Verify the data fprmat
            if type(contact) != dict: contact = contact.to_dict()

            # Process data
            contact["TIME_REGISTRED"] = f"{time.localtime(contact['TIME_REGISTRED']).tm_mday}/{time.localtime(contact['TIME_REGISTRED']).tm_mon}/{time.localtime(contact['TIME_REGISTRED']).tm_year}"
            
            try:
                contact["LAST_AMOUNT_TIME_APPROBED"] = f"{time.localtime(contact['LAST_AMOUNT_TIME_APPROBED']).tm_mday}/{time.localtime(contact['LAST_AMOUNT_TIME_APPROBED']).tm_mon}/{time.localtime(contact['LAST_AMOUNT_TIME_APPROBED']).tm_year}"
            except:
                pass

            contact["TIME_ASSIGNATED"] = f"{time.localtime(contact['TIME_ASSIGNATED']).tm_mday}/{time.localtime(contact['TIME_ASSIGNATED']).tm_mon}/{time.localtime(contact['TIME_ASSIGNATED']).tm_year}"

            # Store data
            #print(json.dumps(contact, indent=4))
            all_contacts.append(contact)
        
        actual_year = time.localtime().tm_year
        actual_month = time.localtime().tm_mon
        actual_day = time.localtime().tm_mday

        # Create a pandas data-frame
        data_frame = pandas.DataFrame(all_contacts)

        # Verify the existence of the file and update file if exists
        if os.path.exists(self.file_contacts_path):
            print("Updating file:", self.file_contacts_path)
            try:
                os.remove(self.file_contacts_path)
            except OSError as e:
                print(f"Error removing the file: {e}")
                return None
        else:
            print("Creating file:", self.file_contacts_path)

        # --- INICIO DE LÓGICA DE FORMATO AVANZADO ---
        
        # Usamos 'xlsxwriter' como motor para tener control total del estilo
        writer = pandas.ExcelWriter(self.file_contacts_path, engine='xlsxwriter')
        
        # Convertimos el dataframe a Excel. 
        # freeze_panes=(1, 0) fija la primera fila (cabecera)
        data_frame.to_excel(writer, sheet_name='Today contacts', index=False, freeze_panes=(1, 0))

        # Obtenemos los objetos workbook y worksheet para aplicar estilos
        workbook  = writer.book
        worksheet = writer.sheets['Today contacts']
        
        # Definimos una paleta de colores suaves (Tonos pastel)
        soft_colors = [
            '#E3F2FD', # Azul suave
            '#E8F5E9', # Verde suave
            '#FFF3E0', # Naranja suave
            '#F3E5F5', # Púrpura suave
            '#FFEBEE', # Rojo suave
            '#F1F8E9', # Lima suave
            '#E0F7FA', # Cyan suave
            '#FFF8E1'  # Amarillo suave
        ]
        
        # Formato para la cabecera (Negrita, fondo oscuro, texto blanco, borde)
        header_format = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'vcenter',
            'align': 'center',
            'fg_color': '#455A64', # Gris azulado oscuro
            'font_color': 'white',
            'border': 1
        })

        # Iteramos sobre las columnas para ajustar ancho y color
        for i, col in enumerate(data_frame.columns):
            # 1. Calcular el ancho óptimo
            # Obtenemos la longitud máxima del contenido de la columna (convirtiendo a string)
            # O la longitud del encabezado, lo que sea mayor.
            column_data_max = data_frame[col].astype(str).map(len).max()
            column_header_len = len(str(col))
            
            # Agregamos un poco de "padding" (espacio extra) para que no quede apretado
            max_len = max(column_data_max, column_header_len) + 4
            
            # Establecemos un límite máximo razonable (ej. 50 caracteres) para evitar columnas gigantes
            final_width = min(max_len, 60)
            
            # 2. Preparar el color de la columna
            # Seleccionamos un color de la lista cíclicamente
            bg_color = soft_colors[i % len(soft_colors)]
            
            # Creamos el formato para las celdas de datos
            cell_format = workbook.add_format({
                'bg_color': bg_color,
                'border': 1,
                'valign': 'vcenter'
            })
            
            # 3. Aplicar ancho de columna
            worksheet.set_column(i, i, final_width)
            
            # 4. Aplicar el color de fondo a las celdas de datos
            # Usamos conditional_format para aplicar el estilo a todas las celdas con valor (no vacías)
            # Esto asegura que el color se vea aunque Pandas ya haya escrito los datos.
            # Rango: Desde fila 1 (después del header) hasta la última fila de datos
            if len(data_frame) > 0:
                worksheet.conditional_format(1, i, len(data_frame), i, {
                    'type': 'no_errors', # Aplica a todo lo que no sea error (efectivamente todo el contenido)
                    'format': cell_format
                })
            
            # 5. Reescribir la cabecera con su formato específico
            # Esto asegura que la cabecera tenga su propio estilo y no el color de la columna
            worksheet.write(0, i, col, header_format)

        # Guardar y cerrar
        writer.close()

        # Set status finished
        self._set_status_finished(sucess_result=True)
        self.exported_file_result = self.file_contacts_path

        return None

    def pause(self) -> bool: raise NotImplementedError
    def resume(self) -> bool: raise NotImplementedError
    def cancel(self) -> bool: raise NotImplementedError
    def stop(self) -> bool:
        self._set_status_finished(sucess_result=False)
        return True

    def abort(self) -> bool: raise NotImplementedError
    
class CRMUtilities:
    # Property definition
    RESOURCES_TABLE = {
        "resources":"./resources",
        "logs":"./resources/logs",
        "call_logs":"./resources/logs/call_logs",
        "execution_logs":"./resources/logs/execution_logs",
        "contacts":"./resources/contacts",
        "user":"./resources/user",
        "contacts_information":"./resources/contacts/information",
        "contacts_formats":"./resources/contacts/formats",
        "contacts_excel_format":"./resources/contacts/formats/excel",
    }
    
    MINIMUM_CALL_TIME: int = 4
    MAXIMUM_CALL_TIME: int = 8
    WAIT_BETWEEN_CALLS = tuple(range(MINIMUM_CALL_TIME, MAXIMUM_CALL_TIME))


    def __init__(self,
        website: object
    ) -> None:
        # Property assigment
        self.website = website

        # File logs
        self.general_file_logs = f"General logs [{time.strftime('%d-%m-%Y')}].log"
        self.call_file_logs = CallLogDataBase(self.RESOURCES_TABLE["call_logs"] + "/")
        self.contacts_file_logs = f"Contact logs [{time.strftime('%d-%m-%Y')}].log"
        self.call_logger = CallLogger(self.website, self.call_file_logs)

        # Create the resources folder
        self._deploy_resources()

        # Configure logger
        self.logger = self._crear_logger(
            nombre_logger="crm.execution",
            ruta_archivo=self.RESOURCES_TABLE["execution_logs"] + "/" + self.general_file_logs
        )

        # Initialize the databases
        self.call_file_logs.open_database()

    @property
    def user_profile_file(self) -> str:
        return f"User profile.json"

    @property
    def user_profile_path(self) -> str:
        return f"{self.RESOURCES_TABLE['user']}/{self.user_profile_file}"

    # Private methods
    def _crear_logger(self, nombre_logger: str, ruta_archivo: str) -> logging.Logger:
        # Crear carpeta si no existe
        os.makedirs(os.path.dirname(ruta_archivo), exist_ok=True)

        # Crear logger
        logger = logging.getLogger(nombre_logger)
        logger.setLevel(logging.DEBUG)   # Nivel mínimo

        # Evitar múltiples handlers duplicados si la función se llama varias veces
        if not logger.handlers:
            # Crear handler para archivo
            file_handler = logging.FileHandler(ruta_archivo, encoding="utf-8")
            file_handler.setLevel(logging.DEBUG)

            # Formato del log
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            file_handler.setFormatter(formatter)

            # Asociar handler
            logger.addHandler(file_handler)

        return logger

    def _deploy_resources(self) -> bool:
        for resource in self.RESOURCES_TABLE:
            # Verify existence
            if os.path.exists(self.RESOURCES_TABLE[resource]):
                continue
            
            # Create resource
            try:
                os.mkdir(self.RESOURCES_TABLE[resource])
            except:
                print(f"[ERROR] There was an error creating the resource folder: {self.RESOURCES_TABLE[resource]}")
                return False
        
        return True
    
    def _get_contactsinfo_files(self, folder_container: str) -> list:
        # Get every file in the contacts information folder
        all_files = os.listdir(folder_container)
        
        # Verify the query result
        if not all_files: return False
        if len(all_files) == 0: return False
        
        contacts_list = []
        
        for file_name in all_files:
            file_path = folder_container + "/" + file_name
            
            # Verify the file extension
            if not file_path.endswith("json"):
                print("Bad file extension detected:", file_path)
                continue
            
            # Open the file
            file_handler = open(file=file_path, mode='r', encoding="UTF-8")
            
            # Verify the open result
            if not file_handler:
                print("Error opening contact information file:", file_path)
                continue
            
            # Read the file content
            try:
                file_content = file_handler.read()
                contact_info = json.loads(file_content)
                
                # Make a contact object
                #contact_object = Contact(contact_info)
                contacts_list.append(contact_info)
            except KeyboardInterrupt:
                print("Error reading or parsing contact information file:", file_path)
            finally:
                try:
                    file_handler.close()
                except:
                    print("There was an error closing the contact information file:", file_path)
        
        # Return results
        return contacts_list

    def _get_folder_container(self):
        SELECTOR_CONTAINER_CONTROLLER = tkinter.Tk()
        SELECTOR_CONTAINER_CONTROLLER.withdraw()
        
        folder_path = filedialog.askdirectory(
            initialdir=os.getcwd(),
            title="Select the container folder of the contact data files"
        )
        
        return folder_path

    # Public methods
    def set_user_profile(self, username: str, password: str, update: bool = False) -> bool:
        # Verify the existence of the user profile file
        if os.path.exists(self.user_profile_path):
            if not update: return True
        
        try:
            # Open the user profile file
            user_profile_file = open(
                file=self.user_profile_path,
                mode='w',
                encoding="UTF-8",
            )
            
            # Write the user profile data
            user_profile_file.write(
                json.dumps(
                    {
                        "USERNAME":username,
                        "PASSWORD":password
                    }, indent=4, ensure_ascii=False
                )
            )
            
            # Close the user profile file
            user_profile_file.close()
            
            # Return results
            return True
        except:
            return False

    def get_user_profile(self) -> dict | bool:
        # Verify the eistence of the user profile file
        #print(self.user_profile_path)
        #print(os.path.exists(self.user_profile_path))
        if not os.path.exists(self.user_profile_path): return False
        
        # Try to open and read the user profile file
        try:
            self.logger.info("Creating user profile file...")
            user_profile_file = open(
                file=self.user_profile_path,
                mode='r',
                encoding="UTF-8"
            )
            self.logger.info("User profile file created sucessfully")
            
            # Read all the data
            data = user_profile_file.read()
            
            # Close the file
            user_profile_file.close()
            
            # Deformat the data
            user_profile = json.loads(data)

            # Return results
            return user_profile
        except OSError:
            return False
    
    def start_call_logs(self) -> bool:
        return self.call_logger.start()
    
    def stop_call_logs(self) -> bool:
        return self.call_logger.stop()

    def update_user_profile(self, username: str, password: str) -> bool:
        try:
            userprofile_file = open(
                file=self.RESOURCES_TABLE["user"] + "User profile.json",
                mode='w',
                encoding="UTF-8"
            )

            userprofile_file.write(
                json.dumps(
                    {
                        "USERNAME":username,
                        "PASSWORD":password
                    },
                    indent=4
                )
            )

            userprofile_file.close()
            return True
        except:
            return False
    
    def make_call_volume(self, objective_calls: int, total_calls_per_contact: int, start_page: int = 1, agent_user: bool = False) -> bool:
        # Verify the operation mode
        if agent_user:
            # Request parameters to the user
            objective_calls: int = None
            while True:
                objective_calls = input("Specify the objective calls (only type integer numbers):\n>>> ")
                
                try:
                    objective_calls = int(objective_calls)
                except:
                    print("Error. Please specify a integer number. Try again")
                    continue

                if objective_calls <= 0:
                    print("Error. Please specify a number greather than 0. Try again")
                    continue

                # Stop the request
                break

            total_calls_per_contact: int = None
            while True:
                total_calls_per_contact = input("Specify the total calls per contact (only type integer numbers):\n>>> ")
                
                try:
                    total_calls_per_contact = int(total_calls_per_contact)
                except:
                    print("Error. Please specify a integer number. Try again")
                    continue

                if total_calls_per_contact <= 0:
                    print("Error. Please specify a number greather than 0. Try again")
                    continue

                # Stop the request
                break

            start_page: int = None
            while True:
                start_page = input("Specify the start page (only type integer numbers):\n>>> ")
                
                try:
                    start_page = int(start_page)
                except:
                    print("Error. Please specify a integer number. Try again")
                    continue

                if start_page <= 0:
                    print("Error. Please specify a number greather than 0. Try again")
                    continue

                # Stop the request
                break
        else:
            pass

        # Data establishment
        print("Total volume calls objective:", objective_calls)
        total_calls = 0
        
        # Get the totalcontacts page
        totalcontacts_page = self.website.get_page("totalcontacts")

        if totalcontacts_page: pass
        else: return False
        
        # Make calls volume process
        # Go to the calls menu
        print("Going to the calls menu...")
        totalcontacts_page.go_to_callmenu_page()
        while not totalcontacts_page.is_loaded:
            print("Waiting for the calls menu to be ready...")
        print("Calls menu is ready.")
        
        # Go to the "all contacts" page
        print("Going to the 'all contacts' menu...")
        totalcontacts_page.go_to_all_contacts_menu()
        while not totalcontacts_page.is_loaded:
            print("Waiting for the 'all contacts' menu to be ready...")
        print("'All contacts' menu is ready.")
        
        # Search the start page
        # Identify the last page
        last_contacts_page = int(totalcontacts_page.query_last_menu_page())

        # Verify start-end page
        if start_page > last_contacts_page:
            print(f"The start page is greather than the last page. First page: {start_page}. Last page: {last_contacts_page}")
            return False
        
        # Verify the start page value
        if start_page < 1:
            print("We cant use pages less than: 1")
            return False
        
        # Search the specified start page
        search_result = totalcontacts_page.search_page(start_page)

        # Verify result
        if not search_result:
            print(f"There was an error searching the contacts page: {start_page}")
            return False
        

        print("Last contacts page:", last_contacts_page)
        while not totalcontacts_page.is_loaded:
            print("Waiting for the 'all contacts' menu to be ready...")
        print("'All contacts' menu is ready.")
        
        print("Starting process...")
        while True:
            if total_calls >= objective_calls:
                print("Objective calls reached. Stopping process.")
                break
            
            # Identify the current contacts page
            current_contacts_page = int(totalcontacts_page.identify_current_page_number())
            print("Current contacts page:", current_contacts_page)
            while not totalcontacts_page.is_loaded:
                print("Waiting for the 'all contacts' menu to be ready...")
            print("'All contacts' menu is ready.")

            if current_contacts_page > last_contacts_page:
                print("No more contacts pages available. Stopping process.")
                break
            
            # Extract all contacts (for first time)
            current_contacts = totalcontacts_page.extract_all_contacts_page()
            print("Contacts in current page:", len(current_contacts))
            while not totalcontacts_page.is_loaded:
                print("Waiting for the 'all contacts' menu to be ready...")
            print("'All contacts' menu is ready.")

            # Process each contact
            for contact in current_contacts:
                if total_calls >= objective_calls:
                    print("Objective calls reached. Stopping process.")
                    break
                
                # Verify the current call status
                if totalcontacts_page.is_on_wait():
                    # Set unwait status
                    totalcontacts_page.unset_wait()
                    time.sleep(3)
                    
                print("Processing contact:", contact.name, "-", "Time assignated:", contact.time_assignated)
                
                # Open contact
                print("Opening contact...")
                #continue
                totalcontacts_page.open_contact(contact)
                while not self.website.get_page("contactpreview").is_loaded:
                    print("Waiting for the contact preview to be ready...")
                print("Contact preview is ready.")
                
                # Make calls per contact
                print("Starting calls for contact...")
                for _ in range(total_calls_per_contact):
                    print("Making call number:", total_calls + 1)
                    call_result = totalcontacts_page.call()
                    total_calls += 1

                    # Verify the call result
                    if not call_result:
                        print("[ERROR] THERE WAS A ERROR MAKING THE CALL")
                        break


                    # Log the call event
                    self.call_file_logs.log_call(contact.uid)
                    time.sleep(random.choice(self.WAIT_BETWEEN_CALLS))
                    
                    print("Total calls made so far:", total_calls)
                    if total_calls >= objective_calls:
                        print("Objective calls reached. Stopping process.")
                        break
                    
                    # Hangup call
                    print("Hanging up call...")
                    totalcontacts_page.hangup()
                    time.sleep(8)
                
                # Close contact profile
                print("Closing contact profile...")
                self.website.get_page("contactpreview").close_profile()
                while not totalcontacts_page.is_loaded: print("Waiting for the 'all contacts' menu to be ready...")
                print("'All contacts' menu is ready.")
            
            # Go to next contacts page
            print("Going to next contacts page...")
            totalcontacts_page.go_to_next_page()
            while not totalcontacts_page.is_loaded:
                print("Waiting for the 'all contacts' menu to be ready...")
            print("'All contacts' menu is ready.")
        
        
        return True

    def extract_today_contacts(self, get_details: bool = False, autosave_contacts: bool = True, user_agent: bool = False) -> dict:
        if user_agent:
            while True:
                get_details = input("¿You want to extract detailed profiles?\n[y/n] >>> ")
                
                if get_details.lower().strip() == "y":
                    get_details = True
                    break
                elif get_details.lower().strip() == "n":
                    get_details = False
                    break
                else:
                    print("Wrong option. Try again")
                    continue
            
        else:
            pass
        # Create the today contacts folder
        today_contacts_folder = f"Contacts [{time.localtime().tm_mday}-{time.localtime().tm_mon}-{time.localtime().tm_year}]"
        today_contacts_folder_path = self.RESOURCES_TABLE["contacts_information"] + "/" + today_contacts_folder

        # Verify today contacts folder existence
        if not os.path.exists(today_contacts_folder_path):
            # Create folder
            os.mkdir(today_contacts_folder_path)

            # Verify the existence
            if not os.path.exists(today_contacts_folder_path):
                print("[ERROR] We can´t create the today contacts folder")
                return False
            else:
                print("Sucesfully created the today contacts folder")
        else:
            print("The today contacts folder already exists. Skipping creation process...")


        # Get totalcontacts page
        totalcontacts_page = self.website.get_page("totalcontacts")

        if totalcontacts_page: pass
        else: return False

        # Go to the calls menu
        # Go to the calls menu
        print("Going to the calls menu...")
        totalcontacts_page.go_to_callmenu_page()
        while not totalcontacts_page.is_loaded: print("Waiting for the calls menu to be ready...")
        print("Calls menu is ready.")
        
        # Go to the "all contacts" page
        print("Going to the 'all contacts' menu...")
        totalcontacts_page.go_to_all_contacts_menu()
        while not totalcontacts_page.is_loaded: print("Waiting for the 'all contacts' menu to be ready...")
        print("'All contacts' menu is ready.")
        
        # Search the start page
        # Identify the last page
        last_contacts_page = int(totalcontacts_page.query_last_menu_page())

        print("Last contacts page:", last_contacts_page)
        while not totalcontacts_page.is_loaded: print("Waiting for the 'all contacts' menu to be ready...")
        print("'All contacts' menu is ready.")
        
        print("Starting process...")
        contacts_table = {}

        # Query the current date
        actual_year = time.localtime().tm_year
        actual_month = time.localtime().tm_mon
        actual_day = time.localtime().tm_mday

        total_contacts = 0
        total_todays_contacts = 0

        while True:
            # Query the current page number
            current_page_number = int(totalcontacts_page.identify_current_page_number())

            # Append data
            if current_page_number in contacts_table: pass
            else: contacts_table[current_page_number] = []

            # Verify the current-last page
            if current_page_number >= last_contacts_page:
                break

            # Extract the page contacts
            #current_contacts = totalcontacts_page.extract_all_contacts_page(get_details=get_details)
            current_contacts = totalcontacts_page.get_contacts()
            print("Contacts in current page:", len(current_contacts))

            total_contacts += len(current_contacts)

            # Process every contact
            for contact in current_contacts:
                if autosave_contacts:
                    # Verify the current existence of the contact information
                    if os.path.exists(today_contacts_folder_path + "/" + f"{contact.uid}.json"):
                        print(f"Contact information for UID: {contact.uid} already exists. Skipping...")
                        continue
                    
                # Verify the assignation date
                assignation_year = time.localtime(contact.time_assignated).tm_year
                assignation_month = time.localtime(contact.time_assignated).tm_mon
                assignation_day = time.localtime(contact.time_assignated).tm_mday

                if assignation_year == actual_year and assignation_month == actual_month and assignation_day == actual_day:
                    print("="*30)
                    print(f"Assignation time: {assignation_day}/{assignation_month}/{assignation_year}")
                    print(f"Today´s contact: {contact.name} | Page: {contact.page_number} | UID: {contact.uid}")
                    print("Contact basic information:")
                    print(json.dumps(contact.to_dict(), indent=4, ensure_ascii=False))

                    print("Getting contact details...")
                    contact_detailed = totalcontacts_page.get_contact(contact)

                    # Insert new data
                    # TSO identification
                    contact_detailed.tso_id = contact.tso_id
                    contact_detailed.phone_number = contact.phone_number
                    contact_detailed.task = contact.task
                    contact_detailed.group_type = contact.group_type
                    contact_detailed.product_type = contact.product_type
                    contact_detailed.time_assignated = contact.time_assignated
                    contact_detailed.call_operator = contact.call_operator
                    contact_detailed.page_number = current_page_number
                    contact_detailed.call_executor = contact.call_executor

                    print("Detailed contact profile:")
                    print(json.dumps(contact_detailed.to_dict(), indent=4, ensure_ascii=False, default=serialize_object))
                    print("="*30)

                    total_todays_contacts += 1
                    contacts_table[current_page_number].append(contact_detailed)
                    
                    # Auto save the extracted contact
                    if autosave_contacts:
                        print("Autosaving contact information...")
                        try:
                            contact_info_file = open(
                                file=today_contacts_folder_path + "/" + f"{contact.uid}.json",
                                mode='w',
                                encoding="UTF-8"
                            )

                            print("Contact file sucessfully created")
                        except:
                            print("There was an error creating the contact information file")
                            continue

                        try:
                            # Dumps the contact profile
                            contact_info_file.write(
                                json.dumps(contact_detailed.to_dict(), indent=4, ensure_ascii=False, default=serialize_object)
                            )

                            print("Contact information sucessfully writed")
                        except:
                            print("There was an error writting the contact information")
                            continue

                        try:
                            # Close the file
                            contact_info_file.close()

                            print("Contact information file closed sucessfully")
                        except:
                            print("There was an error closing the contact information file")
                            continue
                    else:
                        print("Autosave contacts is disabled. Skipping...")


            # Go to the next contacts page
            print("Going to next contacts page...")
            totalcontacts_page.go_to_next_page()
            while not totalcontacts_page.is_loaded: print("Waiting for the 'all contacts' menu to be ready...")
            print("'All contacts' menu is ready.")


        print("Total contacts:", total_contacts)
        print("Total todays contacts:", total_todays_contacts)
        
        # Return results
        return contacts_table

    def export_contacts_to_excel(self,
            contacts: dict = None,
            user_agent: bool = False
        ) -> str | bool:
            if user_agent:
                # Request folder container to the user
                folder_container = self._get_folder_container()
                print("Folder container:", folder_container)
                
                if folder_container == "": 
                    messagebox.showerror(
                        title="Error selecting folder container",
                        message="You must select a valid folder container to save the contacts Excel file"
                    )
                    return False
            
                # Get the contacts from the information files
                contacts = self._get_contactsinfo_files(folder_container)
            else:
                if not contacts:
                    return False
            
            # Process pages
            print("Contacts retrieved:")
            # print(contacts) # Comentado para no saturar la consola si son muchos
            
            all_contacts = []
            for contact in contacts:
                # Verify the data fprmat
                if type(contact) != dict: contact = contact.to_dict()

                # Process data
                contact["TIME_REGISTRED"] = f"{time.localtime(contact['TIME_REGISTRED']).tm_mday}/{time.localtime(contact['TIME_REGISTRED']).tm_mon}/{time.localtime(contact['TIME_REGISTRED']).tm_year}"
                
                try:
                    contact["LAST_AMOUNT_TIME_APPROBED"] = f"{time.localtime(contact['LAST_AMOUNT_TIME_APPROBED']).tm_mday}/{time.localtime(contact['LAST_AMOUNT_TIME_APPROBED']).tm_mon}/{time.localtime(contact['LAST_AMOUNT_TIME_APPROBED']).tm_year}"
                except:
                    pass

                contact["TIME_ASSIGNATED"] = f"{time.localtime(contact['TIME_ASSIGNATED']).tm_mday}/{time.localtime(contact['TIME_ASSIGNATED']).tm_mon}/{time.localtime(contact['TIME_ASSIGNATED']).tm_year}"

                # Store data
                print(json.dumps(contact, indent=4))
                all_contacts.append(contact)

            print(f"Total contacts to export: {len(all_contacts)}")
            
            # Query the current date
            actual_year = time.localtime().tm_year
            actual_month = time.localtime().tm_mon
            actual_day = time.localtime().tm_mday

            # Create a pandas data-frame
            data_frame = pandas.DataFrame(all_contacts)

            # Definir ruta y nombre de archivo
            file_name = f"Contacts [{actual_day}-{actual_month}-{actual_year}]"
            # Asumiendo que self.RESOURCES_TABLE está disponible
            output_dir = self.RESOURCES_TABLE.get("contacts_excel_format", ".") 
            file_path = os.path.join(output_dir, file_name + ".xlsx")

            # Verify the existence of the file and remove if exists
            if os.path.exists(file_path):
                print("Updating file:", file_path)
                try:
                    os.remove(file_path)
                except OSError as e:
                    print(f"Error removing the file: {e}")
                    return False
            else:
                print("Creating file:", file_path)

            # --- INICIO DE LÓGICA DE FORMATO AVANZADO ---
            
            # Usamos 'xlsxwriter' como motor para tener control total del estilo
            writer = pandas.ExcelWriter(file_path, engine='xlsxwriter')
            
            # Convertimos el dataframe a Excel. 
            # freeze_panes=(1, 0) fija la primera fila (cabecera)
            data_frame.to_excel(writer, sheet_name='Contacts', index=False, freeze_panes=(1, 0))
            
            # Obtenemos los objetos workbook y worksheet para aplicar estilos
            workbook  = writer.book
            worksheet = writer.sheets['Contacts']
            
            # Definimos una paleta de colores suaves (Tonos pastel)
            soft_colors = [
                '#E3F2FD', # Azul suave
                '#E8F5E9', # Verde suave
                '#FFF3E0', # Naranja suave
                '#F3E5F5', # Púrpura suave
                '#FFEBEE', # Rojo suave
                '#F1F8E9', # Lima suave
                '#E0F7FA', # Cyan suave
                '#FFF8E1'  # Amarillo suave
            ]
            
            # Formato para la cabecera (Negrita, fondo oscuro, texto blanco, borde)
            header_format = workbook.add_format({
                'bold': True,
                'text_wrap': True,
                'valign': 'vcenter',
                'align': 'center',
                'fg_color': '#455A64', # Gris azulado oscuro
                'font_color': 'white',
                'border': 1
            })

            # Iteramos sobre las columnas para ajustar ancho y color
            for i, col in enumerate(data_frame.columns):
                # 1. Calcular el ancho óptimo
                # Obtenemos la longitud máxima del contenido de la columna (convirtiendo a string)
                # O la longitud del encabezado, lo que sea mayor.
                column_data_max = data_frame[col].astype(str).map(len).max()
                column_header_len = len(str(col))
                
                # Agregamos un poco de "padding" (espacio extra) para que no quede apretado
                max_len = max(column_data_max, column_header_len) + 4
                
                # Establecemos un límite máximo razonable (ej. 50 caracteres) para evitar columnas gigantes
                final_width = min(max_len, 60)
                
                # 2. Preparar el color de la columna
                # Seleccionamos un color de la lista cíclicamente
                bg_color = soft_colors[i % len(soft_colors)]
                
                # Creamos el formato para las celdas de datos
                cell_format = workbook.add_format({
                    'bg_color': bg_color,
                    'border': 1,
                    'valign': 'vcenter'
                })
                
                # 3. Aplicar ancho de columna
                worksheet.set_column(i, i, final_width)
                
                # 4. Aplicar el color de fondo a las celdas de datos
                # Usamos conditional_format para aplicar el estilo a todas las celdas con valor (no vacías)
                # Esto asegura que el color se vea aunque Pandas ya haya escrito los datos.
                # Rango: Desde fila 1 (después del header) hasta la última fila de datos
                if len(data_frame) > 0:
                    worksheet.conditional_format(1, i, len(data_frame), i, {
                        'type': 'no_errors', # Aplica a todo lo que no sea error (efectivamente todo el contenido)
                        'format': cell_format
                    })
                
                # 5. Reescribir la cabecera con su formato específico
                # Esto asegura que la cabecera tenga su propio estilo y no el color de la columna
                worksheet.write(0, i, col, header_format)

            # Guardar y cerrar
            writer.close()

            return file_path