# Library import
from selenium.webdriver.remote.webelement import WebElement
from typing import Tuple, List, Dict, Literal, Any
from selenium.common.exceptions import TimeoutException, NoSuchElementException, NoSuchFrameException
from selenium.webdriver.common.by import By

# Property definition
GENRES = Literal["MASCULINO", "FEMENINO"]
USER_STATUSES = Literal["APROBADO", "COBRADO", "RECHAZADO", "PENDIENTE"]

# Functions definition
def serialize_object(object):
    return object.to_dict()

# Classes definition
class DiscountCoupon:
    def __init__(
        self,
        cupon_id: str,
        cupon_name: str,
        cupon_type: str,
        cupon_import: str,
        cupon_use_status: bool,
        cupon_time_valid: int,
        cupon_use_conditions: str,
        cupon_emission_time: str
    ):
        self.cupon_id = cupon_id
        self.cupon_name = cupon_name
        self.cupon_type = cupon_type
        self.cupon_import = cupon_import
        self.cupon_use_status = cupon_use_status
        self.cupon_time_valid = cupon_time_valid
        self.cupon_use_conditions = cupon_use_conditions
        self.cupon_emission_time = cupon_emission_time
    
    # Public methods
    def to_dict(self) -> dict:
        discount_coupon_profile = {
            "COUPON_ID":self.cupon_id,
            "COUPON_NAME":self.cupon_name,
            "COUPON_TYPE":self.cupon_type,
            "COUPON_IMPORT":self.cupon_import,
            "COUPON_USE_STATUS":self.cupon_use_status,
            "COUPON_USE_CONDITIONS":self.cupon_use_conditions,
            "COUPON_EMISSION_TIME":self.cupon_emission_time
        }

        return discount_coupon_profile

class Contact:
    ADMIN_DOMAIN_CONTACT_QUERY_PATH: str = "https://admin.oa.wowcredito.com/tele-sale/userInfo?uid="

    def __init__(self, profile_data: dict):
        # Campos base
        self.name: str = profile_data.get("NAME", None) # Nombre de usuario // customerName
        self.uid: str = profile_data.get("UID", None) # UID // 
        self.genre: str = profile_data.get("GENRE", None) # Género //
        self.phone_number: str = profile_data.get("PHONE_NUMBER", None) # Número de teléfono del usuario // customerMobile
        self.email: str = profile_data.get("EMAIL", None) # Buzón // email
        self.task: str = profile_data.get("TASK", None) # Tarea
        self.group_type: str = profile_data.get("GROUP_TYPE", None) # customerGroupType
        self.client_base: str = profile_data.get("CLIENT_BASE", None) # Carteras de clientes //
        self.product_type: str = profile_data.get("PRODUCT_TYPE", None) # productType
        self.application: str = profile_data.get("APPLICATION", None)
        self.tso_id: str = profile_data.get("TSO", None)

        self.user_status: str = profile_data.get("USER_STATUS", None) # Estado del usuario 
        
        self.time_registred: str = profile_data.get("TIME_REGISTRED", None) # Fecha de registro
        self.term: str = profile_data.get("TERM", None) # Plazo opcional
        self.reservation: str = profile_data.get("SOURCE_CHANNELS", None) # Reserva
        self.date_cite: int = profile_data.get("DATE_CITE", None) # Hora de la cita

        # URLs generadas automáticamente
        self.url_query: str = self.ADMIN_DOMAIN_CONTACT_QUERY_PATH + self.uid if self.uid else None
        self.url_details: str = None
        self.url_preview: str = None

        # Créditos y montos
        self.amount_limit: float = self._parse_float(profile_data.get("AMOUNT_LIMIT", None))
        self.amount_available: float = self._parse_float(profile_data.get("AMOUNT_AVAILABLE", None))
        self.amount_increment_total: float = self._parse_float(profile_data.get("Límite ajustado"))
        self.last_amount_time_approbed: str = profile_data.get("LAST_AMOUNT_TIME_APPROBED", None)

        self.amount_limit_incremented: bool = profile_data.get("Si aumentó el límite") == "Sí"
        self.last_amount_increment: float = self._parse_float(profile_data.get("Aumentar el límite"))

        # Campo booleano
        self.invalidate: bool = False  # se asigna fuera desde tabla principal

        # Información de llamada
        self.time_assignated: int = profile_data.get("ASSIGNATION_TIME", None) # Tiempo de asignacion
        self.call_executor : str = profile_data.get("CALL_EXECUTOR", None) # Asignar ejecutor	
        self.call_uuid: str = None

        # Cupones
        self.available_discount_coupon: bool = profile_data.get("ID del cupón") is not None
        self.available_discount_cupons: list | None = None

        # Call details
        self.call_uuid = profile_data.get("CALL_UUID", None)
        self.call_operator = profile_data.get("CALL_OPERATOR", None)

        # Informacion del gestor CRM
        self.page_number: int = None

        if self.available_discount_coupon:
            self.available_discount_cupons = [
                DiscountCoupon(
                    profile_data.get("ID del cupón"),
                    profile_data.get("Nombre del cupón"),
                    profile_data.get("Tipo de cupón"),
                    profile_data.get("Importe del cupón"),
                    profile_data.get("Estado de uso"),
                    profile_data.get("Fecha de validez"),
                    profile_data.get("Condiciones de uso"),
                    profile_data.get("Tiempo de emisión")
                )
            ]

    def _parse_float(self, value: str | None) -> float | None:
        """Intento de conversión robusta para valores numéricos con comas."""
        if not value:
            return None
        try:
            return float(value.replace(",", "").replace("$", ""))
        except:
            return None
        
    def to_dict(self) -> dict:
        local_profile = {
            "UID":self.uid,
            "NAME":self.name,
            "PHONE_NUMBER":self.phone_number,
            "EMAIL":self.email,
            "GENRE":self.genre,
            "TASK":self.task,
            "GROUP_TYPE":self.group_type,
            "CLIENT_BASE":self.client_base,
            "PRODUCT_TYPE":self.product_type,
            "APPLICATION":self.application,
            "TSO":self.tso_id,
            "USER_STATUS":self.user_status,
            "TIME_REGISTRED":self.time_registred,
            "TERM":self.term,
            "RESERVATION":self.reservation,
            "DATE_CITE":self.date_cite,
            "URL_QUERY":self.url_query,
            "AMOUNT_LIMIT":self.amount_limit,
            "AMOUNT_AVAILABLE":self.amount_available,
            "LAST_AMOUNT_TIME_APPROBED":self.last_amount_time_approbed,
            "AMOUNT_LIMIT_INCREMENTED":self.amount_limit_incremented,
            "LAST_AMOUNT_INCREMENT":self.last_amount_increment,
            "INVALIDATE":self.invalidate,
            "TIME_ASSIGNATED":self.time_assignated,
            "CALL_OPERATOR":self.call_operator,
            "CALL_UUID":self.call_uuid,
            "AVAILABLE_DISCOUNT_COUPON":self.available_discount_coupon,
            "AVAILABLE_DISCOUNT_CUPONS":self.available_discount_cupons,
            "CONTACTS_PAGE_NUMBER":self.page_number
        }

        return local_profile