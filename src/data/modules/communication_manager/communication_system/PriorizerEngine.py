# Library import
import os
import time
import json
import sqlite3
import threading

# Classes definition
class PriorizerDatabase:
    # Class property definition
    class Contact:
        def __init__(self, UID: str, priority_value: int) -> None:
            # Instance property assignment
            self.UID = UID
            self.priority_value = priority_value
    
    def __init__(self, database_file: str, storage_location: str) -> None:
        # Instance property definition
        self.database_file: str = database_file
        self.database_extension: str = "db"
        self.storage_location: str = storage_location
        self.database_controller: object = None
        
    # Property methods definition
    @property
    def database_filepath(self) -> str: return f"{self.storage_location}/{self.database_file}.{self.database_extension}"
    
    # Private methods
    def _load_database(self) -> bool:
        "This method create and load the database file (if not exists), or directly load it"
        raise NotImplementedError
     
    def _initialize_database(self) -> bool:
        "This method initializes the table schema of the database (only if not exists)"
        cursor = self.database_controller.cursor()
        
        TABLE_CREATE: str = """CREATE TABLE IF NOT EXISTS contacts (
            UID TEXT PRIMARY KEY,
            PRIORITY_VALUE INTEGER NOT NULL
        );"""
        
        # Create (if not exists) the data table
        cursor.execute(TABLE_CREATE)
        
        INDEX_CREATE: str = """CREATE INDEX IF NOT EXISTS idx_priority ON contacts (PRIORITY_VALUE DESC);"""
        
        # Create (if not exists) the primary index value
        cursor.execute(INDEX_CREATE)
        
        # Confirm the sentence execution
        self.database_controller.commit()
        
        # Return results
        return True
    
    def _query_contact(self, uid: str) -> int:
        "This method query the priority value for a contact, specified by its UID"
        raise NotImplementedError
    
    def _query_contacts(self, limit: int = -1) -> list:
        "This method query for a specified range of contacts in the database. If its: -1, it returns all the database"
        
        cursor = self.database_controller.cursor()
        
        QUERY_SENTENCE: str = """SELECT UID, PRIORITY_VALUE FROM contacts ORDER BY PRIORITY_VALUE DESC"""
        
        # Verify the contact query limit
        if limit > 0:
            QUERY_SENTENCE += " LIMIT ?;"
            
            # Execute the query sentence
            cursor.execute(QUERY_SENTENCE, (limit,))
        else:
            # execute the query sentence
            cursor.execute(QUERY_SENTENCE)
            
        # Return results
        return cursor.fetchall()
     
    def _append_contact(self, uid: str, priority_value: int) -> bool:
        "This method appends (if not exists) a new contact to the database, with his UID and his priority value"
        try:
            cursor = self.database_controller.cursor()
            
            # Execute the creation contact
            cursor.execute(
                """INSERT OR IGNORE INTO contacts (UID, PRIORITY_VALUE)
                VALUES (?, ?)
                """, (uid, priority_value)
            )
            
            # Confirm the update sentence
            self.database_controller.commit()
            
            # Return results
            return True
        except sqlite3.Error as Error:
            print(f"[ERROR] Integrate contact: {Error}")
            return False
    
    def _delete_contact(self, uid: str) -> bool:
        "This method delete a contact (if exists) from the database"
        cursor = self.database_controller.cursor()
        
        # Execute the delete sentence
        cursor.execute(
            "DELETE FROM contacts WHERE UID = ?;",
            (uid,)
        )
        
        # Confirm the sentence changes
        self.database_controller.commit()
        
        # Return results
        return cursor.rowcount > 0
    
    # Public methods
    def exists(self, UID: str) -> bool:
        "This method search for a specified contact by its UID and return a boolean value if exists or not"
        
        cursor = self.database_controller.cursor()
        
        # Verify the database existence
        cursor.execute(
            """SELECT 1 FROM contacts WHERE UID = ? LIMIT 1;""", (UID,)
        )
        
        # Return results
        return cursor.fetchone() is not None
    
    def integrate_contact(self, UID: str, priority_value: int) -> bool:
        "This method creates a specified contact (if not exists) with his specified priority value"
        return self._append_contact(UID, priority_value)

    def query_contacts(self, limit: int = 50) -> list:
        "This method query for a specified range of contacts in the database"
        return self._query_contacts(limit)
        
    def delete_contact(self, UID: str) -> bool:
        "This method execute a delete sentence for a specified contact by its UID on the database"
        return self._delete_contact(UID)

    def start(self) -> bool:
        "This method starts the sorted contacts database"
        print("Starting the priorizer database...")
        
        try:
            # Create the database connection controller
            self.database_controller = sqlite3.connect(self.database_filepath)
            
            # Initialize the database
            self.database_controller.execute("PRAGMA foreign_keys = ON;")
            
            # Initialize the data table
            self._initialize_database()
            
            # Return results
            return True
        except sqlite3.Error as Error:
            print(f"[ERROR] SQLite database initialize: {Error}")
            return False
    
    def stop(self) -> bool:
        "This method stops the sorted contacts database"
        print("Stopping the priorizer database...")
        
        if self.database_controller:
            self.database_controller.close()
            self.database_controller = None
        
        return True
    
class Priorizer:
    def __init__(self) -> None:
        # Instance property definition
        self.criteria_schema: dict = {
            "AVAILABLE_AMOUNT":{
                "HIGH":(30000, 30),
                "MEDIUM":(16000, 20),
                "LOW":(8000, 10)
            }
        }
        
        self.criteria_functions = [
            self._evaluate_available_amount
        ]
    
    # Private methods
    def _evaluate_available_amount(self, contact_profile: dict) -> int:
        # Get the available amount 
        amount = contact_profile.get("AVAILABLE_AMOUNT", None)
        
        # Verify the get result
        if not amount: return 0
        
        # Evaluate the available amount range value
        for value_range in self.criteria_schema["AVAILABLE_AMOUNT"]:
            value, score = self.criteria_schema["AVAILABLE_AMOUNT"][value_range]
            
            if amount <= value: return score
        
        return self.criteria_schema["AVAILABLE_AMOUNT"]["high"][1]
    
    def evaluate_priority(self, contact_profile: dict) -> int:
        contact_priority = 0
        
        # Execute every criteria function
        for criteria_function in self.criteria_functions:
            contact_priority += criteria_function(contact_profile)
    
        # Return results
        print("Contact priority calculated:", contact_priority)
        
        return contact_priority

class PriorizerEngine:
    def __init__(self, contacts_storage_location: str) -> None:
        # Instance property assignment
        self.contacts_storage_location: str = contacts_storage_location
        
        # Instance property definition
        self.database_file: str = "Contacts priorized"
        self.update_timer: int = 300 # Expressed in seconds
        self.priorizer_database = PriorizerDatabase(self.database_file, self.contacts_storage_location)
        self.priorizer = Priorizer()
        self.status: bool = False
    
    # Private methods
    def _is_contact_file(self, absolute_filepath: str) -> bool:
        file_name, file_extension = os.path.splitext(absolute_filepath)
        
        if not os.path.isfile(absolute_filepath): return False
        if file_extension.upper() != ".JSON": return False
        else: return True 
        
    def _identify_contacts(self) -> list:
        try:
            all_contacts_files = os.listdir(self.contacts_storage_location)
        except:
            return []
        
        # Filter contact files by pattern
        contacts_files_filtered = []
        for file in all_contacts_files:
            absolute_filepath = os.path.join(self.contacts_storage_location, file)
            if self._is_contact_file(absolute_filepath): contacts_files_filtered.append(file)
        
        # Return results
        return contacts_files_filtered
    
    def _get_contacts_files(self, contacts_files: list) -> list:
        contact_profiles = []
        
        # Process every contact file
        for file in contacts_files:
            try:
                absolute_filepath = os.path.join(self.contacts_storage_location, file)
                with open(file=absolute_filepath, mode='r', encoding="UTF-8") as contact_file:
                    contact_profiles.append(
                        json.loads(contact_file.read())
                    )

                    #contact_file.close()
            except Exception as Error:
                print(f"[ERROR]", "On getting contact profile information:", file, "REASON:", Error)
                continue
        
        # Return results
        return contact_profiles

    def _filter_complete_contacts(self, contacts_profiles: list) -> list:
        contacts_filtered = []
        
        # Process every contact to filter it by its status: COMPLETE/PARTIAL
        for contact_profile in contacts_profiles:
            if contact_profile.get("status", None) == "COMPLETE": contacts_filtered.append(contact_profile)
        
        # Return results
        return contacts_filtered
    
    def _updater_routine(self) -> None:
        while self.status:
            time.sleep(3)
            self.update_database()
        
        # Return results
        return None
    
    def update_database(self) -> bool:
        # Identify the current existent contacts
        all_existent_contacts = self._identify_contacts()
        
        print("All existent contacts:", len(all_existent_contacts))
        print(all_existent_contacts)
        
        # Get all the contacts profile
        all_contacts_profiles = self._get_contacts_files(all_existent_contacts)
        
        # Filter all the profiles to get the available contacts
        all_available_contacts = self._filter_complete_contacts(all_contacts_profiles)
        
        print("All available contacts:", len(all_available_contacts))
        print(all_available_contacts)
        
        # Process every contact profile
        for contact_profile in all_available_contacts:
            contact_uid = contact_profile.get("UID")
            
            # Protect verification for security
            if not contact_uid: continue
            
            # Verify if the contact currently exists in the sort database
            if self.priorizer_database.exists(contact_profile.get("UID")): continue
            
            # Calculate the contact priority value
            contact_priority_value = self.priorizer.evaluate_priority(contact_profile)
            
            # Create the new contact log in the database
            create_result = self.priorizer_database.integrate_contact(contact_profile.get("UID"), contact_priority_value)
            
            # Log the creation event
            print(f"[LOG] New contact: {contact_profile.get('UID')}: {contact_priority_value} - CREATION: {create_result}")
            
        # Return results
        return True
    
    def start(self) -> bool:
        # Start the database
        print("Starting the priorizer engine...")
        self.priorizer_database.start()
        
        # Enable the priorizer engine
        self.status = True
        
        # Launch the updater corroutine
        updater_routine = threading.Thread(
            target=self._updater_routine,
            args=[],
            daemon=True
        )
        
        updater_routine.start()
        
        # Return results
        return True
    
    def stop(self) -> bool:
        # Stop the database
        print("Stopping the priorizer engine")
        self.priorizer_database.stop()
        
        # Disable the priorizer engine
        self.status = False
        
        # Return results
        return True