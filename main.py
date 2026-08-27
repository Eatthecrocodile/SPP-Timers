import sys
import json
from pathlib import Path

from datetime import datetime
from ui.timer_widget import TimerWidget
from flow_layout import FlowLayout
from ui.settings_menu import SettingsMenu

from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QFont, QPainter, QColor, QIcon
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QPushButton,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QGridLayout,
    QScrollArea,
    QFileDialog,
    QLineEdit
)


def resource_path(relative_path):
    """
    Retourne le chemin vers une ressource :
    - depuis le dossier du projet en développement
    - depuis le bundle PyInstaller en production
    """
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(__file__).resolve().parent

    return base_path / relative_path


class DrawerHandle(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setFixedHeight(60)
        self.setCursor(Qt.PointingHandCursor)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.parent().settingsMenu.open_drawer()

        super().mousePressEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(
            QPainter.Antialiasing
        )

        painter.setPen(Qt.NoPen)
        painter.setBrush(
            QColor("#555")
        )

        width = 46
        height = 5

        x = (
            self.width() - width
        ) // 2

        y = (
            self.height() - height
        ) // 2

        painter.drawRoundedRect(
            x,
            y,
            width,
            height,
            2.5,
            2.5
        )


class MainWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.setObjectName("mainWindow")
        self.setWindowTitle("SPP Timers")
        self.resize(900, 600)

        self.settings = {
            "show_clock": True,
            "sort_urgent": False,
            "vibration": False,
            "lock_desk": False,
            "auto_delete": False,
            "auto_delete_delay": 10
        }

        self.setStyleSheet("""
            QWidget#mainWindow {
                background-color: #000;
                color: white;
                font-family: Arial;
            }

            QScrollArea {
                background-color: #000;
                border: none;
            }

            QScrollArea QWidget {
                background-color: #000;
            }

            QPushButton {
                background-color: #00aaff;
                color: black;
                border: none;
                border-radius: 8px;
                padding: 8px 15px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #666;
                color: #00aaff;
            }
        """)

        # Horloge
        self.clock = QLabel()
        self.clock.setAlignment(Qt.AlignCenter)
        self.clock.setStyleSheet("""
            color: red;
            font-size: 50px;
            font-weight: bold;
        """)

        # Project Name
        self.projectName = QLineEdit("PROJECT NAME")
        self.projectName.setAlignment(Qt.AlignCenter)
        self.projectName.setFixedHeight(26)

        self.projectName.setStyleSheet("""
            QLineEdit {
                background: transparent;
                color: #00aaff;
                border: none;
                border-top: 1px solid #333;
                padding: 3px 0 0 0;
                font-size: 14px;
                font-weight: bold;
            }

            QLineEdit:focus {
                border-top: 1px solid #00aaff;
            }
        """)

        # Bloc central du header
        clockBlock = QVBoxLayout()
        clockBlock.setContentsMargins(0, 0, 0, 0)
        clockBlock.setSpacing(2)
        clockBlock.addWidget(self.clock)
        clockBlock.addWidget(self.projectName)

        # Boutons
        self.addButton = QPushButton("+ Timer")
        self.addButton.clicked.connect(self.add_timer)

        self.settingsButton = QPushButton("☰")
        self.settingsButton.setStyleSheet("""
            QPushButton:hover {
                color: black;
            }
        """)

        self.settingsMenu = SettingsMenu(self)
        self.drawerHandle = DrawerHandle(self)
        self.drawerHandle.raise_()

        self.settingsMenu.opened.connect(
            self.update_drawer_handle
        )

        self.settingsMenu.closed.connect(
            self.update_drawer_handle
        )

        self.settingsButton.clicked.connect(
            self.settingsMenu.toggle
        )

        self.settingsMenu.show_clock_changed.connect(
            self._show_clock_changed
        )

        self.settingsMenu.save_requested.connect(
            self.save_timers
        )

        self.settingsMenu.open_requested.connect(
            self.load_timers
        )

        self.settingsMenu.show_timer_mode_changed.connect(
            self._show_timer_mode_changed
        )

        self.settingsMenu.sort_urgent_changed.connect(
            self._sort_urgent_changed
        )

        self.settingsMenu.vibration_changed.connect(
            self._vibration_changed
        )

        self.settingsMenu.lock_changed.connect(
            self._lock_changed
        )

        self.settingsMenu.start_all_requested.connect(
            self.start_all_timers
        )

        self.settingsMenu.auto_delete_changed.connect(
            self._auto_delete_changed
        )

        self.settingsMenu.auto_delete_delay_changed.connect(
            self._auto_delete_delay_changed
        )

        # Layout haut
        top = QHBoxLayout()

        top.addStretch()
        top.addLayout(clockBlock)

        top.addStretch()
        top.addWidget(self.addButton)
        top.addWidget(self.settingsButton)

        # Layout principal
        layout = QGridLayout()

        # Zone scrollable des timers
        self.timerContainer = QWidget()

        self.timerArea = FlowLayout(
            self.timerContainer,
            spacing=10
        )

        self.timerContainer.setLayout(self.timerArea)

        self.scrollArea = QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )
        self.scrollArea.setVerticalScrollBarPolicy(
            Qt.ScrollBarAsNeeded
        )
        self.scrollArea.setFrameShape(QScrollArea.NoFrame)

        self.scrollArea.setWidget(self.timerContainer)

        self.timers = []

        layout.addLayout(top, 0, 0, 1, 2)
        layout.addWidget(self.scrollArea, 1, 0, 1, 2)

        layout.setRowStretch(0, 0)
        layout.setRowStretch(1, 1)

        self.setLayout(layout)

        self.update_drawer_handle()

        # ==========================================================
        # MOTEUR TEMPOREL MAITRE
        # ==========================================================

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time_engine)
        self.timer.start(250)

        self.update_time_engine()

    def update_drawer_handle(self):

        if not hasattr(self, "drawerHandle"):
            return

        handle_height = 60

        self.drawerHandle.setGeometry(
            0,
            self.height() - handle_height,
            self.width(),
            handle_height
        )

        self.drawerHandle.setVisible(
            not self.settingsMenu.is_open
        )

        self.drawerHandle.raise_()

    def _show_clock_changed(self, value):
        self.settings["show_clock"] = value
        self.clock.setVisible(value)

    def _show_timer_mode_changed(self, value):
        self.settings["show_timer_mode"] = value

        for timer in self.timers:
            timer.modeSwitch.setVisible(value)

    def _sort_urgent_changed(self, value):

        self.settings["sort_urgent"] = value

        if not value:
            return

        active = [
            timer
            for timer in self.timers
            if timer.target is not None
        ]

        inactive = [
            timer
            for timer in self.timers
            if timer.target is None
        ]

        active.sort(
            key=lambda timer: timer.target
        )

        ordered = active + inactive

        for timer in ordered:
            self.timerArea.removeWidget(timer)

        for timer in ordered:
            self.timerArea.addWidget(timer)

    def _vibration_changed(self, value):
        self.settings["vibration"] = value

    def _lock_changed(self, value):

        print("LOCK DESK =", value)
        print("TIMERS =", len(self.timers))

        self.settings["lock_desk"] = value

        for timer in self.timers:
            timer.set_locked(value)

    def _auto_delete_changed(self, value):

        self.settings["auto_delete"] = value

        for timer in self.timers:
            timer.auto_delete = value

    def _auto_delete_delay_changed(self, value):

        self.settings["auto_delete_delay"] = value

        for timer in self.timers:
            timer.auto_delete_delay = value

    def update_time_engine(self):

        now = datetime.now()

        current_second = now.replace(
            microsecond=0
        )

        for timer in self.timers:
            timer.update(
                now,
                current_second
            )

        self.update_clock(
            now
        )

    def update_clock(self, now):

        self.clock.setText(
            now.strftime("%H:%M:%S")
        )

    def start_all_timers(self):

        for timer in self.timers:
            timer.start()

    def add_timer(self):
        timer = TimerWidget()

        timer.auto_delete = self.settings.get(
            "auto_delete",
            False
        )

        timer.auto_delete_delay = self.settings.get(
            "auto_delete_delay",
            10
        )

        timer.modeSwitch.setVisible(
            self.settings.get("show_timer_mode", True)
        )

        timer.delete_requested.connect(self.remove_timer)

        self.timers.append(timer)

        self.timerArea.addWidget(timer)

        timer.set_locked(
            self.settings["lock_desk"]
        )

        def start_all_timers(self):

            for timer in self.timers:
                timer.start()

    # ==============================================================
    # EXPORT JSON
    # ==============================================================

    def save_timers(self):

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save SPP-Timers",
            "",
            "SPP-Timers JSON (*.json)"
        )

        if not file_path:
            return

        data = {
            "version": "1.0",
            "envName": self.projectName.text(),
            "events": [],
            "settings": {
                "showClock": self.settings.get(
                    "show_clock",
                    True
                ),
                "sortUrgentFirst": self.settings.get(
                    "sort_urgent",
                    False
                ),
                "vibration": self.settings.get(
                    "vibration",
                    False
                ),
                "locked": self.settings.get(
                    "lock_desk",
                    False
                ),
                "autoDelete": self.settings.get(
                    "auto_delete",
                    False
                ),
                "autoDeleteDelay": self.settings.get(
                    "auto_delete_delay",
                    60
                )
            }
        }

        for timer in self.timers:
            data["events"].append(
                timer.to_event_data()
            )

        with open(
            file_path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                data,
                file,
                indent=4,
                ensure_ascii=False
            )

    # ==============================================================
    # IMPORT JSON
    # ==============================================================

    def load_timers(self):

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open SPP-Timers",
            "",
            "SPP-Timers JSON (*.json)"
        )

        if not file_path:
            return

        try:

            with open(
                file_path,
                "r",
                encoding="utf-8"
            ) as file:

                data = json.load(file)

        except (OSError, json.JSONDecodeError):
            return

        # ----------------------------------------------------------
        # VERIFIER LE FORMAT
        # ----------------------------------------------------------

        if data.get("version") != "1.0":
            return

        # ----------------------------------------------------------
        # NOM DU PROJET
        # ----------------------------------------------------------

        self.projectName.setText(
            data.get("envName", "")
        )

        # ----------------------------------------------------------
        # REGLAGES
        # ----------------------------------------------------------

        settings = data.get(
            "settings",
            {}
        )

        self.settings["show_clock"] = settings.get(
            "showClock",
            True
        )

        self.settings["lock_desk"] = settings.get(
            "locked",
            False
        )

        self.settings["sort_urgent"] = settings.get(
            "sortUrgentFirst",
            False
        )

        self.settings["vibration"] = settings.get(
            "vibration",
            False
        )

        self.settings["auto_delete"] = settings.get(
            "autoDelete",
            False
        )

        self.settings["auto_delete_delay"] = settings.get(
            "autoDeleteDelay",
            60
        )

        self.settings["auto_delete"] = settings.get(
            "autoDelete",
            False
        )

        self.settings["auto_delete_delay"] = settings.get(
            "autoDeleteDelay",
            60
        )

        self.settingsMenu.autoDeleteCheck.setChecked(
            self.settings["auto_delete"]
        )

        self.settingsMenu.autoDeleteSlider.setValue(
            self.settings["auto_delete_delay"]
        )

        self.clock.setVisible(
            self.settings["show_clock"]
        )

        # ----------------------------------------------------------
        # SUPPRIMER LES TIMERS ACTUELS
        # ----------------------------------------------------------

        for timer in self.timers:
            self.timerArea.removeWidget(timer)
            timer.deleteLater()

        self.timers.clear()

        # ----------------------------------------------------------
        # RECREER LES TIMERS
        # ----------------------------------------------------------

        for event_data in data.get(
            "events",
            []
        ):

            timer = TimerWidget()

            timer.from_event_data(
                event_data
            )

            timer.auto_delete = self.settings.get(
                "auto_delete",
                False
            )

            timer.auto_delete_delay = self.settings.get(
                "auto_delete_delay",
                10
            )

            timer.modeSwitch.setVisible(
                self.settings.get(
                    "show_timer_mode",
                    True
                )
            )

            timer.delete_requested.connect(
                self.remove_timer
            )

            self.timers.append(
                timer
            )

            self.timerArea.addWidget(
                timer
            )

            timer.set_locked(
                self.settings["lock_desk"]
            )

    def remove_timer(self, timer):

        if timer in self.timers:
            self.timers.remove(timer)

        self.timerArea.removeWidget(timer)
        timer.deleteLater()

    def resizeEvent(self, event):
        super().resizeEvent(event)

        if hasattr(self, "drawerHandle"):
            self.update_drawer_handle()

        if (
            hasattr(self, "settingsMenu")
            and self.settingsMenu.is_open
        ):
            self.settingsMenu.reposition()


app = QApplication(sys.argv)

# Icône de l'application Qt
icon_path = resource_path("assets/SPP-Timer.png")
app.setWindowIcon(QIcon(str(icon_path)))

window = MainWindow()
window.show()

sys.exit(app.exec())