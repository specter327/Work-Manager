from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QStackedWidget,
    QHBoxLayout, QTreeWidget, QTreeWidgetItem, QLabel
)
from PyQt5.QtCore import Qt
import sys
import qdarkstyle  # Tema base

# Importación de módulos
from ..modules import available_modules
from .interfaces import ContextManager

class ApplicationGUI(QMainWindow):
    def __init__(self, modules_path: str = "src.data.modules"):
        self._app = QApplication.instance() or QApplication(sys.argv)
        super().__init__()

        self.modules_path = modules_path
        self.modules_loaded = []
        self.widgets = {}
        self.widget_map = {}
        self.context_manager = ContextManager()

        self.setGeometry(100, 100, 1000, 600)
        self.setWindowTitle("CRM Gestor - Tema Oscuro")

        # -------------------------------
        # Tema oscuro base + overrides personalizados
        # -------------------------------
        self._app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5() + self._custom_style())

        # -------------------------------
        # Layout principal
        # -------------------------------
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QHBoxLayout(central_widget)

        # ----- Sidebar -----
        self.sidebar_layout = QVBoxLayout()
        self.main_layout.addLayout(self.sidebar_layout, 1)

        self.apartados_tree = QTreeWidget()
        self.apartados_tree.setHeaderHidden(True)
        self.sidebar_layout.addWidget(self.apartados_tree)

        # ----- Área dinámica -----
        self.stack = QStackedWidget()
        self.main_layout.addWidget(self.stack, 4)

        placeholder = QLabel("Selecciona un apartado a la izquierda")
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setStyleSheet("color: white; font-size: 16px;")
        self.stack.addWidget(placeholder)

        # Conexión selección del árbol
        self.apartados_tree.itemClicked.connect(self.on_apartado_selected)

        # Estilo sidebar (se aplica adicionalmente al global)
        self.apartados_tree.setFocusPolicy(Qt.NoFocus)

        # -------------------------------
        # Cargar módulos dinámicamente
        # -------------------------------
        self.load_modules()

    # ======================================================
    #  Estilos personalizados (misma estética premium)
    # ======================================================
    def _custom_style(self):
        return """
        /* ----- Ventana principal ---- */
        QWidget {
            background-color: #2a2b2f;
        }

        /* ----- Sidebar (árbol de navegación) ----- */
        QTreeWidget {
            background-color: #2a2b2f;
            border-radius: 12px;
            padding: 8px;
            font-size: 14px;
            color: #E6EFFA;
        }
        QTreeWidget::item {
            padding: 10px;
            border-radius: 8px;
            margin-bottom: 3px;
        }
        QTreeWidget::item:hover {
            background-color: rgba(80,120,180,0.25);
        }
        QTreeWidget::item:selected,
        QTreeWidget::item:selected:active,
        QTreeWidget::item:selected:!active {
            background-color: #1ABC9C !important;
            color: white !important;
        }

        /* ----- Ventanas internas ----- */
        QWidget#Card {
            background-color: #14243B;
            border-radius: 16px;
            padding: 18px;
        }

        QLabel {
            font-family: 'Segoe UI';
        }

        QLabel#Title {
            font-size: 20px;
            font-weight: bold;
            color: #FFFFFF;
        }

        QLabel#StatLabel {
            font-size: 13px;
            color: #B9C6D4;
        }

        QLabel#StatValue {
            font-size: 16px;
            font-weight: bold;
            color: white;
        }

        QPushButton {
            background-color: #223A5E;
            border-radius: 10px;
            padding: 10px 14px;
            font-size: 14px;
            color: #E3EEFF;
        }
        QPushButton:hover {
            background-color: #2E547E;
        }
        QPushButton:pressed {
            background-color: #1A2F4A;
        }
        """

    # ======================================================
    #  Cargar módulos dinámicamente
    # ======================================================
    def load_modules(self):
        from src.data.modules import available_modules

        self.modules_loaded = []
        self.widgets = {}
        self.widget_map = {}

        for module_entry in available_modules:
            try:
                module_controller = module_entry.ModuleController(self.context_manager)
            except Exception as e:
                print(f"[ERROR] No se pudo instanciar ModuleController: {e}")
                continue
            
            try:
                module_controller.start()
            except Exception as Error:
                print(f"[ERROR] No se pudo iniciar el módulo {module_controller.module_name}: {Error}")
                continue

            self.modules_loaded.append(module_controller)
            module_name = module_controller.module_name

            # Crear item en el árbol
            module_item = QTreeWidgetItem([module_name])
            self.apartados_tree.addTopLevelItem(module_item)

            # Obtener funciones internas
            try:
                functions = module_controller.get_functions()
            except Exception as e:
                print(f"[ERROR] No se pudo obtener funciones de {module_name}: {e}")
                continue

            for func in functions:
                func_name = func.function_name
                widget = func.get_widget()

                self.widgets[func_name] = widget
                self.stack.addWidget(widget)

                func_item = QTreeWidgetItem([func_name])
                module_item.addChild(func_item)
                self.widget_map[id(func_item)] = widget

    # ======================================================
    #  Selección del árbol
    # ======================================================
    def on_apartado_selected(self, item, column):
        w = self.widget_map.get(id(item))
        if w:
            self.stack.setCurrentWidget(w)
        else:
            label = QLabel(f"Has seleccionado: {item.text(0)}")
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("color: white; font-size: 16px;")
            self.stack.addWidget(label)
            self.stack.setCurrentWidget(label)

    # ======================================================
    #  Start / Stop
    # ======================================================
    def start(self):
        self.show()
        sys.exit(self._app.exec_())

    def stop(self):
        self._app.quit()
