# Library import
from selenium.webdriver.common.by import By
from typing import Optional, Tuple
from selenium.common.exceptions import TimeoutException, NoSuchFrameException, NoSuchElementException, ElementClickInterceptedException, StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .contactslistsheader import ContactsList

# Classes definition
class BussinesSummaryPage(ContactsList):
    # Property definition
    TIMEOUT: int = 10
    
    #MAIN_CONTENT_IDENTIFIER: Tuple[str, str] = (By.ID, "maincontent")
    BUSSINES_SUMMARY_TITLE: Tuple[str, str] = (By.XPATH, "//h1[@class='site-h1' and contains(., 'Mi lista de nombres sin llamar')]")

    # Private methods
    def _find_bussines_summary_title(self) -> bool:
        try:
            # 3. Esperar y buscar el elemento dentro del iframe
            print(f"Buscando el título del menú de llamadas (Timeout: {self.TIMEOUT}s).")
            title_element = WebDriverWait(self.website.webbrowser.driver, self.TIMEOUT).until(
                EC.presence_of_element_located(self.BUSSINES_SUMMARY_TITLE)
            )
            
            print("✅ Título 'Mi lista de nombres sin llamar' encontrado.")
            return title_element

        except TimeoutException:
            print(f"❌ Error: El título '{self.BUSSINES_SUMMARY_TITLE[1]}' no fue encontrado dentro del iframe en {self.TIMEOUT}s.")
            return None
        except NoSuchFrameException:
            print("❌ Error: No se pudo encontrar el iframe 'maincontent'.")
            return None
        except Exception as e:
            print(f"❌ Error inesperado: {type(e).__name__} - {e}")
            return None

    # Public methods
    def is_current_page(self) -> bool:
        # Focus to the main content
        if self._focus_main_contacts_frame():
            # Search the principal content title
            search_result = self._find_bussines_summary_title()

            # Unfocus the main content and return to the main document
            self._unfocus_main_contacts_frame()

            if search_result: return True
            else: return False
        else:
            return False