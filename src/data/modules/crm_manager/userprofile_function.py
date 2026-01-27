from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QFrame,
    QHBoxLayout, QLineEdit, QSizePolicy
)
from PyQt5.QtCore import Qt, QTimer
from abc import ABC
from ...core.interfaces import FunctionInterface, ProcessInterface  # Ajusta import según tu estructura


class UserProfileFunction(FunctionInterface, ABC):

    function_name = "User Profile Management"

    def __init__(self, parent_module):
        super().__init__(parent_module)

        self._update_timer = QTimer()
        self._update_timer.setInterval(500)

        self.widget = QWidget()
        self._setup_ui()

        self._update_timer.timeout.connect(self._refresh_ui_status)
        self._update_timer.start()

    # -----------------------------
    # SETUP UI
    # -----------------------------
    def _setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignTop)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Card principal
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #1e1f22;
                border-radius: 14px;
                padding: 20px;
            }
        """)
        card_layout = QVBoxLayout()
        card_layout.setSpacing(15)

        # Título
        title = QLabel("Gestión de Perfil de Usuario")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: white;")
        card_layout.addWidget(title)

        # Descripción
        desc = QLabel("Visualiza tu perfil actual, crea un perfil nuevo o actualiza el existente.")
        desc.setStyleSheet("font-size: 13px; color: #C7C7C7;")
        desc.setWordWrap(True)
        card_layout.addWidget(desc)

        # Campos de usuario y contraseña
        self.username_label = QLabel("Usuario: -")
        self._style_field_label(self.username_label)
        card_layout.addWidget(self.username_label)

        self.password_label = QLabel("Contraseña: -")
        self._style_field_label(self.password_label)
        card_layout.addWidget(self.password_label)

        # Botones Crear / Actualizar
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.btn_create = QPushButton("Crear perfil")
        self._style_button(self.btn_create, "#0E639C", "#0B4F8C")
        self.btn_create.clicked.connect(lambda: self._toggle_profile_panel(show=True, create=True))
        btn_layout.addWidget(self.btn_create)

        self.btn_update = QPushButton("Actualizar perfil")
        self._style_button(self.btn_update, "#6c757d", "#6c757d")  # gris inicial
        self.btn_update.clicked.connect(lambda: self._toggle_profile_panel(show=True, create=False))
        btn_layout.addWidget(self.btn_update)

        card_layout.addLayout(btn_layout)

        # Panel integrado para crear/actualizar perfil (invisible inicialmente)
        self.profile_panel = QFrame()
        self.profile_panel.setStyleSheet("""
            QFrame {
                background-color: #2C2F36;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        self.profile_panel.setVisible(False)
        profile_layout = QVBoxLayout()
        profile_layout.setSpacing(10)

        # Texto instructivo
        profile_label = QLabel("Perfil del CRM")
        profile_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #FFFFFF;")
        profile_layout.addWidget(profile_label)

        # Inputs
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Usuario")
        self.username_input.setStyleSheet(self._input_style())
        profile_layout.addWidget(self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Contraseña")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet(self._input_style())
        profile_layout.addWidget(self.password_input)

        # Botones Aceptar / Cancelar
        panel_btn_layout = QHBoxLayout()
        panel_btn_layout.setSpacing(10)

        self.panel_cancel = QPushButton("Cancelar")
        self._style_button(self.panel_cancel, "#D9534F", "#C64542")
        self.panel_cancel.clicked.connect(lambda: self._toggle_profile_panel(show=False))
        self.panel_cancel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        panel_btn_layout.addWidget(self.panel_cancel)

        self.panel_accept = QPushButton("Aceptar")
        self._style_button(self.panel_accept, "#1DB954", "#17A44C")
        self.panel_accept.clicked.connect(lambda: self._submit_profile())
        self.panel_accept.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        panel_btn_layout.addWidget(self.panel_accept)

        profile_layout.addLayout(panel_btn_layout)
        self.profile_panel.setLayout(profile_layout)

        card_layout.addWidget(self.profile_panel)

        # Estado del perfil
        self.label_status = QLabel("Perfil inexistente")
        self.label_status.setAlignment(Qt.AlignCenter)
        self.label_status.setStyleSheet("""
            QLabel {
                background-color: #D9534F;
                color: white;
                padding: 8px 14px;
                border-radius: 8px;
                font-weight: bold;
            }
        """)
        card_layout.addWidget(self.label_status)

        card.setLayout(card_layout)
        main_layout.addWidget(card)
        self.widget.setLayout(main_layout)

    # -----------------------------
    # Mostrar / ocultar panel integrado
    # -----------------------------
    def _toggle_profile_panel(self, show: bool, create: bool = True):
        self.profile_panel.setVisible(show)
        if show:
            self.username_input.clear()
            self.password_input.clear()
            self._current_action_create = create

    # -----------------------------
    # Enviar datos desde panel integrado
    # -----------------------------
    def _submit_profile(self):
        username = self.username_input.text()
        password = self.password_input.text()
        create = getattr(self, "_current_action_create", True)

        print(f"{'Crear' if create else 'Actualizar'} perfil: {username} / {password}")
        
        success = False
        if create:
            success = self.parent_module.engine.set_user_profile(username, password, update=False)
        else:
            success = self.parent_module.engine.set_user_profile(username, password, update=True)
        
        # Aquí integras la lógica real
        self._toggle_profile_panel(show=False)
        self._refresh_ui_status()

    # -----------------------------
    # Refrescar UI
    # -----------------------------
    def _refresh_ui_status(self):
        profile_exists = self.parent_module.engine.get_user_profile()
        #print("User profile:", profile_exists)
        
        if profile_exists:
            self.label_status.setText("Perfil existente. Actualiza el ya existente")
            self.label_status.setStyleSheet("""
                QLabel {
                    background-color: #1DB954;
                    color: white;
                    padding: 8px 14px;
                    border-radius: 8px;
                    font-weight: bold;
                }
            """)
            self.username_label.setText(f"Usuario: {profile_exists.get('USERNAME', 'ERROR. Invalid format')}")
            self.password_label.setText(f"Contraseña: {profile_exists.get('PASSWORD', 'ERROR. Invalid format')}")
            self.btn_create.setEnabled(False)
            self._style_button(self.btn_create, "#6c757d", "#6c757d")
            self._style_button(self.btn_update, "#1DB954", "#17A44C")
            self.btn_update.setEnabled(True)
        else:
            self.label_status.setText("Perfil inexistente. Crea uno nuevo")
            self.label_status.setStyleSheet("""
                QLabel {
                    background-color: #D9534F;
                    color: white;
                    padding: 8px 14px;
                    border-radius: 8px;
                    font-weight: bold;
                }
            """)
            self.username_label.setText("Usuario:")
            self.password_label.setText("Contraseña:")
            self._style_button(self.btn_create, "#0E639C", "#0B4F8C")
            self.btn_create.setEnabled(True)
            self._style_button(self.btn_update, "#6c757d", "#6c757d")
            self.btn_update.setEnabled(False)

    # -----------------------------
    # Estilos
    # -----------------------------
    def _style_field_label(self, lbl: QLabel):
        lbl.setStyleSheet("""
            QLabel {
                background-color: #2b2d31;
                color: #ffffff;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 14px;
            }
        """)

    def _style_button(self, btn: QPushButton, bg: str, bg_hover: str):
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg};
                color: white;
                border-radius: 8px;
                padding: 10px 16px;
                font-size: 14px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {bg_hover};
            }}
        """)

    def _input_style(self):
        return """
            QLineEdit {
                background-color: #1e1f22;
                color: white;
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #1DB954;
                background-color: #27292d;
            }
        """

    # -----------------------------
    # Interfaz
    # -----------------------------
    def get_widget(self) -> QWidget:
        return self.widget

    def execute(self, *args, **kwargs) -> ProcessInterface:
        print("Función UserProfile ejecutando (solo UI).")
        return None
