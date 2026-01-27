# Library import
import os
import json
from datetime import datetime, timezone
import copy
import time
import threading

# Classes definition
class StorageCenter:
    # General property definition
    CLIENT_INFORMATION_STATUS: tuple = ("PARTIAL", "COMPLETE")
    
    def __init__(self,
        root_path: str,
        folder_name: str
    ) -> None:
        # Instance property definition
        self.root_path = os.path.abspath(root_path)
        self.folder_name = folder_name
        self.file_contact_extension = "json"
        
        # Initialize base folder
        if not self.__initialize_base_folder():
            raise RuntimeError("Could not initialize storage center base folder")
    
    def __initialize_base_folder(self) -> bool:
        print("Storage center full path:", self.base_full_path)
        if os.path.exists(self.base_full_path):
            return True
        else:
            try:
                os.mkdir(self.base_full_path)
                
                return os.path.exists(self.base_full_path)
            except Exception as Error:
                return False
    
    @property
    def base_full_path(self) -> str:
        return f"{self.root_path}/{self.folder_name}"
    
    def get_contact_filepath(self, uid: str) -> str:
        return self.base_full_path + f"/{uid}.{self.file_contact_extension}"

    def contact_exists(self, uid: str) -> bool:
        if os.path.exists(self.get_contact_filepath(uid)):
            return True
        else:
            return False
    
    def get_contact_status(self, uid: str) -> str | None:
        if self.contact_exists(uid):
            try:
                with open(self.get_contact_filepath(uid), "r") as file:
                    contact_profile = json.load(file)
                    return contact_profile.get("status", None)
            except:
                return None
        else:
            return None

    def query_contacts(self) -> list:
        all_contacts = os.listdir(self.base_full_path)
        contacts = []
        
        for contact_file in all_contacts:
            # Extract the file name (client UID)
            contact_uid, file_extension = os.path.splitext(contact_file)
            
            # Filter the contact information files
            if file_extension == ".json":
                # Save the file contact
                contacts.append(contact_uid)
        
        # Return results
        return contacts

    def get_contact(self, uid: str) -> dict | None:
        if self.contact_exists(uid):
            with open(self.get_contact_filepath(uid), "r") as file:
                return json.load(file)
            
            return None
        else:
            return None
    
    def _save_contact(self, uid: str, contact_data: dict, status: str) -> bool:
        if status not in self.CLIENT_INFORMATION_STATUS:
            raise ValueError("Invalid status value")
        
        try:
            with open(self.get_contact_filepath(uid), "w") as file:
                contact_profile = {
                    "uid":uid, 
                    "status":status,
                    "last_updated":datetime.now(timezone.utc).isoformat(),
                    "data":copy.deepcopy(contact_data)
                }
                
                print(f"Creating contact: UID: {uid} - Status: {status}")
                json.dump(contact_profile, file, indent=4, separators=(",",":"), ensure_ascii=True)
            return True
        except Exception as e:
            return False
    
    def initialize_contact(self, uid: str, contact_data: dict) -> bool:
        # Verify the current contact existence
        if self.contact_exists(uid):
            # Verify the current contact status
            if self.get_contact_status(uid) == "COMPLETE":
                return False
        
        return self._save_contact(uid, contact_data, status="PARTIAL")

    def complete_contact(self, uid: str, contact_data: dict) -> bool:
        # Verify the current contact existence
        if self.contact_exists(uid):
            # Verify the current contact status
            if self.get_contact_status(uid) == "COMPLETE":
                return False
        
        return self._save_contact(uid, contact_data, status="COMPLETE") 
    
class PassiveCapture:
    def __init__(self,
        admin_website: object,
        user_website: object,
        storage_center: StorageCenter
    ) -> None:
        # Instance property definition
        self.monitor_status: bool = False
        self.monitor_process: object = None
        
        # Instance property assignment
        self.admin_website = admin_website
        self.user_website = user_website
        self.storage_center = storage_center
    
    def _inject_monitor(self, use_javascript: bool = True) -> bool:
        if use_javascript:
            javascript_code = """
(function () {

    // Namespace persistente
    if (window.CaptureEngine) {
        return window.CaptureEngine.monitorId || true;
    }

    window.CaptureEngine = {};

    window.CaptureEngine.initializeBufferStorage = function () {
        if (!sessionStorage.getItem("CaptureBuffer")) {
            sessionStorage.setItem("CaptureBuffer", JSON.stringify({}));
        }
        return true;
    };

    window.CaptureEngine.identifyContact = function () {
        return document.getElementById("outboundCallConsole") !== null;
    };

    window.CaptureEngine.getContactData = function () {
        const contactConsoleFrame = document.getElementById("outboundCallConsole");
        if (!contactConsoleFrame || !contactConsoleFrame.contentDocument) {
            return null;
        }

        const contactDataFrame =
            contactConsoleFrame.contentDocument.getElementById("contactsConsole");

        if (!contactDataFrame || !contactDataFrame.contentDocument) {
            return null;
        }

        const keys = contactDataFrame.contentDocument.querySelectorAll(
            "div.el-form-item__label"
        );
        const values = contactDataFrame.contentDocument.querySelectorAll(
            "div.el-form-item__content"
        );

        const contactData = {};
        const length = Math.min(keys.length, values.length);

        for (let i = 0; i < length; i++) {
            const key = keys[i].textContent.trim().replace(":", "");
            const value = values[i].textContent.trim();
            contactData[key] = value;
        }

        return contactData;
    };

    window.CaptureEngine.getCaptureBuffer = function () {
        window.CaptureEngine.initializeBufferStorage();
        return JSON.parse(sessionStorage.getItem("CaptureBuffer"));
    };

    window.CaptureEngine.setBufferStorage = function (buffer) {
        sessionStorage.setItem("CaptureBuffer", JSON.stringify(buffer));
    };

    window.CaptureEngine.saveContactData = function (contactData) {
        if (!contactData || typeof contactData !== "object") return false;

        const uid = contactData["UID"];
        if (!uid) return false;

        const buffer = window.CaptureEngine.getCaptureBuffer();
        if (buffer[uid]) return false;

        buffer[uid] = contactData;
        window.CaptureEngine.setBufferStorage(buffer);
        return true;
    };

    window.CaptureEngine.backgroundContactWatcher = function () {
        try {
            if (!window.CaptureEngine.identifyContact()) return;

            const contactData = window.CaptureEngine.getContactData();
            if (!contactData || !contactData["UID"]) return;

            window.CaptureEngine.saveContactData(contactData);
        } catch (error) {
            console.error("CaptureEngine error:", error);
        }
    };

    window.CaptureEngine.startContactMonitoring = function (intervalMs = 1000) {
        if (window.CaptureEngine.monitorId) {
            return window.CaptureEngine.monitorId;
        }

        window.CaptureEngine.monitorId =
            setInterval(window.CaptureEngine.backgroundContactWatcher, intervalMs);

        return window.CaptureEngine.monitorId;
    };

    window.CaptureEngine.stopContactMonitoring = function () {
        if (!window.CaptureEngine.monitorId) return true;

        clearInterval(window.CaptureEngine.monitorId);
        delete window.CaptureEngine.monitorId;
        return true;
    };

    window.CaptureEngine.emptyCaptureBuffer = function () {
        sessionStorage.removeItem("CaptureBuffer");
        window.CaptureEngine.initializeBufferStorage();
        return true;
    };

    // Auto-inicio del monitor
    return window.CaptureEngine.startContactMonitoring(1000);

})();
"""            
            execution_result = self.user_website.webbrowser.execute_javascript(javascript_code)
            print("[INFO] Inject monitor result:", execution_result)
            return True
        else:
            raise NotImplementedError

    def _recolect_buffer(self, use_javascript: bool = True) -> list:
        if use_javascript:
            javascript_code = """return window.CaptureEngine.getCaptureBuffer();"""
            
            execution_result = self.user_website.webbrowser.execute_javascript(javascript_code)
            return execution_result
        else:
            raise NotImplementedError
    
    def _empty_buffer(self, use_javascript: bool = True) -> bool:
        if use_javascript:
            javascript_code = """return window.CaptureEngine.emptyCaptureBuffer();"""
            
            execution_result = self.user_website.webbrowser.execute_javascript(javascript_code)
            return execution_result
        else:
            raise NotImplementedError

    def _monitor_new_clients(self) -> None:
        # Wait until the website is available
        print("Launching the clients monitor on background...")
        while True:
            time.sleep(3)
            
            # Verify that the user is logged in
            try:
                #session_inactive = self.admin_website.get_page("login").is_current_page()
                session_inactive = self.user_website.identify_current_page() is None
            except:
                session_inactive = True
                
            #("Session active:", session_active)
            if session_inactive: continue
            else:
                # Start the navegator JavaScript capture monitoring process                
                # Inject the monitor status
                if not self._inject_monitor(): raise RuntimeError("Could not inject monitor script")
                                
                # Update the monitor status
                self.monitor_status = True

                break
        
        time.sleep(3)
        while self.monitor_status:
            # Temporal wait
            time.sleep(1)
            
            # Recolect buffer data
            buffer_data = self._recolect_buffer()
            
            if len(buffer_data) == 0: continue
            
            print("New clients recolected:")
            for UID in buffer_data:
                print(f" - {UID}")
                
                if not self.storage_center.contact_exists(UID):
                    contact_data = buffer_data[UID]
                    self.storage_center.initialize_contact(UID, contact_data)
                    print(f"   -> Contact {UID} initialized in storage center")
                else:
                    print(f"    -> Contact: {UID} already exists in storage center")
                    continue
            
            # Clean the capture buffer
            print("Cleaning capture buffer...")
            self._empty_buffer()
            
            pass

        # Return results
        return None
    
    def start(self) -> bool:
        print("Starting the Passive Capture mechanism...")
        # Verify the current monitor status
        if self.monitor_status: return True
                
        # Launch the buffer monitoring thread
        monitor_thread = threading.Thread(
            target=self._monitor_new_clients,
            daemon=True
        )
        monitor_thread.start()
        
        # Update the monitor process thread
        self.monitor_process = monitor_thread
        
        # Return results
        return True
    
    def stop(self) -> bool:
        # Stop the monitor JavaScript thread
        javascript_code = """return window.CaptureEngine.stopContactMonitoring();"""
        execution_result = self.user_website.webbrowser.execute_javascript(javascript_code)
        
        if not execution_result: raise RuntimeError("Could not stop contact monitoring JavaScript script")
        
        # Update the monitor status
        self.monitor_status = False
        
        # Wait for the monitor process to finish
        if self.monitor_process and self.monitor_process.is_alive():
            self.monitor_process.join()
        
        # Return results
        return True

class ActiveCapture:
    def __init__(self,
        admin_website: object,
        user_website: object,
        storage_center: object
    ) -> None:
        # Instance property definition
        self.monitor_status: bool = False
        
        self.execution_temporizer: int = 1800 # Represented in seconds
        self.execution_interval: int = 1800 # Represented in seconds
        self.minimum_contacts_threshold: int = 1
        self._last_execution_timestamp: float = 0.0
        
        self.current_execution_process: bool = False
        self.execution_routine_thread: object = None
        
        # Instance property assignment
        self.admin_website = admin_website
        self.user_website = user_website
        self.storage_center = storage_center
    
    def _evaluate_extraction_conditions(self) -> bool:
        if self._count_partial_contacts() >= self.minimum_contacts_threshold:
            return True
        
        if (time.time() - self._last_execution_timestamp) >= self.execution_interval:
            return True
        
        # Return negative
        return False
    
    def _count_partial_contacts(self) -> int:
        count = 0
        all_contacts = self.storage_center.query_contacts()
        
        for contact_uid in all_contacts:
            contact_status = self.storage_center.get_contact_status(contact_uid)
            if contact_status == "PARTIAL":
                count += 1
        
        # Return results
        return count

    def _identify_new_contacts(self) -> list:
        # Go to the main page -> call menu
        if not self.user_website.get_page("homeuser").go_to_callmenu_page():
            print(f"[ERROR] Error going to the call menu page")
            return []
        
        # Go to the "all contacts" list page
        if not self.user_website.get_page("bussinessummary").go_to_all_contacts_menu():
            print(f"[ERROR] Error going to the all contacts menu")
            return []
        
        # Identify the current page
        timewait_limit = 10
        initial_time = time.time()
        while not self.user_website.get_page("totalcontacts").is_loaded:        
            if time.time() - initial_time >= timewait_limit:
                print(f"[ERROR] Time limit expired")
                return []
            
            time.sleep(1)
        
        # Query the initial and last page
        initial_page = self.user_website.get_page("totalcontacts").identify_current_page_number()
        last_page = self.user_website.get_page("totalcontacts").query_last_menu_page()
        
        # Validate the extracted values
        if not initial_page or not last_page:
            print(f"[ERROR] Error getting the initial/last page")
            return []
        
        # Storage of new clients detected
        new_clients = {}
        
        # Process every contact page
        for page in tuple(range(initial_page, last_page + 1)):
            # Query the contacts on the current page
            current_page_contacts = self.user_website.get_page("totalcontacts").get_contacts()
            
            # Verify the query result
            if not current_page_contacts:
                print(f"[ERROR] We cant get the current page contacts")
                return list(new_clients.values())
            
            # Process every contact per page
            for contact in current_page_contacts:
                # Verify if the contact already exists
                if self.storage_center.contact_exists(contact.uid):
                    # Verify the current contact status
                    if self.storage_center.get_contact_status(contact.uid) == "COMPLETE": continue
                    
                    # Append the new contact (existent, but partial)
                    new_clients[contact.uid] = contact
                else:
                    # Append the new contact (not exists)
                    new_clients[contact.uid] = contact
            
            # Verify the current page
            if page >= last_page: break
            
            # Go to the next page
            if not self.user_website.get_page("totalcontacts").go_to_next_page():
                print("[ERROR] Could not go to the next page")
                break
        
        # Return results
        return list(new_clients.values())

    def _extract_new_clients(self, contacts: list) -> list:
        # Process every new contact
        contacts_extracted = []
        
        for contact in contacts:
            # Verify the current contact existence
            if self.storage_center.contact_exists(contact.uid):
                # Verify the current contact status
                if self.storage_center.get_contact_status(contact.uid) == "COMPLETE": continue
                
                # Try to get the contact information
                contact_complete_profile = self.user_website.get_page("totalcontacts").get_contact(contact)
                
                # Verify the query sucess
                if not contact_complete_profile: print(f"[ERROR] Error getting the contact information"); continue
                
                # Save the contact information
                self.storage_center.complete_contact(contact.uid, contact_complete_profile)
                
                # Append the new contact extracted
                contacts_extracted.append(contact)
            else:
                # Try to get the contact information
                contact_complete_profile = self.user_website.get_page("totalcontacts").get_contact(contact)
                
                # Verify the query sucess
                if not contact_complete_profile: print(f"[ERROR] Error getting the contact information"); continue
                
                # Save the contact information
                self.storage_center.complete_contact(contact.uid, contact_complete_profile)
                
                # Append the new contact extracted
                contacts_extracted.append(contact)
        
        # Return results
        return contacts_extracted 

    def _execution_routine(self) -> None:
        # Pending contacts buffer
        pending_new_contacts = []
        
        while self.monitor_status:
            # Time wait execution
            time.sleep(3)
            
            # Validate the extraction conditions
            if not self._evaluate_extraction_conditions(): continue
            
            # Update the last execution timestamp
            self._last_execution_timestamp = time.time()
            
            # Identify new contacts
            new_contacts_identified = self._identify_new_contacts()
            
            # Save on buffer the new contacts
            for contact in new_contacts_identified:
                # Append (if not exists) the new contact to the pending buffer
                if not contact.uid in pending_new_contacts: pending_new_contacts.append(contact.uid)
                
            # Extract the new contacts identified
            contacts_sucessfully_extracted = self._extract_new_contacts(pending_new_contacts)
            
            # Delete all the contacts processed sucessfully
            for contact in contacts_sucessfully_extracted:
                if contact.uid in pending_new_contacts: pending_new_contacts.remove(contact.uid)
            

            # Repeat process
            continue
        
        # Return results
        return None
    
    def start(self) -> bool:
        print("Active Capture: Starting the active capture mechanism...")
        
        # Create the execution routine thread
        execution_routine_thread = threading.Thread(
            target=self._execution_routine,
            daemon=True
        )
        
        # Launch the execution routine thread
        execution_routine_thread.start()
        
        # Assign the execution routine thread to the instance property
        self.execution_routine_thread = execution_routine_thread
        
        # Enable the monitor status
        self.monitor_status = True
        
        # Return results
        return True
    
    def stop(self) -> bool:
        # Disable the monitor status
        self.monitor_status = False
        
        # Return results
        return True
    
class CaptureEngine:
    def __init__(self,
        root_path: str,
        folder_name: str,
        admin_website: object,
        user_website: object
    ) -> None:
        # Instance property assignment
        self.storage_center = StorageCenter(
            root_path=root_path,
            folder_name=folder_name
        )
        self.admin_website = admin_website
        self.user_website = user_website
        self.passive_capture = PassiveCapture(
            admin_website=self.admin_website,
            user_website=self.user_website,
            storage_center=self.storage_center
        )
        self.active_capture = ActiveCapture(
            admin_website=self.admin_website,
            user_website=self.user_website,
            storage_center=self.storage_center
        )
        
        #print("All existing contacts:")
        #print(self.storage_center.query_contacts())
    
    def start(self) -> bool:
        # Start the passive capture engine
        self.passive_capture.start()
        self.active_capture.start()
        print("ALL PARTIAL CONTACTS:", self.active_capture._count_partial_contacts())
        
        # Return results
        return True
    
    def stop(self) -> bool:
        # Stop the capture mechanism
        #self.passive_capture.stop()
        #self.active_capture.stop()
        
        # Return results
        return True