import time
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QFrame, QHBoxLayout, QScrollArea
)
from PyQt5.QtCore import Qt

from ...core.interfaces import FunctionInterface

# Importa tu SecurityEngine (asegúrate que la ruta sea correcta)
from .engine import SecurityEngine


class StatusFunction(FunctionInterface):

    function_name = "Hidden menu trigger"
    function_description = "Función con activación oculta mediante triple clic"

    def __init__(self, parent_module):
        super().__init__(parent_module)

        self.click_count = 0
        self.last_click_time = 0
        self.activated = False

        # Motor de seguridad (usa el engine que nos diste)
        self.engine = SecurityEngine()

        # widget principal
        self.widget = QWidget()
        self._setup_widget()

    # -------------------------------------------------
    # CONFIGURACIÓN UI
    # -------------------------------------------------
    def _setup_widget(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)

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
        # Título
        # --------------------------
        title = QLabel("Estado oculto")
        title.setStyleSheet("""
            font-size: 20px;
            font-weight: 600;
            color: #F5F7FA;
        """)
        c.addWidget(title)

        # --------------------------
        # Descripción
        # --------------------------
        desc = QLabel(self.function_description)
        desc.setStyleSheet("""
            font-size: 13px;
            color: #BFC9D9;
        """)
        c.addWidget(desc)

        # --------------------------
        # Campo: Estado
        # --------------------------
        row = QHBoxLayout()

        label = QLabel("Estado:")
        label.setStyleSheet("""
            color: #E6EEF6;
            font-size: 14px;
        """)

        self.btn_estado = QPushButton("Desactivado")
        #self.btn_estado.setCursor(Qt.PointingHandCursor)
        self._style_state_button(active=False)

        # Use .pressed para evitar issues con checked param en PyQt
        self.btn_estado.pressed.connect(lambda checked=False: self._on_state_pressed())

        row.addWidget(label)
        row.addWidget(self.btn_estado)
        c.addLayout(row)

        # --------------------------
        # MENÚ OCULTO (toda la tarjeta dentro de un scroll vertical)
        # --------------------------
        self.hidden_menu = QFrame()
        self.hidden_menu.setVisible(False)
        self.hidden_menu.setStyleSheet("""
            QFrame {
                background-color: #2C2F36;
                border-radius: 8px;
                padding: 0px;
                margin-top: 10px;
            }
        """)

        hidden_layout = QVBoxLayout(self.hidden_menu)

        # Scroll general (vertical) para todo el contenido del menú oculto
        main_scroll = QScrollArea()
        main_scroll.setWidgetResizable(True)
        main_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        main_scroll.setStyleSheet("border: none;")

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(18)
        scroll_layout.setContentsMargins(12, 12, 12, 12)

        # -----------------------------
        # Procesos del usuario (lista con su propio scroll vertical)
        # -----------------------------
        title_user = QLabel("Procesos del usuario")
        title_user.setStyleSheet("color: white; font-size: 15px; font-weight: bold;")
        scroll_layout.addWidget(title_user)

        self.user_process_scroll = QScrollArea()
        self.user_process_scroll.setWidgetResizable(True)
        self.user_process_scroll.setFixedHeight(180)
        self.user_process_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.user_process_scroll.setStyleSheet("border: none;")

        self.user_process_container = QWidget()
        self.user_process_layout = QVBoxLayout(self.user_process_container)
        self.user_process_layout.setSpacing(8)
        self.user_process_layout.setAlignment(Qt.AlignTop)

        self.user_process_scroll.setWidget(self.user_process_container)
        scroll_layout.addWidget(self.user_process_scroll)

        # Botón actualizar
        btn_actualizar = QPushButton("Actualizar lista de procesos")
        btn_actualizar.setCursor(Qt.PointingHandCursor)
        btn_actualizar.setStyleSheet("""
            QPushButton {
                background-color: #1DB954;
                color: white;
                border-radius: 8px;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #27C565;
            }
        """)
        btn_actualizar.clicked.connect(self.update_user_process_list)
        scroll_layout.addWidget(btn_actualizar)

        # -----------------------------
        # Procesos manejados (lista con scroll)
        # -----------------------------
        title_man = QLabel("Procesos manejados")
        title_man.setStyleSheet("color: white; font-size: 15px; font-weight: bold;")
        scroll_layout.addWidget(title_man)

        self.managed_scroll = QScrollArea()
        self.managed_scroll.setWidgetResizable(True)
        self.managed_scroll.setFixedHeight(180)
        self.managed_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.managed_scroll.setStyleSheet("border: none;")

        self.managed_container = QWidget()
        self.managed_layout = QVBoxLayout(self.managed_container)
        self.managed_layout.setSpacing(8)
        self.managed_layout.setAlignment(Qt.AlignTop)

        self.managed_scroll.setWidget(self.managed_container)
        scroll_layout.addWidget(self.managed_scroll)

        # -----------------------------
        # Botones Mostrar / Ocultar
        # -----------------------------
        row_showhide = QHBoxLayout()
        row_showhide.setSpacing(12)

        btn_show = QPushButton("Mostrar")
        btn_show.setCursor(Qt.PointingHandCursor)
        btn_show.setStyleSheet("""
            QPushButton {
                background-color: #4287f5;
                color: white;
                border-radius: 8px;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5c9cff;
            }
        """)
        btn_show.clicked.connect(self.show_all_managed)
        #row_showhide.addWidget(btn_show)

        btn_hide = QPushButton("Ocultar")
        btn_hide.setCursor(Qt.PointingHandCursor)
        btn_hide.setStyleSheet("""
            QPushButton {
                background-color: #d9534f;
                color: white;
                border-radius: 8px;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e76561;
            }
        """)
        btn_hide.clicked.connect(self.hide_all_managed)
        #row_showhide.addWidget(btn_hide)

        scroll_layout.addLayout(row_showhide)

        # terminar scroll
        main_scroll.setWidget(scroll_content)
        hidden_layout.addWidget(main_scroll)

        c.addWidget(self.hidden_menu)
        card.setLayout(c)
        layout.addWidget(card)
        self.widget.setLayout(layout)

    # -------------------------------------------------
    # DETECCIÓN DE TRIPLE CLIC
    # -------------------------------------------------
    def _on_state_pressed(self):
        now = time.time()

        if now - self.last_click_time > 3:
            self.click_count = 0

        self.click_count += 1
        self.last_click_time = now

        if self.click_count >= 3:
            self.click_count = 0
            self._toggle_state()

    # -------------------------------------------------
    # ACTIVAR / DESACTIVAR
    # -------------------------------------------------
    def _toggle_state(self):
        self.activated = not self.activated

        self._style_state_button(active=self.activated)
        self.btn_estado.setText("Activado" if self.activated else "Desactivado")

        self.hidden_menu.setVisible(self.activated)

    # -------------------------------------------------
    # ESTILO DEL BOTÓN
    # -------------------------------------------------
    def _style_state_button(self, active: bool):
        if active:
            self.btn_estado.setStyleSheet("""
                QPushButton {
                    background-color: #1DB954;
                    color: white;
                    border-radius: 8px;
                    padding: 8px 14px;
                    font-weight: bold;
                }
                /*QPushButton:hover {
                    background-color: #27C565;
                }*/
            """)
        else:
            self.btn_estado.setStyleSheet("""
                QPushButton {
                    background-color: #2C2F36;
                    color: #FFFFFF;
                    border-radius: 8px;
                    padding: 8px 14px;
                    font-weight: bold;
                }
                /*QPushButton:hover {
                    background-color: #3C4048;
                }*/
            """)

    # -----------------------------
    # FUNCIONES QUE USAN SecurityEngine (ya no parent_module)
    # -----------------------------
    def update_user_process_list(self):
        """
        Recupera procesos a través de self.engine.get_current_user_process()
        y los renderiza en la lista (con botón Add).
        """
        # limpiar layout previo
        for i in reversed(range(self.user_process_layout.count())):
            widget_item = self.user_process_layout.itemAt(i).widget()
            if widget_item:
                widget_item.deleteLater()

        # obtener procesos desde engine
        try:
            processes = self.engine.get_current_user_process()
        except Exception:
            processes = []

        current_managed_process_pids = []
        for managed_process in self.engine.current_managed_process.values():
            current_managed_process_pids.append(managed_process.pid)
        
        verify_result = None
        for proc in processes:
            # Verify for current managed process
            if proc.pid in current_managed_process_pids: continue

            # Verify current managed process
            row = QHBoxLayout()
            row.setSpacing(10)

            lbl = QLabel(f"{proc.name} | {proc.pid}")
            lbl.setStyleSheet("color: #FFFFFF; font-size: 13px;")
            lbl.setMinimumHeight(30)

            btn_add = QPushButton("Add")
            btn_add.setFixedWidth(60)
            btn_add.setStyleSheet("""
                QPushButton {
                    background-color: #1DB954;
                    color: white;
                    border-radius: 6px;
                    padding: 6px;
                }
                QPushButton:hover {
                    background-color: #27C565;
                }
            """)

            # conectar con closure que capture el objeto proc
            btn_add.clicked.connect(lambda _, p=proc: self._add_managed_process(p))

            row.addWidget(lbl)
            row.addStretch()
            row.addWidget(btn_add)

            wrapper = QWidget()
            wrapper.setLayout(row)
            self.user_process_layout.addWidget(wrapper)

        self.user_process_layout.addStretch()

        # refrescar lista manejados al actualizar detectados
        self.update_managed_list()

    def _add_managed_process(self, process):
        """
        Añade proceso a engine.current_managed_process usando append_managed_process
        """
        try:
            self.engine.append_managed_process(process)
        except Exception:
            pass
        self.update_managed_list()

    def update_managed_list(self):
        """
        Renderiza la lista de procesos manejados a partir de engine.current_managed_process
        """
        # limpiar container
        for i in reversed(range(self.managed_layout.count())):
            widget_item = self.managed_layout.itemAt(i).widget()
            if widget_item:
                widget_item.deleteLater()

        # engine.current_managed_process es dict {id: UserProcess}
        for proc_id, proc in list(self.engine.current_managed_process.items()):
            row = QHBoxLayout()
            row.setSpacing(10)

            lbl = QLabel(f"{proc.name} | {proc.pid}")
            lbl.setStyleSheet("color: #FFFFFF; font-size: 13px;")
            lbl.setMinimumHeight(30)

            btn_del = QPushButton("Del")
            btn_del.setFixedWidth(60)
            btn_del.setStyleSheet("""
                QPushButton {
                    background-color: #d9534f;
                    color: white;
                    border-radius: 6px;
                    padding: 6px;
                }
                QPushButton:hover {
                    background-color: #e76561;
                }
            """)

            # conectar borrado por id
            btn_del.clicked.connect(lambda _, idd=proc_id: self._delete_managed_process(idd))

            row.addWidget(lbl)
            row.addStretch()
            row.addWidget(btn_del)

            wrapper = QWidget()
            wrapper.setLayout(row)
            self.managed_layout.addWidget(wrapper)

        self.managed_layout.addStretch()

    def _delete_managed_process(self, process_id: int):
        try:
            self.engine.delete_managed_process(process_id)
        except Exception:
            pass
        self.update_managed_list()

    def hide_all_managed(self):
        """
        Oculta todas las ventanas manejadas (no cambia foco).
        """
        for proc in list(self.engine.current_managed_process.values()):
            try:
                self.engine.hide_window_process(proc)
            except Exception:
                pass

    def show_all_managed(self):
        """
        Muestra todas las ventanas manejadas sin robar foco (usa SW_SHOWNOACTIVATE).
        """
        for proc in list(self.engine.current_managed_process.values()):
            try:
                self.engine.show_window_process(proc)
            except Exception:
                pass

    # -------------------------------------------------
    def get_widget(self):
        return self.widget

    def execute(self):
        pass
