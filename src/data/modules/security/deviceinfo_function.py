from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QSizePolicy, QMessageBox
)
from PyQt5.QtCore import Qt

# Asumimos que estos existen en tu proyecto
from ...core.interfaces import FunctionInterface
from .engine import SecurityEngine

# from your_project.module_interface import ModuleInterface
# from your_project.process_interface import ProcessInterface
# from your_project.function_interface import FunctionInterface


class DeviceInfoFunction(FunctionInterface):
    """
    Implementación de FunctionInterface que muestra
    información del dispositivo en una interfaz gráfica.
    """

    def __init__(self, parent_module):
        super().__init__(parent_module)
        self.security_engine = SecurityEngine()
        self._build_ui()

    # ----------------------------------------------
    # Nombre de la función
    # ----------------------------------------------
    @property
    def function_name(self) -> str:
        return "Información del Dispositivo"

    # ----------------------------------------------
    # Método de ejecución (por ahora mock)
    # ----------------------------------------------
    def execute(self, *args, **kwargs):
        print("Ejecutando DeviceInfoFunction (placeholder)...")
        # Aquí luego llamaremos las funciones reales
        return None

    # ----------------------------------------------
    # Retorna el widget asociado
    # ----------------------------------------------
    def get_widget(self) -> QWidget:
        return self.widget

    # ----------------------------------------------
    # Construcción de la UI
    # ----------------------------------------------
    def _build_ui(self):
        layout = QVBoxLayout()
        self.widget.setLayout(layout)

        # Título
        title = QLabel("Información del Dispositivo")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Labels (solo placeholder; luego llenaremos con datos reales)
        self.machine_guid_label = QLabel("Machine GUID: ---")
        self.bios_serial_label = QLabel("BIOS Serial: ---")
        self.disk_serial_label = QLabel("Disk Serial: ---")
        self.device_hash_label = QLabel("Device ID (Hash): ---")

        for label in [
            self.machine_guid_label,
            self.bios_serial_label,
            self.disk_serial_label,
            self.device_hash_label,
        ]:
            label.setStyleSheet("font-size: 14px;")
            label.setAlignment(Qt.AlignLeft)
            layout.addWidget(label)

        # Botón para actualizar
        self.refresh_btn = QPushButton("Actualizar información")
        self.refresh_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                padding: 6px 14px;
                font-size: 14px;
            }
        """)

        # Por ahora no hace nada; después lo conectaremos
        self.refresh_btn.clicked.connect(lambda checked=False: self.update_device_info())

        layout.addWidget(self.refresh_btn, alignment=Qt.AlignCenter)

        # Espaciador
        layout.addStretch()

    # -------------------------------------------------------
    # Método que luego conectaremos al botón para llenar datos
    # -------------------------------------------------------
    def update_labels(self, info_dict: dict):
        """
        Actualiza los labels con la información real del dispositivo.
        Este método lo llamaremos más adelante cuando ya tengamos
        las funciones reales integradas.
        """
        #self.machine_guid_label.setText(f"Machine GUID: {info_dict.get('machine_guid', '---')}")
        #self.bios_serial_label.setText(f"BIOS Serial: {info_dict.get('bios_serial', '---')}")
        #self.disk_serial_label.setText(f"Disk Serial: {info_dict.get('disk_serial', '---')}")
        self.device_hash_label.setText(f"ID: {info_dict}")

    def update_device_info(self):
        try:
            info = self.security_engine.get_device_id()
            self.update_labels(info)
        except Exception as e:
            QMessageBox.critical(
                self.widget,
                "Error",
                f"No se pudo obtener información del dispositivo:\n{e}"
            )
