from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QFrame, 
    QHBoxLayout, QLineEdit
)
from PyQt5.QtCore import Qt, QTimer
from ...core.interfaces import FunctionInterface
from .engine import ExportContactsProcess


class ExportContactsFunction(FunctionInterface):
    """
    Export contacts to Excel with modern dark-themed UI
    similar to the GenerateCallVolumeFunctionUI style.
    """

    function_name = "Export Contacts"

    def __init__(self, parent_module):
        super().__init__(parent_module)

        self.process = None

        self.widget = QWidget()
        self._setup_widget()

        # Timer para refrescar el estado del proceso
        self._update_timer = QTimer()
        self._update_timer.setInterval(500)
        self._update_timer.timeout.connect(self._update_process_status)

    # ============================================================
    #   UI SETUP — BOTONES LATERALES
    # ============================================================
    def _setup_widget(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # ---------------------------------------------------------
        #   CARD (contenedor principal)
        # ---------------------------------------------------------
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

        # ---------------------------------------------------------
        #   TITULO
        # ---------------------------------------------------------
        title = QLabel("Export Contacts to Excel")
        title.setStyleSheet("""
            font-size: 19px;
            font-weight: 600;
            color: #FFFFFF;
        """)
        card_layout.addWidget(title)

        # ---------------------------------------------------------
        #   DESCRIPCIÓN
        # ---------------------------------------------------------
        desc = QLabel("Export contacts to an Excel file. Shows result and file path.")
        desc.setStyleSheet("font-size: 13px; color: #C7C7C7;")
        desc.setWordWrap(True)
        card_layout.addWidget(desc)

        # ---------------------------------------------------------
        #   BOTONES INICIAR EXPORTACIÓN Y RESULTADO
        #   - A la misma altura
        #   - Start a la izquierda, Resultado a la derecha
        # ---------------------------------------------------------
        btn_row = QHBoxLayout()
        btn_row.setContentsMargins(0, 0, 0, 0)
        btn_row.setSpacing(10)

        self.btn_execute = QPushButton("Start Export")
        self._style_button(self.btn_execute, "#0d6efd", "#0B4F8C")
        self.btn_execute.setFixedSize(140, 35)
        self.btn_execute.clicked.connect(lambda: self._handle_execute())

        self.btn_result = QPushButton("Resultado")
        self._style_button(self.btn_result, "#2C2F36", "#3C4048")
        self.btn_result.setFixedSize(140, 35)
        self.btn_result.setEnabled(False)

        # Ubicación: izquierda y derecha
        btn_row.addWidget(self.btn_execute, alignment=Qt.AlignLeft)
        btn_row.addStretch()
        btn_row.addWidget(self.btn_result, alignment=Qt.AlignRight)

        card_layout.addLayout(btn_row)

        # ---------------------------------------------------------
        #   CAMPO DE RUTA DE ARCHIVO
        # ---------------------------------------------------------
        self.file_path_field = QLineEdit()
        self.file_path_field.setReadOnly(True)
        self.file_path_field.setPlaceholderText("Archivo exportado")
        self.file_path_field.setStyleSheet("""
            QLineEdit {
                background-color: #2b2d31;
                color: #ffffff;
                border: 1px solid #3C3C3C;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 14px;
            }
            QLineEdit:hover {
                border: 1px solid #4A90E2;
                background-color: #323438;
            }
            QLineEdit:focus {
                border: 1px solid #0E639C;
                background-color: #2f3237;
            }
            QLineEdit[placeholderText="true"] {
                color: #9A9A9A;
            }
        """)
        card_layout.addWidget(self.file_path_field)

        # ---------------------------------------------------------
        #   SET LAYOUT
        # ---------------------------------------------------------
        card.setLayout(card_layout)
        layout.addWidget(card)
        self.widget.setLayout(layout)

    # ============================================================
    #   ESTILOS
    # ============================================================
    def _style_button(self, btn, bg, bg_hover):
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg};
                color: white;
                border-radius: 8px;
                padding: 10px 18px;
                font-size: 14px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {bg_hover};
            }}
        """)

    def _style_line_edit(self, le):
        le.setStyleSheet("""
            QLineEdit {
                background-color: #2b2d31;
                color: #ffffff;
                border: 1px solid #3C3C3C;
                border-radius: 8px;
                padding: 10px 12px;
                font-size: 14px;
            }
            QLineEdit:hover {
                border: 1px solid #0E639C;
                background-color: #323438;
            }
            QLineEdit:focus {
                border: 1px solid #0E639C;
                background-color: #2f3237;
            }
        """)

    # ============================================================
    #   BOTÓN HANDLER
    # ============================================================
    def _handle_execute(self):
        self.btn_result.setText("Exportando contactos...")
        process = self.execute()
        process.start()

        self.btn_execute.setEnabled(False)
        self.btn_result.setText("Resultado")
        self._style_button(self.btn_result, "#2C2F36", "#3C4048")
        self.file_path_field.clear()

        self._update_timer.start()

    # ============================================================
    #   TIMER UPDATE PARA REFRESCAR ESTADO
    # ============================================================
    def _update_process_status(self):
        if not self.process:
            return

        if self.process.status == self.process.FINISHED_STATUS:
            self._update_timer.stop()
            self.btn_execute.setEnabled(True)

            result_data = self.process.current_process
            exported_file = result_data.get("EXPORTED_FILE_RESULT", None)

            if exported_file:
                self.btn_result.setText("Éxito")
                self._style_button(self.btn_result, "#1DB954", "#17A44C")
                self.file_path_field.setText(exported_file)
            else:
                self.btn_result.setText("Fallo")
                self._style_button(self.btn_result, "#D9534F", "#B94743")
                self.file_path_field.setText("")

    # ============================================================
    #   GET WIDGET
    # ============================================================
    def get_widget(self) -> QWidget:
        return self.widget

    # ============================================================
    #   EJECUTAR PROCESO (SIN CAMBIOS FUNCIONALES)
    # ============================================================
    def execute(self, *args, **kwargs) -> ExportContactsProcess:
        if not self.process or self.process.status.is_finished:
            self.process = ExportContactsProcess(
                CRMUtilities=self.parent_module.engine
            )
        return self.process
