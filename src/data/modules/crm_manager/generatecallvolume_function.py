# UI para controlar el engine de volumen de llamadas
import time
from threading import Thread

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QFrame,
    QHBoxLayout, QLineEdit, QProgressBar
)
from PyQt5.QtCore import QObject, pyqtSignal, Qt
from PyQt5.QtGui import QIntValidator

from ...core.interfaces import FunctionInterface
from .engine import GenerateCallVolumeFunction as EngineCallVolume


class VolumeEmitter(QObject):
    progress_changed = pyqtSignal(float)
    status_changed = pyqtSignal(str)
    details_changed = pyqtSignal(dict)


class NumericLineEdit(QLineEdit):
    """
    QLineEdit que solo acepta enteros (QIntValidator) y expone
    value() / setValue() para mantener compatibilidad con código
    que esperaba QSpinBox.
    """
    def __init__(self, minimum=0, maximum=999999, parent=None):
        super().__init__(parent)
        self._min = minimum
        self._max = maximum
        self.setValidator(QIntValidator(self._min, self._max, self))
        self.setText(str(self._min))
        self.setAlignment(Qt.AlignRight)

    def value(self) -> int:
        txt = self.text().strip()
        if txt == "":
            return 0
        try:
            v = int(txt)
        except ValueError:
            return 0
        # Clamp to range
        if v < self._min:
            return self._min
        if v > self._max:
            return self._max
        return v

    def setValue(self, val: int):
        if val is None:
            val = 0
        try:
            ival = int(val)
        except Exception:
            ival = 0
        # Clamp
        if ival < self._min:
            ival = self._min
        if ival > self._max:
            ival = self._max
        self.setText(str(ival))


class GenerateCallVolumeFunctionUI(FunctionInterface):

    function_name = "Generar Volumen de Llamadas"
    function_description = "Ejecuta el proceso que genera llamadas y las cuelga para registrar tráfico."

    def __init__(self, parent_module):
        super().__init__(parent_module)

        self.CRMUtilities = parent_module.engine
        self.engine = parent_module.engine

        self.process = None
        self._emitter = VolumeEmitter()

        self.widget = QWidget()
        self._setup_widget()

        self._emitter.progress_changed.connect(self._update_progress)
        self._emitter.status_changed.connect(self._update_status)
        self._emitter.details_changed.connect(self._update_details)

    # ============================================================
    #   UI SETUP — DARK MODERN STYLE
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
        c = QVBoxLayout()
        c.setSpacing(15)

        # ---------------------------------------------------------
        #   TITULO
        # ---------------------------------------------------------
        title = QLabel("Generador de volumen de llamadas")
        title.setStyleSheet("""
            font-size: 19px;
            font-weight: 600;
            color: #FFFFFF;
        """)
        c.addWidget(title)

        # ---------------------------------------------------------
        #   DESCRIPCIÓN
        # ---------------------------------------------------------
        desc = QLabel(self.function_description)
        desc.setStyleSheet("font-size: 13px; color: #C7C7C7;")
        desc.setWordWrap(True)
        c.addWidget(desc)

        # ---------------------------------------------------------
        #   SPINBOX ROWS (ahora NumericLineEdit)
        # ---------------------------------------------------------
        def field_row(label_text, widget):
            row = QHBoxLayout()
            row.setSpacing(10)

            label = QLabel(label_text)
            label.setStyleSheet("color: #D4D4D4; font-size: 13px;")

            row.addWidget(label)
            row.addWidget(widget, 1)
            return row

        # Total objetivo (NumericLineEdit)
        self.input_total_objective = NumericLineEdit(minimum=1, maximum=999999)
        self.input_total_objective.setValue(500)
        self._apply_spinbox_style(self.input_total_objective)
        c.addLayout(field_row("Total objetivo:", self.input_total_objective))

        # Llamadas por contacto
        self.input_calls_per_contact = NumericLineEdit(minimum=1, maximum=99)
        self.input_calls_per_contact.setValue(1)
        self._apply_spinbox_style(self.input_calls_per_contact)
        c.addLayout(field_row("Llamadas / contacto:", self.input_calls_per_contact))

        # Página inicio
        self.input_start_page = NumericLineEdit(minimum=1, maximum=9999)
        self.input_start_page.setValue(1)
        self._apply_spinbox_style(self.input_start_page)
        c.addLayout(field_row("Página inicio:", self.input_start_page))

        # ---------------------------------------------------------
        #   ESTADO DEL PROCESO
        # ---------------------------------------------------------
        self.lbl_status = QLabel("Detenido")
        self.lbl_status.setAlignment(Qt.AlignCenter)
        self.lbl_status.setStyleSheet("""
            QLabel {
                background-color: #5A0000;
                color: white;
                padding: 8px;
                border-radius: 8px;
                font-weight: 600;
                font-size: 14px;
            }
        """)
        c.addWidget(self.lbl_status)

        # ---------------------------------------------------------
        #   PROGRESO
        # ---------------------------------------------------------
        self.progress = QProgressBar()
        self.progress.setValue(0)
        self.progress.setFixedHeight(20)
        self.progress.setStyleSheet("""
            QProgressBar {
                border: 1px solid #3C3C3C;
                border-radius: 6px;
                background: #1E1E1E;
                color: #D4D4D4;
                text-align: center;
                font-size: 12px;
            }
            QProgressBar::chunk {
                background-color: #0E639C;
                border-radius: 6px;
            }
        """)
        c.addWidget(self.progress)

        # ---------------------------------------------------------
        #   DETALLES
        # ---------------------------------------------------------
        self.lbl_details = QLabel("Procesados: 0 | Actual: 0 | Hoy: 0")
        self.lbl_details.setStyleSheet("color:#C7C7C7; font-size: 13px;")
        c.addWidget(self.lbl_details)

        # ---------------------------------------------------------
        #   BOTONES MODERNOS
        # ---------------------------------------------------------
        buttons = QHBoxLayout()
        buttons.setSpacing(12)

        btn_start = QPushButton("Iniciar")
        btn_stop = QPushButton("Detener")

        # Botón base
        def style_button(btn, bg, bg_hover):
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {bg};
                    color: white;
                    border-radius: 8px;
                    padding: 8px 16px;
                    font-size: 14px;
                    /*font-weight: 600;*/
                }}
                QPushButton:hover {{
                    background-color: {bg_hover};
                }}
            """)

        style_button(btn_start, "#0d6efd", "#0b5cd5")
        style_button(btn_stop,  "#D9534F", "#B94743")

        btn_start.clicked.connect(lambda checked=False: self._start_process())
        btn_stop.clicked.connect(lambda checked=False: self._stop_process())

        buttons.addWidget(btn_start)
        buttons.addWidget(btn_stop)
        c.addLayout(buttons)

        card.setLayout(c)
        layout.addWidget(card)
        self.widget.setLayout(layout)

    # ============================================================
    #   SPINBOX STYLE (ahora compatible con NumericLineEdit)
    # ============================================================
    def _apply_spinbox_style(self, spin):
        # spin puede ser QLineEdit personalizado (NumericLineEdit)
        spin.setStyleSheet("""
            /* ===========================
               NUMERIC INPUT — DARK MINIMAL
               =========================== */
            QLineEdit {
                background-color: #2b2d31;
                color: #ffffff;
                border: 1px solid #3C3C3C;
                border-radius: 8px;
                padding: 8px 12px;
                min-width: 130px;
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

            /* Placeholder color */
            QLineEdit[placeholderText="true"] {
                color: #9A9A9A;
            }
        """)
        spin.setAlignment(Qt.AlignRight)

    # ============================================================
    #   ENGINE CONTROL + SIGNAL UPDATES
    # ============================================================
    def get_widget(self):
        return self.widget

    def _start_process(self):
        print("[UI] Iniciar proceso de volumen de llamadas...")

        total = self.input_total_objective.value()
        per_contact = self.input_calls_per_contact.value()
        start_page = self.input_start_page.value()

        self.process = EngineCallVolume(
            CRMUtilities=self.parent_module.engine,
            total_objective_calls=total,
            total_calls_per_contact=per_contact,
            start_page=start_page
        )

        self.process.start()

        Thread(target=self._poll_engine_status, daemon=True).start()

        self._emitter.status_changed.emit("Ejecutando")

    def _poll_engine_status(self):
        while True:
            if not self.process:
                return
            progress = self.process.current_progress()
            details = self.process.current_process()
            self._emitter.progress_changed.emit(progress)
            self._emitter.details_changed.emit(details)
            if getattr(self.process, "status", None) == "FINISHED":
                self._emitter.status_changed.emit("Finalizado")
                return
            time.sleep(0.3)

    def _stop_process(self):
        if self.process:
            self.process.stop()
        self._emitter.status_changed.emit("Detenido")

    def _update_progress(self, value):
        self.progress.setValue(int(value))

    def _update_status(self, status):
        colors = {
            "Ejecutando": "#0E639C",
            "Finalizado": "#1DB954",
            "Detenido":   "#AA0000",
        }
        self.lbl_status.setText(status)
        self.lbl_status.setStyleSheet(f"""
            QLabel {{
                background-color: {colors.get(status, "#3C3C3C")};
                color: white;
                padding: 8px;
                border-radius: 8px;
                font-weight: 600;
            }}
        """)

    def _update_details(self, data):
        proc  = data.get("TOTAL_PROCESSED_CONTACTS", 0)
        cur   = data.get("CURRENT_PAGE_NUMBER", 0)
        today = data.get("TOTAL_TODAY_CONTACTS", 0)

        self.lbl_details.setText(
            f"Procesados: {proc} | Actual page: {cur} | Hoy: {today}"
        )

    def execute(self):
        pass
