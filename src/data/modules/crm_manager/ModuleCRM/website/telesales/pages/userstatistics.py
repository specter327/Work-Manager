# Library import
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from typing import Optional, List

# Classes definition
class UserStatisticsPage:
    # Property definition
    CLAVE_DOCUMENTO_ESTADISTICAS = (By.ID, "maincontent")
    ENLACE_DOCUMENTO_ESTADISTICAS = "/apps/callcenter/service/owner/index.html"
    TIEMPO_LIMITE_CARGA = 10

    # Public methods
    def is_current_page(self) -> bool:
        print(f"Iniciando detección de 'EstadisticasOwnerPage'...")
        try:
            # 1. Esperar a que el iframe esté presente en el DOM y obtener el elemento.
            iframe_element = WebDriverWait(self.website.webbrowser.driver, self.TIEMPO_LIMITE_CARGA).until(
                EC.presence_of_element_located(self.CLAVE_DOCUMENTO_ESTADISTICAS)
            )
            
            # 2. Obtener el atributo 'src' del iframe.
            current_src = iframe_element.get_attribute("src")
            
            # 3. Verificar que el 'src' contenga la ruta base de la página de estadísticas.
            # Usamos 'in' porque el 'src' puede incluir la URL base completa (https://...)
            # y también los parámetros (?owner=true).
            if current_src and self.ENLACE_DOCUMENTO_ESTADISTICAS in current_src:
                print(f"✅ Detección exitosa: Iframe '{iframe_element.get_attribute('id')}' encontrado.")
                print(f"   SRC verificado: '{current_src}' contiene la ruta esperada.")
                return True
            else:
                print(f"❌ Detección fallida: Iframe encontrado, pero el SRC no coincide con la página de estadísticas.")
                print(f"   SRC encontrado: '{current_src}' | SRC esperado (parcial): '{self.ENLACE_DOCUMENTO_ESTADISTICAS}'")
                return False

        except TimeoutException:
            # El tiempo de espera se agotó sin encontrar el elemento.
            print(f"❌ Detección fallida: El iframe '{self.CLAVE_DOCUMENTO_ESTADISTICAS[1]}' no fue encontrado después de {self.TIEMPO_LIMITE_CARGA} segundos.")
            return False
        
    def get_data_cards(self, use_javascript: bool = True) -> List[dict]:
        if use_javascript:
            query_code = """// Functions definition
    function getCardsData(){
        // Search the frame document element
        let frameDocumentElement = document.getElementById("maincontent");

        // Verify the search result
        if (frameDocumentElement === null){
            return null;
        }

        // Search the data elements
        let dataElements = frameDocumentElement.contentDocument.querySelectorAll("div.layui-row div.layui-col-md3 div.uk_monitor");

        // Verify the search result
        if (dataElements.length === 0){
            return null;
        }

        // Extract the data
        let dataProfiles = [];

        for (let dataElement of dataElements){
            // Create a data profile
            let dataProfile = new Map();
            console.log("Element:");
            console.log(dataElement);

            // Extract the data element header
            let dataElementHeader = dataElement.querySelector("div.uk-measure-header").textContent.trim();

            // Extract the data value
            let dataElementValue = dataElement.querySelector("div.ukefu-measure-title").textContent.trim();

            // Set data
            console.log("Element title: " + dataElementHeader);
            console.log("Element value: " + dataElementValue);

            dataProfile.set("CARD-TITLE", dataElementHeader);
            dataProfile.set("CARD-VALUE", dataElementValue);

            // Extract the sub-data
            // Search the sub-data elements
            let subDataElements = dataElement.querySelectorAll("div.ukefu-bt-text-content span");

            // Verify search result
            if (subDataElements.length === 0){
                // Add data profile to data profiles
                console.log("Ommiting sub-elements of empty element:", dataElementHeader);
                dataProfiles.push(dataProfile);

                continue;
            }

            // Process the sub-data elements
            let subDataProfiles = [];
            let subDataProfile = new Map();

            for (let subDataElement of subDataElements){
                // Create a sub-data profile
                console.log("Sub-element:");
                console.log(subDataElement);

                // Verify if is a title or value
                if (subDataElement.style.color == ""){
                    // Is a title
                    subDataProfile.set("SUB-CARD-TITLE", subDataElement.textContent.trim());
                } else {
                    // Is a value
                    subDataProfile.set("SUB-CARD-VALUE", subDataElement.textContent.trim());
                }

                console.info(subDataProfile);
                if (subDataProfile.size == 2){
                    console.info("Completed sub-element:", subDataProfile);

                    // Add sub-data card to sub-data cards
                    subDataProfiles.push(subDataProfile);

                    // Create a new sub-data profile
                    subDataProfile = new Map();
                }
            }

            // Set sub-data profiles
            dataProfile.set("SUB-DATA", subDataProfiles);

            // Add data profile to data profiles
            dataProfiles.push(dataProfile);
        }
        
        return dataProfiles;
    }
    
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

    // Use
    let dataCards = getCardsData();
    
    // Process the data
    let dataCardsJSON = convertMapToJson(dataCards);
    
    console.info("Returning data cards:", dataCards);
    return JSON.stringify(dataCardsJSON);"""
            execution_result = self.website.webbrowser.execute_javascript(query_code)
            return execution_result
        else:
            raise NotImplementedError