# Library import
import time
import sqlite3
import os
from datetime import datetime

# Classes definition
class CallLogDataBase:
    def __init__(self, resource_root: str) -> None:
        # Property assigment
        self.resource_root = resource_root

        # Property definition
        self.database_name: str = datetime.now().strftime("Call log [%d-%m-%Y]")
        self.database_extension: str = "db"
        self.database_file = self.resource_root + os.extsep.join([self.database_name, self.database_extension])

        self.database_file = self.database_file.replace("%D", str(time.localtime().tm_mday))
        self.database_file = self.database_file.replace("%M", str(time.localtime().tm_mon))
        self.database_file = self.database_file.replace("%Y", str(time.localtime().tm_year))

        self.database_connection: object = None

    # Private methods    
    def _connect_database(self) -> bool:
        database_connection = sqlite3.connect(self.database_file, check_same_thread=False)

        if database_connection:
            self.database_connection = database_connection

            return True
        else:
            return False

    def _initialize_database(self) -> bool:
        try:
            # Execute the creation sentence
            self.database_connection.execute("""
CREATE TABLE IF NOT EXISTS CONTACTS (
                    UID TEXT PRIMARY KEY,
                    TOTAL_CALLS INTEGER NOT NULL
                );
""")
            # Confirm the changes
            self.database_connection.commit()

            return True
        except sqlite3.Error as error:
            print("[ERROR]", error)
            return False

    # Public methods
    def open_database(self) -> bool:
        # Verify connection
        if not self._connect_database(): return False

        # Initialize the database
        if not self._initialize_database(): return False


        # Return results
        return True

    def close_database(self) -> bool:
        if self.database_connection:
            self.database_connection.close()
            
            return True
        else:
            return False
    
    def log_call(self, UID: str) -> bool:
        try:
            cursor = self.database_connection.execute(
                "UPDATE CONTACTS SET TOTAL_CALLS = TOTAL_CALLS + 1 WHERE UID = ?", 
                (UID,)
            )

# 2. Verificar si se actualizó alguna fila
            if cursor.rowcount == 0:
                # Si no se actualizó, significa que es un nuevo contacto: lo insertamos
                self.database_connection.execute(
                    "INSERT INTO CONTACTS (UID, TOTAL_CALLS) VALUES (?, ?)", 
                    (UID, 1)
                )
                print(f"-> Nuevo contacto '{UID}' registrado con 1 llamada.")
            else:
                print(f"-> Llamada registrada para '{UID}'. Contador incrementado.")
                
            self.database_connection.commit()
            return True
            
        except sqlite3.Error as e:
            print(f"Error al registrar la llamada para {UID}: {e}")
            self.database_connection.rollback() # Deshacer si hubo un error
            return False
    
    def query_total_calls(self, UID: str) -> int | bool:
        try:
            # Usamos el signo de interrogación (?) como placeholder para evitar inyección SQL
            cursor = self.database_connection.execute(
                "SELECT TOTAL_CALLS FROM CONTACTS WHERE UID = ?", 
                (UID,)
            )
            
            # fetchone() recupera la primera (y única) fila que coincida
            registro = cursor.fetchone()
            
            if registro:
                # Como configuramos row_factory = sqlite3.Row, podemos acceder por nombre
                return registro[0]
            else:
                return None
                
        except sqlite3.Error as e:
            print(f"Error al consultar el registro de {UID}: {e}")
            return None
    
    def query_all_contacts(self) -> list:
        try:
            # Ejecutar la consulta para seleccionar UID y TOTAL_CALLS
            cursor = self.database_connection.execute("SELECT UID, TOTAL_CALLS FROM CONTACTS")
            
            # fetchall() recupera una lista de tuplas estándar
            registros_tuplas = cursor.fetchall()
            
            # Mapear la lista de tuplas a una lista de diccionarios manualmente
            registros_dict = []
            for row_tuple in registros_tuplas:
                registros_dict.append({
                    "UID": row_tuple[0],       # El UID está en la posición 0
                    "TOTAL_CALLS": row_tuple[1] # TOTAL_CALLS está en la posición 1
                })
            
            return registros_dict
                
        except sqlite3.Error as e:
            print(f"Error al obtener todos los registros: {e}")
            return None