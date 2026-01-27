import time
from threading import Thread

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QFrame, QHBoxLayout
)
from PyQt5.QtCore import QObject, pyqtSignal, Qt

from ...core.interfaces import FunctionInterface


# --------------------------
# EMISORES DE SEÑALES
# --------------------------
class BrowserStatusEmitter(QObject):
    status_changed = pyqtSignal(bool)


class SessionStatusEmitter(QObject):
    session_changed = pyqtSignal(bool)


class OpenCRMFunction(FunctionInterface):

    function_name = "Open/close CRM"
    function_description = "Control del navegador CRM"

    def __init__(self, parent_module):
        super().__init__(parent_module)

        self._emitter = BrowserStatusEmitter()
        self._session_emitter = SessionStatusEmitter()
        self.browser_driver = None
        self.auto_login_enabled = False
        self.parent_module = parent_module

        self.widget = QWidget()
        self._setup_widget()

        # Conectar señales
        self._emitter.status_changed.connect(self._update_status_ui)
        self._session_emitter.session_changed.connect(self._update_session_ui)

        # Iniciar thread de actualización de sesión
        Thread(target=self._update_session_status_loop, daemon=True).start()

    # ============================================================
    # SETUP DE WIDGET
    # ============================================================
    def _setup_widget(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)

        # --------------------------
        # TARJETA PRINCIPAL
        # --------------------------
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #1e1f22;
                border-radius: 12px;
                padding: 20px;
            }
        """)
        c = QVBoxLayout()
        c.setSpacing(14)

        # --------------------------
        # TÍTULO
        # --------------------------
        title = QLabel("Gestor CRM")
        title.setStyleSheet("""
            font-size: 20px;
            font-weight: 600;
            color: #F5F7FA;
        """)
        c.addWidget(title)

        # --------------------------
        # DESCRIPCIÓN
        # --------------------------
        desc = QLabel(self.function_description)
        desc.setStyleSheet("""
            font-size: 13px;
            color: #BFC9D9;
        """)
        c.addWidget(desc)

        # --------------------------
        # ESTADO
        # --------------------------
        status_row = QHBoxLayout()
        lbl = QLabel("Estado:")
        lbl.setStyleSheet("color: #E6EEF6; font-size: 14px;")

        self.label_status = QLabel("Desconectado")
        self.label_status.setAlignment(Qt.AlignCenter)
        self.label_status.setStyleSheet("""
            QLabel {
                background-color: #AA0000;
                color: white;
                padding: 8px 14px;
                border-radius: 8px;
                font-weight: bold;
            }
        """)

        status_row.addWidget(lbl)
        status_row.addWidget(self.label_status)
        c.addLayout(status_row)

        # --------------------------
        # BOTÓN DE SESIÓN
        # --------------------------
        session_row = QHBoxLayout()
        session_row.addWidget(QLabel("Sesión:"))
        self.btn_session_status = QPushButton("No iniciada")
        self.btn_session_status.setEnabled(False)
        self.btn_session_status.setStyleSheet("""
            QPushButton {
                background-color: #2C2F36;
                color: #FFFFFF;
                border-radius: 8px;
                padding: 8px 14px;
                font-weight: bold;
            }
        """)
        session_row.addWidget(self.btn_session_status)
        c.addLayout(session_row)

        # --------------------------
        # BOTÓN DE AUTOLOGIN
        # --------------------------
        autologin_row = QHBoxLayout()
        autologin_row.addWidget(QLabel("Auto-login:"))

        self.btn_auto_login = QPushButton("Desactivado")
        self.btn_auto_login.setCheckable(True)
        self.btn_auto_login.setStyleSheet("""
            QPushButton {
                background-color: #AA0000;
                color: white;
                border-radius: 8px;
                padding: 8px 14px;
                font-weight: bold;
            }
        """)
        self.btn_auto_login.clicked.connect(self._toggle_auto_login)
        autologin_row.addWidget(self.btn_auto_login)
        c.addLayout(autologin_row)

        # --------------------------
        # BOTONES PRINCIPALES
        # --------------------------
        btn_row = QHBoxLayout()

        btn_open = QPushButton("Abrir CRM")
        btn_open.setCursor(Qt.PointingHandCursor)
        btn_open.setStyleSheet("""
            QPushButton {
                background-color: #0d6efd;
                color: white;
                border-radius: 8px;
                padding: 10px 18px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #0d6efd;
            }
            QPushButton:pressed {
                background-color: #0b5cd5;
            }
        """)
        btn_open.clicked.connect(lambda: self._open_crm())
        btn_row.addWidget(btn_open)

        btn_close = QPushButton("Cerrar CRM")
        btn_close.setCursor(Qt.PointingHandCursor)
        btn_close.setStyleSheet("""
            QPushButton {
                background-color: #D9534F;
                color: white;
                border-radius: 8px;
                padding: 10px 18px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #E06A67;
            }
            QPushButton:pressed {
                background-color: #C64542;
            }
        """)
        btn_close.clicked.connect(self._close_crm)
        btn_row.addWidget(btn_close)

        c.addLayout(btn_row)

        # --------------------------
        # CERRAR CARD
        # --------------------------
        card.setLayout(c)
        layout.addWidget(card)
        self.widget.setLayout(layout)

    # ============================================================
    # TOGGLE AUTOLOGIN
    # ============================================================
    def _toggle_auto_login(self):
        self.auto_login_enabled = not self.auto_login_enabled
        if self.auto_login_enabled:
            self.btn_auto_login.setText("Activado")
            self.btn_auto_login.setStyleSheet("""
                QPushButton {
                    background-color: #1DB954;
                    color: white;
                    border-radius: 8px;
                    padding: 8px 14px;
                    font-weight: bold;
                }
            """)
        else:
            self.btn_auto_login.setText("Desactivado")
            self.btn_auto_login.setStyleSheet("""
                QPushButton {
                    background-color: #AA0000;
                    color: white;
                    border-radius: 8px;
                    padding: 8px 14px;
                    font-weight: bold;
                }
            """)

    # ============================================================
    # LOOP DE ACTUALIZACIÓN DE SESIÓN
    # ============================================================
    def _update_session_status_loop(self):
        while True:
            try:
                session_active = not self.parent_module.admin_website.get_page("login").is_current_page()
            except:
                session_active = False

            self._session_emitter.session_changed.emit(session_active)
            time.sleep(1)

    # ============================================================
    # ACTUALIZAR UI BOTÓN SESIÓN
    # ============================================================
    def _update_session_ui(self, active):
        if active:
            self.btn_session_status.setText("Iniciada")
            self.btn_session_status.setStyleSheet("""
                QPushButton {
                    background-color: #1DB954;
                    color: white;
                    border-radius: 8px;
                    padding: 8px 14px;
                    font-weight: bold;
                }
            """)
        else:
            self.btn_session_status.setText("No iniciada")
            self.btn_session_status.setStyleSheet("""
                QPushButton {
                    background-color: #AA0000;
                    color: white;
                    border-radius: 8px;
                    padding: 8px 14px;
                    font-weight: bold;
                }
            """)

    # ============================================================
    # RESTO DEL CÓDIGO (SIN CAMBIOS)
    # ============================================================
    def get_widget(self):
        return self.widget

    def _open_crm(self):
        print("[OpenCRM] Abriendo navegador CRM...")
        Thread(target=self._open_crm_background, daemon=True).start()

    def _open_crm_background(self):
        try:
            webbrowser = self.parent_module.engine.website.webbrowser
            initial_url = self.parent_module.admin_website.get_page("login").url
            print("INITIAL URL:", initial_url)
            webbrowser.open_browser(headless=False, initial_url=initial_url)
            
            # Verify auto-login function
            if self.auto_login_enabled:
                credentials = self.parent_module.engine.get_user_profile()
                
                if credentials:
                    self.parent_module.admin_website.get_page("login").login(
                        username=credentials.get("USERNAME"),
                        password=credentials.get("PASSWORD")
                    )
                else:
                    self.parent_module.engine.logger.error("Tried to auto-login in the CRM website, but we cant recover the user credentials")
            
            # Inject keyboard hotkeys
            self.parent_module.engine.website.get_page("homeuser").inject_hangup_hotkey()
            self.parent_module.engine.website.get_page("homeuser").inject_call_hotkey()

            self.browser_driver = webbrowser.driver
            self._emitter.status_changed.emit(True)
            Thread(target=self._watch_browser, daemon=True).start()
        except Exception as e:
            print("[OpenCRM] Error:", e)
            self._emitter.status_changed.emit(False)

    def _watch_browser(self):
        print("[WATCHER] Monitoreando navegador CRM...")
        driver = self.browser_driver
        if not driver:
            return
        try:
            while True:
                try:
                    _ = driver.title
                except Exception:
                    print("[WATCHER] CRM cerrado")
                    self._emitter.status_changed.emit(False)
                    return
                time.sleep(1)
        except:
            self._emitter.status_changed.emit(False)

    def _close_crm(self):
        try:
            if self.parent_module.engine.website.webbrowser:
                self.parent_module.engine.website.webbrowser.close_browser()
        except:
            pass
        self.browser_driver = None
        self._emitter.status_changed.emit(False)

    def _update_status_ui(self, connected):
        if connected:
            self.label_status.setText("Conectado")
            self.label_status.setAlignment(Qt.AlignCenter)
            self.label_status.setStyleSheet("""
                QLabel {
                    background-color: #1DB954;
                    color: white;
                    padding: 8px 14px;
                    border-radius: 8px;
                    font-weight: bold;
                    text-align: center;
                }
            """)
        else:
            self.label_status.setText("Desconectado")
            self.label_status.setAlignment(Qt.AlignCenter)
            self.label_status.setStyleSheet("""
                QLabel {
                    background-color: #AA0000;
                    color: white;
                    padding: 8px 14px;
                    border-radius: 8px;
                    font-weight: bold;
                    text-align: center;
                }
            """)

    def execute(self):
        pass
