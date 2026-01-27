# Library import
import time
import keyboard
import pygetwindow as gw
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

# Classes definition
class HotkeyController:
    BROWSER_KEYWORDS = ["chrome", "edge", "firefox", "brave", "opera"]
    TARGET_WINDOW_TEXT = "全渠道客服系统"  # Texto que debe incluir la ventana para activar los hotkeys

    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.browser_windows = []
        self.update_browser_windows()

    # ---------------------------------------------------------
    # 🔍 Detecta automáticamente las ventanas del navegador
    # ---------------------------------------------------------
    def update_browser_windows(self):
        """Actualiza la lista de ventanas que pertenecen al navegador."""
        self.browser_windows = []
        for w in gw.getAllWindows():
            title = (w.title or "").lower()
            if any(b in title for b in self.BROWSER_KEYWORDS):
                self.browser_windows.append(w)

    def is_target_window_focused(self) -> bool:
        """Verifica si la ventana activa incluye el texto objetivo en su título."""
        try:
            active = gw.getActiveWindow()
            if not active or not active.title:
                return False
            return self.TARGET_WINDOW_TEXT in active.title
        except Exception:
            return False

    def is_tab_active(self) -> bool:
        """Verifica si la pestaña del driver tiene foco."""
        try:
            return self.driver.execute_script("return document.hasFocus();")
        except Exception:
            return False

    # ---------------------------------------------------------
    # 🔔 Acción: Presionar botón LLAMAR
    # ---------------------------------------------------------
    def click_call_button(self):
        if not self.is_target_window_focused() or not self.is_tab_active():
            return

        try:
            self.driver.switch_to.default_content()

            try:
                btn = self.driver.find_element(By.CSS_SELECTOR, "div.outboundcall.soft-function")
                if btn and "disabled" not in btn.get_attribute("class"):
                    btn.click()
                    return
            except:
                pass

            try:
                btn = self.driver.find_element(By.CSS_SELECTOR, "div.preview.soft-function")
                if btn and "disabled" not in btn.get_attribute("class"):
                    btn.click()
                    return
            except:
                pass

        except Exception:
            pass

    # ---------------------------------------------------------
    # 🔔 Acción: Presionar botón COLGAR
    # ---------------------------------------------------------
    def click_hangup_button(self):
        if not self.is_target_window_focused() or not self.is_tab_active():
            return
        
        try:
            self.driver.switch_to.default_content()
            btn = self.driver.find_element(By.CSS_SELECTOR, "#softphone-hungup")
            if btn and "disabled" not in btn.get_attribute("class"):
                btn.click()
        except:
            pass

    # ---------------------------------------------------------
    # 🎧 Registro de hotkeys globales
    # ---------------------------------------------------------
    def register_call_hotkey(self):
        keyboard.add_hotkey("shift+x", lambda: self.click_call_button())
        #keyboard.wait()
        return True
    
    def register_hangup_hotkey(self):
        keyboard.add_hotkey("shift+c", lambda: self.click_hangup_button())
        #keyboard.wait()
        return True

class WebPageHeader:
    # Property definition
    @property
    def is_loaded(self) -> bool:
        query_code = """function isReady(){
    // Search the frame document element
    let frameDocumentElement = document.getElementById("maincontent");

    // Verify the search result
    if (frameDocumentElement === null) {
        return null;
    }

    // Verify the frame document element status, and the main document status
    return (frameDocumentElement.contentDocument.readyState === "complete") && (document.readyState === "complete");
}

// Use
return isReady();
"""

        time.sleep(4)  # Small delay to ensure the page has time to update its state
        return self.website.webbrowser.execute_javascript(query_code)

    # Public methods
    def go_to_home_page(self, use_javascript: bool = True) -> bool:
        if use_javascript:
            query_code = """// Search the button element
let homeMenuPageButton = document.querySelector("a[data-href='/apps/content.html']");

// Verify the search result
if (homeMenuPageButton === null){
    return null;
} else{
    // Execute the click interaction
    try{
        homeMenuPageButton.click();
        return true;
    } catch (error){
        return false;
    }
}"""
            execution_result = self.website.webbrowser.execute_javascript(query_code)
            return execution_result
        else:
            raise NotImplementedError

    def go_to_statistics_page(self, use_javascript: bool = True) -> bool:
        if use_javascript:
            query_code = """// Search the user statistics page
let userStatisticsPage = document.querySelector("a[data-href='/apps/callcenter/service/owner/index.html?owner=true']");

// Verify the search result
if (userStatisticsPage === null){
    return null;
} else{
    try{
        // Execute the click interaction
        userStatisticsPage.click();
        return true;
    } catch (error){
        return false;
    }
}"""
            execution_result = self.website.webbrowser.execute_javascript(query_code)
            return execution_result

    def go_to_callmenu_page(self, use_javascript: bool = True) -> bool:
        if use_javascript:
            query_code = """// Search the call menu page button
let callMenuPageButton = document.querySelector("a[data-href='/apps/callout/names/home.html']");

// Verify the search result
if (callMenuPageButton === null){
    return null
} else{
    try{
        // Execute click interaction
        callMenuPageButton.click();
        return true;
    } catch (error){
        return false
    }
}"""
            execution_result = self.website.webbrowser.execute_javascript(query_code)
            return execution_result
        else:
            raise NotImplementedError
    
    def logout(self, use_javascript: bool = True) -> bool:
        if use_javascript:
            query_code = """// Search the log out button
let logoutButton = document.querySelector("div.logout");

// Verify the search result
if (logoutButton === null){
    return null;
} else{
    try{
        // Execute the click interaction
        logoutButton.click();
        return true;
    } catch(error){
        return false;
    }
}"""

            execution_result = self.website.webbrowser.execute_javascript(query_code)
            return execution_result
        else:
            raise NotImplementedError

    def hangup(self, use_javascript: bool = True) -> bool:
        if use_javascript:
            query_code = """// Search the hang up button
let hangUpButton = document.querySelector("#softphone-hungup");

// Verify the search result
if (hangUpButton === null){
    return null;
} else{
    if (hangUpButton.classList.contains("disabled")){
        // The button is disabled
        return null;
    } else{
        try{
            // Execute the click interaction
            hangUpButton.click();
            return true;
        } catch(error){
            return false;
        }
    }
}""" 

            execution_result = self.website.webbrowser.execute_javascript(query_code)
            return execution_result
        else:
            raise NotImplementedError

    def call(self, use_javascript: bool = True) -> bool:
        if use_javascript:
            query_code = """// Search any call button option
let callButton = document.querySelector("div.outboundcall.soft-function");
let previewCallButton = document.querySelector("div.preview.soft-function");
let targetButton = null;

// Verify the search result
if (callButton && !callButton.classList.contains("disabled")){
    targetButton = callButton;
} else if (previewCallButton && !previewCallButton.classList.contains("disabled")){
    targetButton = previewCallButton;
} else{
    console.error("We dont found the preview or call button");
    return null;
}

// Verify if the button is disabled
if (targetButton.classList.contains("disabled")){
    console.error("The call/preview button is disabled");
    return null;
}

// Execute the click interaction
try{
    targetButton.click();
    return true;
 } catch(error){
    console.error("There was an error pressing the call/preview button:", error);
    return false;
 }"""

            execution_result = self.website.webbrowser.execute_javascript(query_code)
            return execution_result
        else:
            raise NotImplementedError

    def is_on_wait(self, use_javascript: bool = True) -> bool:
        if use_javascript:
            query_code = """// Search the wait button element
let agentStatusButton = document.querySelector("div#softphone-callout");

// Verify the search result
if (agentStatusButton === null){
    return null;
}

// Search the agent status options
let agentStatusOptions = agentStatusButton.querySelectorAll(":scope > div");

let currentAgentStatus = undefined;

for (let agentStatus of agentStatusOptions){
    // Verify the current agent status
    if (!agentStatus.classList.contains("disabled")){
        currentAgentStatus = agentStatus;
        break
    }
}

if (currentAgentStatus === undefined){
    return false; // En llamada
}else{
    // Return results
    return true; //currentAgentStatus.querySelector("div.text").textContent;
}

"""

            execution_result = self.website.webbrowser.execute_javascript(query_code)
            return execution_result
        else:
            raise NotImplementedError

    def set_wait(self, use_javascript: bool = True) -> bool:
        if use_javascript:
            query_code = """// Search the wait button element
    let agentStatusButton = document.querySelector("div#softphone-callout");

    // Verify the search result
    if (agentStatusButton === null){
        return null;
    }

    // Search the agent status options
    let agentStatusOptions = agentStatusButton.querySelectorAll(":scope > div");

    let currentAgentStatus = undefined;

    for (let agentStatus of agentStatusOptions){
        // Verify the current agent status
        console.info("Agent status:", agentStatus);
        if (agentStatus.textContent.trim().includes("Espera")){
            if (!agentStatus.classList.contains("disabled")){
                console.info("Current agent status:", agentStatus);
                currentAgentStatus = agentStatus;
                break
            }
        }
    }

    if (currentAgentStatus === undefined){
        return false; // En llamada/otro estado
    }else{
        // Execute click interaction
        try {
            currentAgentStatus.click();
            // Return results
            return true; // En espera
        } catch (error) {
            return false;
        }
    }"""

            return self.website.webbrowser.execute_javascript(query_code)
        else:
            raise NotImplementedError
    
    def unset_wait(self, use_javascript: bool = True) -> bool:
        if use_javascript:
            query_code = """// Search the wait button element
    let agentStatusButton = document.querySelector("div#softphone-callout");

    // Verify the search result
    if (agentStatusButton === null){
        return null;
    }

    // Search the agent status options
    let agentStatusOptions = agentStatusButton.querySelectorAll(":scope > div");

    let currentAgentStatus = undefined;

    for (let agentStatus of agentStatusOptions){
        // Verify the current agent status
        console.info("Agent status:", agentStatus);
        if (agentStatus.textContent.trim().includes("Llamada")){
            if (!agentStatus.classList.contains("disabled")){
                console.info("Current agent status:", agentStatus);
                currentAgentStatus = agentStatus;
                break
            }
        }
    }

    if (currentAgentStatus === undefined){
        return false; // En llamada/otro estado
    }else{
        // Execute click interaction
        try {
            currentAgentStatus.click();
            // Return results
            return true; // En espera
        } catch (error) {
            return false;
        }
    }"""

            return self.website.webbrowser.execute_javascript(query_code)
        else:
            raise NotImplementedError
    
    def query_current_agent_status(self, use_javascript: bool = True):
        if use_javascript:
            query_code = """// Functions definition
function extractInformationAgentStatusLogoutFail(statusElement){
    return statusElement.textContent.trim();
}
function extractInformationAgentStatusLogoutOffline(statusElement){
    return statusElement.textContent.trim();
}
function extractInformationAgentStatusAvailable(statusElement){
    return statusElement.textContent.trim();
}
function extractInformationCallHangUp(statusElement){
    return statusElement.textContent.trim();
}
function extractInformationCallOutDo(statusElement){
    return statusElement.textContent.trim();
}
function extractInformationStatusCall(statusElement){
    let caller_phone = statusElement.querySelector("div#caller").textContent.trim();
    let called_phone = statusElement.querySelector("div#called").textContent.trim();

    return caller_phone + " " + called_phone;
}
function extractInformationTimerCall(statusElement){
    let phoneNumber = statusElement.querySelectorAll("div")[0].textContent.trim();
    let timer = statusElement.querySelectorAll("div")[1].textContent.trim();

    return phoneNumber + " " + timer;
}

function extractInformationCaller(statusElement){
    return statusElement.textContent.trim()
}

// Search the status container
let statusInformationContainer = document.querySelector("div.status");

// Verify the search result
if (statusInformationContainer === null){
    return null;
}

// Search all the statusses options
let statussesOptions = statusInformationContainer.querySelectorAll(":scope > div");

// Verify the search result
if (statussesOptions === null){
    return null;
}

// Search the current status option
let currentStatusOption = undefined;

for (let statusOption of statussesOptions){
    console.log("Status option:", statusOption);
    if (statusOption.style.display != "none"){
        currentStatusOption = statusOption;
        break;
    }
}

// Verify the search result
if (currentStatusOption === undefined){
    return false;
}

// Extract the status information
console.log("Current status option:", currentStatusOption);
if (currentStatusOption.id == "ukefu_agent_status_no"){
    return extractInformationAgentStatusLogoutFail(currentStatusOption);
} else if (currentStatusOption.id == "ukefu_agent_status_offline"){
    return extractInformationAgentStatusLogoutOffline(currentStatusOption);
} else if (currentStatusOption.id == "ukefu_agent_status_ok"){
    return extractInformationAgentStatusAvailable(currentStatusOption);
} else if (currentStatusOption.id == "ukefu_hangup"){
    return extractInformationCallHangUp(currentStatusOption);
} else if (currentStatusOption.id == "ukefu_agent_docallout"){
    return extractInformationCallOutDo(currentStatusOption);
} else if (currentStatusOption.id == "ukefu_agent_status_call"){
    return extractInformationStatusCall(currentStatusOption);
} else if (currentStatusOption.id == "ukefu_agent_timer_call"){
    return extractInformationTimerCall(currentStatusOption);
} else if (currentStatusOption.id == "caller"){
    return extractInformationCaller(currentStatusOption);
}
"""

            execution_result = self.website.webbrowser.execute_javascript(query_code)
            return execution_result
        else:
            raise NotImplementedError
    
    def is_current_page(self, use_javascript: bool = True) -> bool:
        if use_javascript:
            query_code = """// Search the iframe document element
let iframeDocumentElement = document.querySelector("iframe[src='/apps/callout/names/home.html']");

// Verify the search result
if (iframeDocumentElement === null){
    return false;
} else{
    return true;
}"""

            execution_result = self.website.webbrowser.execute_javascript(query_code)
            return execution_result
        
        else:
            raise NotImplementedError

    def inject_call_hotkey(self, use_javascript: bool = True) -> bool:
        if use_javascript:
            hotkey_controller = HotkeyController(self.website.webbrowser.driver)
            hotkey_controller.register_call_hotkey()

            return True
        
            javascript_code = """
                (function() {
                    try {
                        if (window.__hotkeysInjected__) return true;
                        window.__hotkeysInjected__ = true;

                        // Intentar dar foco al documento principal
                        try { window.focus(); document.body.focus(); } catch(err) {}

                        // Función que agrega hotkeys a un documento
                        function addHotkeys(doc) {
                            try {
                                if (!doc || doc.__hotkeysAdded__) return;
                                doc.__hotkeysAdded__ = true;

                                doc.addEventListener('keydown', function(e) {
                                    try {
                                        // Ctrl + X -> call/preview
                                        if (e.ctrlKey && e.key.toLowerCase() === 'x') {
                                            let callButton = doc.querySelector("div.outboundcall.soft-function");
                                            let previewCallButton = doc.querySelector("div.preview.soft-function");
                                            let targetButton = null;

                                            if (callButton && !callButton.classList.contains("disabled")) {
                                                targetButton = callButton;
                                            } else if (previewCallButton && !previewCallButton.classList.contains("disabled")) {
                                                targetButton = previewCallButton;
                                            }

                                            if (targetButton && !targetButton.classList.contains("disabled")) {
                                                targetButton.click();
                                            }
                                        }

                                        // Ctrl + C -> hangup
                                        if (e.ctrlKey && e.key.toLowerCase() === 'c') {
                                            let hangUpButton = doc.querySelector("#softphone-hungup");
                                            if (hangUpButton && !hangUpButton.classList.contains("disabled")) {
                                                hangUpButton.click();
                                            }
                                        }
                                    } catch(err) {
                                        // Ignorar errores dentro del listener
                                    }
                                });
                            } catch(err) {}
                        }

                        // Registrar en documento principal
                        addHotkeys(document);

                        // Registrar en iframes existentes
                        let iframes = document.querySelectorAll('iframe');
                        for (let i = 0; i < iframes.length; i++) {
                            try {
                                if (iframes[i].contentDocument) {
                                    addHotkeys(iframes[i].contentDocument);
                                }
                            } catch(err) {}
                        }

                        // Observar cambios en el DOM para detectar iframes creados dinámicamente
                        let observer = new MutationObserver(function(mutations) {
                            try {
                                mutations.forEach(function(mutation) {
                                    mutation.addedNodes.forEach(function(node) {
                                        if (node.tagName && node.tagName.toLowerCase() === 'iframe') {
                                            try {
                                                if (node.contentDocument) {
                                                    addHotkeys(node.contentDocument);
                                                }
                                            } catch(err) {}
                                        }
                                    });
                                });
                            } catch(err) {}
                        });

                        observer.observe(document.body, { childList: true, subtree: true });

                        return true;
                    } catch(err) {
                        return false;
                    }
                })();
"""

            try:
                self.website.webbrowser.execute_javascript(javascript_code)
                return True
            except Exception:
                # Ignorar errores de ejecución en Selenium
                return False
        else:
            raise NotImplementedError
    
    def inject_hangup_hotkey(self, use_javascript: bool = True) -> bool:
        if use_javascript:
            hotkey_controller = HotkeyController(self.website.webbrowser.driver)
            hotkey_controller.register_hangup_hotkey()
            
            javascript_code = """(function() {
        try {
            // Evitar inyecciones múltiples
            if (window.__ctrlCHangupListener__)
                return true;

            window.__ctrlCHangupListener__ = true;

            // Listener de teclado
            document.addEventListener('keydown', function(e) {
                if (e.ctrlKey && e.key.toLowerCase() === 'c') {

                    // Buscar el botón de colgar
                    let hangUpButton = document.querySelector("#softphone-hungup");

                    if (!hangUpButton) {
                        console.error("No se encontró el botón de colgar");
                        return false;
                    }

                    if (hangUpButton.classList.contains("disabled")) {
                        console.error("El botón de colgar está deshabilitado");
                        return false;
                    }

                    try {
                        hangUpButton.click();
                        return true;
                    } catch (error) {
                        console.error("Error al hacer click en colgar:", error);
                        return false;
                    }
                }
            });

            return true;

        } catch (err) {
            return false;
        }
    })();
    """

            return self.website.webbrowser.execute_javascript(javascript_code)
        else:
            raise NotImplementedError