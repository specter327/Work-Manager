class Contact:
    # Property definition
    ADMIN_DOMAIN_CONTACT_QUERY_PATH: str = "https://admin.oa.wowcredito.com/tele-sale/userInfo?uid="

    def __init__(self,
        #contact: WebElement,
        data_row, 
        action_row, 
        headers, 
        row_index
    ):
        # Property definition
        self.name: str = None
        self.uid: str = None 
        self.url_query: str = None 
        self.url_details: str = None
        self.url_preview: str = None
        self.genre: GENRES = None
        self.phone_number: str = None
        self.email: str = None
        self.time_assignated: int = None
        self.clients_base: str = None
        self.time_registred: int = None
        self.invalidate: bool = None
        self.application: str = None
        self.term: str = None
        self.user_status: USER_STATUSES = None
        self.amount_limit: float = None
        self.amount_time_limit: int = None
        self.amount_available: float = None
        self.last_amount_time_approbed: int = None
        self.last_amount_increment: float = None
        self.amount_limit_incremented: bool = None
        self.amount_increment_total: float = None
        self.available_discount_coupon: bool = None
        self.available_discount_cupons: list | None = None
        self.reservation: str = None
        
        self.call_button: WebElement = None
        self.preview_button: WebElement = None
        self.details_button: WebElement = None
        self.program_button: WebElement = None
        self.invalidate_button: WebElement = None
    
        # Initialize contact object        
        # Set contact data
        contact_data = self._extract_contact_data(data_row, headers)

        if contact_data: pass
        else:
            raise ValueError("There was an error extracting the contact data")
        
        if self._set_contact_data(contact_data): pass
        else:
            raise ValueError("There was an error setting the contact data")
        
        # Set contact actions
        contact_actions = self._extract_contact_actions(action_row)
        
        if contact_actions: pass
        else: raise ValueError("There was an error extracting the contact actions")
        
        if self._set_contact_actions(contact_actions): pass
        else: raise ValueError("There was an error setting the contact actions")
    
    # Private methods
    def _extract_contact_data(self, data_row: WebElement, headers: List[str]):
            """
            Extrae todos los campos de datos (TD y TH) de la fila de datos usando 
            la estructura XPath definida por el usuario.
            """
            contact_data = {}
            contact_id = 'N/A'
            
            try:
                # 1. Columna TD[1]: ID del Contacto (value del checkbox)
                contact_id_element = data_row.find_element(By.XPATH, "./td[1]/input")
                contact_id = contact_id_element.get_attribute("value")
                contact_data['id'] = contact_id
                
                # 2. Columna TH[1]: Tarea/Lote y URL de Detalles
                tarea_lote_element = data_row.find_element(By.XPATH, "./th[1]/a")
                contact_data['task'] = tarea_lote_element.text.strip()
                contact_data['url_details'] = tarea_lote_element.get_attribute("href")
                
                # 3. Datos de las siguientes columnas <th> (Usamos la posición relativa)
                # Usamos la función auxiliar para hacer la extracción robusta
                
                contact_data['time_assignated'] = self._get_text_or_none(data_row, "./th[2]")
                contact_data['reservation'] = self._get_text_or_none(data_row, "./th[3]")
                contact_data['date_time'] = self._get_text_or_none(data_row, "./th[4]")
                contact_data['uid'] = self._get_text_or_none(data_row, "./th[5]")
                contact_data['name'] = self._get_text_or_none(data_row, "./th[6]")
                contact_data['phone_number'] = self._get_text_or_none(data_row, "./th[7]")
                contact_data['clients_base'] = self._get_text_or_none(data_row, "./th[8]")
                contact_data['product_type'] = self._get_text_or_none(data_row, "./th[9]")
                
                # 4. Columna TH[10]: Email (con limpieza de ****)
                email_raw = self._get_text_or_none(data_row, "./th[10]")
                contact_data['email'] = email_raw.replace("****", "").strip() if email_raw else None
                
                # 5. Columna TH[11]: Fecha de Registro
                contact_data['time_registred'] = self._get_text_or_none(data_row, "./th[11]")
                
                # 6. Columna TD[2]: Asignado a
                contact_data['assigned_to'] = self._get_text_or_none(data_row, "./td[2]")
                
                # 7. Columna TD[3]: Invalidar (yes/no)
                invalidate_text = self._get_text_or_none(data_row, "./td[3]")
                contact_data['invalidate'] = invalidate_text == 'yes' if invalidate_text is not None else None
                
                return contact_data
                # Nota: El campo url_preview y los botones ya no se extraen aquí, 
                # sino en la fila de acción (action_row) o se obtienen del botón 
                # mapeado en _extract_actions.
                
            except NoSuchElementException as e:
                print(f"❌ Error al extraer datos del contacto (ID: {contact_id}). Falló la búsqueda de un elemento interno clave. {e}")
                return False
            except Exception as e:
                print(f"❌ Error inesperado al extraer datos del contacto (ID: {contact_id}): {e}")
                return False

    def _extract_contact_actions(self, action_row: WebElement):
        """Extrae los WebElements de acción y los mapea por su texto visible."""
        actions = {}
        try:
            action_cell = action_row.find_element(By.TAG_NAME, "td") 
            action_elements = action_cell.find_elements(By.TAG_NAME, "a")
            
            for element in action_elements:
                name = element.get_attribute('textContent').strip()
                
                # Mapeo y limpieza de nombres estáticos (eliminando iconos)
                if "Vista previa" in name:
                    clean_name = "preview"
                elif "Llamar" in name:
                    clean_name = "call"
                elif "Programar" in name:
                    clean_name = "program"
                elif "Ver detalles" in name:
                    clean_name = "details"
                elif "Invalidar" in name:
                    clean_name = "invalidate"
                else:
                    # Si aparece un botón desconocido
                    clean_name = f"Acción desconocida {len(self._actions)}"
                    
                actions[clean_name] = element

            return actions
        except Exception as e:
            print(f"Error al extraer y mapear acciones: {e}")
            return False

    def _set_contact_data(self, contact_data: dict) -> bool:
        try:
            # 1. Asignación directa (strings, booleans)
            self.contact_id = contact_data.get('id')
            self.name = contact_data.get('name')
            self.uid = contact_data.get('uid')
            self.phone_number = contact_data.get('phone_number')
            self.email = contact_data.get('email')
            self.clients_base = contact_data.get('clients_base')
            self.product_type = contact_data.get('product_type')
            self.assigned_to = contact_data.get('assigned_to')
            self.task = contact_data.get('task')
            self.reservation = contact_data.get('reservation')
            self.date_time = contact_data.get('date_time')
            
            # 2. Asignación de URLs (Usando 'url_details' como la principal 'self.url')
            self.url_details = contact_data.get('url_details')
            self.url_preview = contact_data.get('url_preview')
            self.url_query = self.ADMIN_DOMAIN_CONTACT_QUERY_PATH + self.uid
            #self.url = self.url_details or self.url_preview # Usar la más detallada como principal
            
            # 3. Conversión/Asignación de fechas y booleanos
            self.time_assignated = contact_data.get('time_assignated') # str
            self.time_registred = contact_data.get('time_registred') # str
            self.invalidate = contact_data.get('invalidate', False) # bool
            self.call_button = contact_data.get("call_buton")
            self.preview_button = contact_data.get("preview_button")

            # 4. Los campos faltantes (amount_limit, genre, etc.) permanecen como None
            
            return True
        except KeyError as e:
            # Esto ocurriría si __extract_contact_data no incluyera alguna de las claves esperadas
            raise KeyError(f"Error al asignar datos: Clave '{e}' no encontrada en el diccionario de datos.")
        except Exception as e:
            # Fallo en la conversión de tipos (si se intenta convertir una cadena a int/float)
            raise ValueError(f"Error inesperado durante la asignación de datos: {e}")

    def _set_contact_actions(self, actions: dict) -> bool:
        self.preview_button = actions.get("preview", None)
        self.call_button = actions.get("call", None)
        self.details_button = actions.get("details", None)
        self.program_button = actions.get("program", None)
        self.invalidate_button = actions.get("invalidate", None)
        
        return True

    def _get_text_or_none(self, element: WebElement, xpath_part: str) -> Any | None:
        """Función auxiliar para manejar la ausencia de elementos internos."""
        try:
            # Usamos el elemento principal (data_row) como contexto para el XPath
            return element.find_element(By.XPATH, xpath_part).text.strip()
        except NoSuchElementException:
            return None
        except Exception:
            return None
        
    def __extract_contact_data(self) -> dict | bool:
        row = self.contact_object_element # El WebElement <tr>
        contact_id = 'N/A' 
        contact_data = {}
        
        try:
            # 1. Columna TD[1]: ID del Contacto (value del checkbox)
            contact_id = row.find_element(By.XPATH, "./td[1]/input").get_attribute("value")
            contact_data['id'] = contact_id
            
            # 2. Columna TH[1]: Tarea/Lote y URL de Detalles
            tarea_lote_element = row.find_element(By.XPATH, "./th[1]/a")
            contact_data['task'] = tarea_lote_element.text.strip()
            contact_data['url_details'] = tarea_lote_element.get_attribute("href")
            
            # 3. Datos de las siguientes columnas <th> (Usamos la posición relativa)
            contact_data['time_assignated'] = row.find_element(By.XPATH, "./th[2]").text.strip()
            contact_data['reserva'] = row.find_element(By.XPATH, "./th[3]").text.strip()
            contact_data['date_time'] = row.find_element(By.XPATH, "./th[4]").text.strip()
            contact_data['uid'] = row.find_element(By.XPATH, "./th[5]").text.strip()
            contact_data['name'] = row.find_element(By.XPATH, "./th[6]").text.strip()
            contact_data['phone_number'] = row.find_element(By.XPATH, "./th[7]").text.strip()
            contact_data['clients_base'] = row.find_element(By.XPATH, "./th[8]").text.strip()
            contact_data['product_type'] = row.find_element(By.XPATH, "./th[9]").text.strip()
            
            # 4. Columna TH[10]: Email
            email_raw = row.find_element(By.XPATH, "./th[10]").text.strip()
            contact_data['email'] = email_raw.replace("****", "").strip() 
            
            # 5. Columna TH[11]: Fecha de Registro
            contact_data['time_registred'] = row.find_element(By.XPATH, "./th[11]").text.strip()
            
            # 6. Columna TD[2]: Asignado a
            contact_data['assigned_to'] = row.find_element(By.XPATH, "./td[2]").text.strip()
            
            # 7. Columna TD[3]: Invalidar (yes/no)
            contact_data['invalidate'] = row.find_element(By.XPATH, "./td[3]").text.strip() == 'yes'
            
            # 8. URL de Previsualización (FIX para el error)
            # Usamos find_elements para no fallar si no existe y un XPath más específico
            url_preview_elements = row.find_elements(By.XPATH, ".//td[last()]/a[contains(@data-href, 'preview.html')]")
            
            url_preview = None
            if url_preview_elements:
                url_preview = url_preview_elements[0].get_attribute("data-href")
                
            contact_data['url_preview'] = url_preview

            contact_data["preview_button"] = self.__get_preview_button()
            contact_data["call_button"] = self.__get_call_buton()

            return contact_data

        except NoSuchElementException as e:
            # Falla si falta alguna columna clave (TH[1] a TH[11] o TD[1] a TD[3])
            print(f"❌ Error al extraer datos del contacto (ID: {contact_id}). Falló la búsqueda de un elemento interno clave. {e}")
            return False
        except Exception as e:
            print(f"❌ Error inesperado al extraer datos del contacto (ID: {contact_id}): {e}")
            return False

    # Public methods
    def open_preview(self) -> bool:
        try:
            self.preview_button.click()
            return True
        except:
            return False
        
        
