# Library import
import psutil
import win32gui
import win32process
import win32con
import getpass
from typing import List, Dict
import random
import os
import keyboard
import threading
from PyQt5.QtWidgets import QMessageBox, QApplication
import sys
import requests
import hashlib
import winreg
import uuid
import subprocess

# Constants definition
CURRENT_PROCESS_NAME: str = "CRM Manager"
VERIFICATION_PROTOCOL: str = "HTTP"
VERIFICATION_SERVER: str = "unexpelled-naissant-meta.ngrok-free.dev"
VERIFICATION_RESOURCE: str = ""

# Classes definition
class UserProcess:
    def __init__(self,
        name: str,
        pid: str,
        hwnd: int
    ) -> None:
        # Instance property assigment
        self.name = name
        self.pid = pid
        self.hwnd = hwnd
        
        # Instance property definition
        self.visibility: bool = True
    
    # Public methods
    def set_invisible(self) -> bool:
        self.visibility = False
        return True
    
    def set_visible(self) -> bool:
        self.visibility = True
        return True
    
    def is_visible(self) -> bool:
        # Verify the current data
        if not self.hwnd: return False
        if not win32gui.IsWindow(self.hwnd): return False
        
        is_visible = bool(win32gui.IsWindowVisible(self.hwnd))
        self.visibility = is_visible
        return self.visibility
        
class SecurityEngine:
    # General properties definition
    SYSTEM_PROCESS_EXCLUSIONS = (
        "EXPLORER.EXE",
        "TEXTINPUTHOST.EXE",
        "APPLICATIONFRAMEHOST.EXE",
        "SYSTEMSETTINGS.EXE",
        "LOCKAPP.EXE"
    )
    
    HIDE_SHOW_PROCESS_HOTKEY: str = "CTRL+ALT+A"
    STOP_PROCESS_HOTKEY: str = "CTRL+ALT+Q"
    
    def __init__(self) -> None:
        # Instance property definitions
        self.current_managed_process: Dict[int, UserProcess] = {}
        self.PRINCIPAL_UNIT_STORAGE: str = f"{os.environ.get('SystemDrive')}"
        self.CURRENT_USER_SESSION: str = f"{getpass.getuser()}"
        self.KEY: str = ".key"
        self.LICENSE_KEY: str = f"{self.PRINCIPAL_UNIT_STORAGE}\\Users\\{self.CURRENT_USER_SESSION}\\{self.KEY}"

        # Initialize hotkeys listeners
        self._inject_hide_show_hotkey()
        self._inject_stop_processes_hotkey()

        # Initialize security verification
        self._validate_or_exit()
    
    # Private methods
    def __filter_user_process(self, process) -> bool:
        raise NotImplementedError
    
    def __enum_window_callback(self, hwnd, windows):
        # Ventana visible y con texto
        if not win32gui.IsWindowVisible(hwnd):
            return

        title = win32gui.GetWindowText(hwnd)
        if not title or len(title.strip()) < 2:
            return

        # Debe ser una ventana normal
        style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
        if not (style & win32con.WS_OVERLAPPEDWINDOW):
            return

        # Ignorar ventanas hijas
        if win32gui.GetParent(hwnd) != 0:
            return

        windows.append(hwnd)
    
    def __generate_process_id(self) -> int:
        while True:
            new_process_id = random.randint(1, 9999)
            if not new_process_id in self.current_managed_process: return new_process_id 

    def __hotkey_hide_show_daemon(self):
        hk = self.HIDE_SHOW_PROCESS_HOTKEY.lower()

        # Registrar hotkey
        keyboard.add_hotkey(hk, lambda: self.toggle_managed_user_processes())

        # Mantener el hilo esperando
        keyboard.wait()  # Mantiene este hilo activo sin bloquear la app

    def _inject_hide_show_hotkey(self):
        # Verificar si el hilo ya existe y está corriendo
        if hasattr(self, "_hotkey_hide_show_thread"):
            if self._hotkey_hide_show_thread.is_alive():
                return True

        # Crear hilo
        self._hotkey_hide_show_thread = threading.Thread(
            target=self.__hotkey_hide_show_daemon,
            daemon=True
        )
        self._hotkey_hide_show_thread.start()
        return True

    def __hotkey_stop_processes_daemon(self):
        hk = self.STOP_PROCESS_HOTKEY.lower()

        # Registrar hotkey
        keyboard.add_hotkey(hk, lambda: self.stop_managed_user_processes())

        # Mantener hilo escuchando
        keyboard.wait()

    def _inject_stop_processes_hotkey(self) -> bool:
        # Evita crear múltiples hilos duplicados
        if hasattr(self, "__hotkey_stop_processes_thread") and \
        self.__hotkey_stop_processes_thread.is_alive():
            return True

        # Iniciar hilo daemon
        self.__hotkey_stop_processes_thread = threading.Thread(
            target=self.__hotkey_stop_processes_daemon,
            daemon=True
        )
        self.__hotkey_stop_processes_thread.start()
        return True

    def _is_authorized(self) -> bool:
        try:
            response = requests.head(f"{VERIFICATION_PROTOCOL.lower()}://{VERIFICATION_SERVER}/{VERIFICATION_RESOURCE}", allow_redirects=True)

            #r = requests.head(f"{VERIFICATION_PROTOCOL.lower()}://{VERIFICATION_SERVER}/{VERIFICATION_RESOURCE}", timeout=3)
            return response.status_code == 200
        except:
            return False
  
    def _verify_license(self) -> bool:
        return os.path.exists(self.LICENSE_KEY)
    
    def _validate_or_exit(self):
        """
        Llama a is_authorized(). Si retorna False, muestra un mensaje
        fatal y cierra toda la aplicación inmediatamente.
        """
        if self._is_authorized():
            print("Application validated.")
            return True  # Todo OK, continuar ejecución

        # Crear mensaje de error modal
        msg = QMessageBox()
        msg.setWindowTitle("Acceso denegado")
        msg.setText(
            "❌ No se pudo validar la autorización de esta aplicación.\n"
            "El acceso ha sido bloqueado."
        )
        msg.setIcon(QMessageBox.Critical)
        msg.setStandardButtons(QMessageBox.Ok)

        msg.exec_()  # Mostrar la ventana

        # Cerrar completamente la aplicación
        QApplication.quit()
        sys.exit(0)  # Por si acaso

        return False
    
    # Public methods
    def append_managed_process(self, process: UserProcess) -> int:
        process_id = self.__generate_process_id()
        self.current_managed_process[process_id] = process
        return process_id
    
    def delete_managed_process(self, process_id: int) -> bool:
        if not process_id in self.current_managed_process: return False
        self.current_managed_process.pop(process_id)
        return True
    
    def get_current_user_process(self) -> List[UserProcess]:
        current_user = getpass.getuser()
        all_process = []
        windows = []

        # Obtener todas las ventanas visibles
        win32gui.EnumWindows(self.__enum_window_callback, windows)

        seen_pids = set()

        for hwnd in windows:
            try:
                # Obtener PID asociado a la ventana
                _, pid = win32process.GetWindowThreadProcessId(hwnd)

                # Evitar repetir procesos si tienen múltiples ventanas
                if pid in seen_pids:
                    continue
                seen_pids.add(pid)

                # Obtener información del proceso
                process = psutil.Process(pid)

                # Validar usuario propietario
                process_user = process.username().split('\\')[-1]
                if process_user.lower() != current_user.lower():
                    continue

                # Filtro de procesos del sistema
                if process.name().upper() in self.SYSTEM_PROCESS_EXCLUSIONS:
                    continue

                # Crear objeto UserProcess con hwnd incluido
                if pid == os.getpid():
                    process_name = CURRENT_PROCESS_NAME
                else:
                    process_name = process.name()
                
                all_process.append(
                    UserProcess(
                        name=process_name,
                        pid=pid,
                        hwnd=hwnd
                    )
                )

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        return all_process

    def hide_window_process(self, process: UserProcess) -> bool:
        # Validate the user process
        if not win32gui.IsWindow(process.hwnd): return False
        if not process.hwnd: return False
        
        try:
            win32gui.ShowWindow(process.hwnd, 0)
            
            process.set_invisible()
            
            return True
        except:
            return False    
    
    def show_window_process(self, process: UserProcess) -> bool:
        # Verify the user process
        if not win32gui.IsWindow(process.hwnd): return False
        if not process.hwnd: return False
        
        try:
            # Mostrar sin robar foco
            SW_SHOWNOACTIVATE = 4
            win32gui.ShowWindow(process.hwnd, SW_SHOWNOACTIVATE)

            # Mover ventana al frente sin activarla
            win32gui.SetWindowPos(
                process.hwnd,
                win32con.HWND_TOP,
                0, 0, 0, 0,
                win32con.SWP_NOMOVE |
                win32con.SWP_NOSIZE |
                win32con.SWP_NOACTIVATE
            )
            return True
        except:
            return False
            
    def toggle_managed_user_processes(self) -> bool:
        if len(self.current_managed_process) == 0: return False
        
        any_visible = any(process.is_visible() for process in self.current_managed_process.values())
        
        try:
            for process in self.current_managed_process.values():
                if any_visible:
                    self.hide_window_process(process)
                else:
                    self.show_window_process(process)
            
            return True
        except:
            return False

    def cleanup_invalid_processes(self):
        """
        Elimina de current_managed_process cualquier proceso cuyo hwnd ya no exista.
        """
        to_delete = []
        for pid, proc in self.current_managed_process.items():
            if not win32gui.IsWindow(proc.hwnd):
                to_delete.append(pid)

        for pid in to_delete:
            self.current_managed_process.pop(pid)
    
    def stop_managed_user_processes(self) -> bool:
        if len(self.current_managed_process) == 0:
            return False

        try:
            to_delete = []

            for process_id, user_process in self.current_managed_process.items():
                try:
                    # psutil para matar el proceso
                    proc = psutil.Process(user_process.pid)
                    proc.kill()  # Terminación inmediata
                    to_delete.append(process_id)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    # Si no se puede matar, simplemente lo eliminamos del registro
                    to_delete.append(process_id)
                    continue

            # Limpiar del registro interno
            for pid in to_delete:
                self.current_managed_process.pop(pid, None)

            return True
        except:
            return False
        
    def _get_machine_guid(self):
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Cryptography")
            value, _ = winreg.QueryValueEx(key, "MachineGuid")
            return value
        except Exception:
            return None

    def _get_bios_serial(self):
        try:
            # usa wmic (puede requerir permisos)
            out = subprocess.check_output(["wmic", "bios", "get", "serialnumber"], stderr=subprocess.DEVNULL, text=True)
            lines = [l.strip() for l in out.splitlines() if l.strip()]
            if len(lines) >= 2:
                return lines[1]
        except Exception:
            pass
        return None

    def _get_disk_serial(self):
        try:
            out = subprocess.check_output(["wmic", "diskdrive", "get", "serialnumber"], stderr=subprocess.DEVNULL, text=True)
            lines = [l.strip() for l in out.splitlines() if l.strip()]
            if len(lines) >= 2:
                return lines[1]
        except Exception:
            pass
        return None

    def get_device_id(self):
        parts = []
        mg = self._get_machine_guid()
        if mg: parts.append(mg)
        bios = self._get_bios_serial()
        if bios: parts.append(bios)
        disk = self._get_disk_serial()
        if disk: parts.append(disk)
        # fallback: hostname + MAC
        parts.append(uuid.getnode().to_bytes(6, 'big').hex())
        raw = "|".join(parts)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()