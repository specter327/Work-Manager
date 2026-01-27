# Library import
import sys
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QGridLayout, QFrame, QProgressBar
)
from PyQt5.QtCore import Qt, QTimer

from ...core.interfaces import FunctionInterface
from .engine import ExtractTodayContactsProcess


# ------------------------------------------------------------
#   FUNCTION METADATA
# ------------------------------------------------------------
FUNCTION_NAME = "Extract today contacts"


# ------------------------------------------------------------
#   FUNCTION IMPLEMENTATION
# ------------------------------------------------------------
class ExtractTodayContactsFunction(FunctionInterface):

    @property
    def function_name(self) -> str:
        return FUNCTION_NAME

    # --------------------------------------------------------
    #   CONSTRUCTOR
    # --------------------------------------------------------
    def __init__(self, parent_module):
        super().__init__(parent_module)

        self.process: ExtractTodayContactsProcess | None = None

        # Build UI
        self._build_ui()

        # Timer
        self.update_timer = QTimer()
        self.update_timer.setInterval(300)
        self.update_timer.timeout.connect(self._update_stats)


    # --------------------------------------------------------
    #   EXECUTE
    # --------------------------------------------------------
    def execute(self, *args, **kwargs) -> ExtractTodayContactsProcess:

        self.process = ExtractTodayContactsProcess(
            CRMUtilities=self.parent_module.engine
        )

        self.process.start()
        self.update_timer.start()

        return self.process


    # --------------------------------------------------------
    #   STOP PROCESS
    # --------------------------------------------------------
    def _stop_process(self):
        if self.process:
            self.process.stop()


    # --------------------------------------------------------
    #   BUILD UI (Dark Mode)
    # --------------------------------------------------------
    def _build_ui(self):

        # -------- GLOBAL DARK THEME --------
        self.widget.setStyleSheet("""
            QWidget {
                background-color: #1e1f22;
                color: #e9e9e9;
                font-family: 'Segoe UI';
            }

            QLabel {
                color: #dddddd;
            }

            QPushButton {
                background-color: #2e2f33;
                color: #f1f1f1;
                border-radius: 6px;
                padding: 8px 20px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #3f4045;
            }
            QPushButton:pressed {
                background-color: #505155;
            }
        """)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # ---------- TITLE ----------
        title = QLabel("Extract today contacts")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size: 22px;
            font-weight: 600;
            color: #ffffff;
        """)

        main_layout.addWidget(title)

        # ---------- BUTTONS ----------
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(20)

        self.btn_start = QPushButton("Iniciar")
        self.btn_start.setStyleSheet("""
            QPushButton {
                background-color: #0d6efd;
            }
            QPushButton:hover {
                background-color: #0b5cd5;
            }
        """)
        self.btn_start.clicked.connect(lambda checked=False: self.execute())

        self.btn_stop = QPushButton("Detener")
        self.btn_stop.setStyleSheet("""
            QPushButton {
                background-color: #d9534f;
            }
            QPushButton:hover {
                background-color: #b94743;
            }
        """)
        self.btn_stop.clicked.connect(lambda checked=False: self._stop_process())

        btn_layout.addWidget(self.btn_start)
        btn_layout.addWidget(self.btn_stop)

        main_layout.addLayout(btn_layout)

        # ---------- CARD ----------
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #2a2b2f;
                border-radius: 12px;
                padding: 20px;
            }
        """)

        card_layout = QVBoxLayout()
        card_layout.setSpacing(20)

        # ---------- GRID ----------
        grid = QGridLayout()
        grid.setSpacing(14)

        self.lbl_current_page = self._create_stat(grid, 0, "Página actual")
        self.lbl_last_page = self._create_stat(grid, 1, "Última página")
        self.lbl_processed_pages = self._create_stat(grid, 2, "Páginas procesadas")
        self.lbl_total_contacts = self._create_stat(grid, 3, "Contactos totales")
        self.lbl_today_contacts = self._create_stat(grid, 4, "Contactos de hoy")

        card_layout.addLayout(grid)

        # ---------- PROGRESS BAR ----------
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #1f2023;
                border-radius: 8px;
                height: 14px;
            }
            QProgressBar::chunk {
                background-color: #4dabf7;
                border-radius: 8px;
            }
        """)

        card_layout.addWidget(self.progress_bar)

        card.setLayout(card_layout)
        main_layout.addWidget(card)

        self.widget.setLayout(main_layout)


    # --------------------------------------------------------
    #   STAT ROW
    # --------------------------------------------------------
    def _create_stat(self, layout: QGridLayout, row: int, label: str) -> QLabel:

        lbl_title = QLabel(label + ":")
        lbl_title.setStyleSheet("""
            font-size: 13px;
            color: #bbbbbb;
        """)

        lbl_value = QLabel("0")
        lbl_value.setStyleSheet("""
            font-size: 14px;
            background-color: #1f2023;
            border-radius: 6px;
            padding: 4px 10px;
            min-width: 80px;
            color: #ffffff;
        """)

        layout.addWidget(lbl_title, row, 0)
        layout.addWidget(lbl_value, row, 1)

        return lbl_value


    # --------------------------------------------------------
    #   UPDATE DISPLAY
    # --------------------------------------------------------
    def _update_stats(self):
        if not self.process:
            return

        data = self.process.current_process

        self.lbl_current_page.setText(str(data["CURRENT_PAGE_NUMBER"]))
        self.lbl_last_page.setText(str(data["LAST_PAGE_NUMBER"]))
        self.lbl_processed_pages.setText(str(data["TOTAL_PROCESSED_PAGES"]))
        self.lbl_total_contacts.setText(str(data["TOTAL_CONTACTS"]))
        self.lbl_today_contacts.setText(str(data["TOTAL_TODAY_CONTACTS"]))

        # progress %
        self.progress_bar.setValue(int(self.process.current_progress))


    # --------------------------------------------------------
    #   RETURN WIDGET
    # --------------------------------------------------------
    def get_widget(self) -> QWidget:
        return self.widget
