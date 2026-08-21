from PySide6.QtCore import (
    Qt,
    Signal,
    QPropertyAnimation,
    QEasingCurve,
    QRect,
    QPropertyAnimation,
)
from PySide6.QtWidgets import (
    QFrame,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QDialog,
    QPushButton,
    QSlider,
    QSizePolicy,
)


class Switch(QWidget):

    toggled = Signal(bool)

    def __init__(self, checked=False, parent=None):
        super().__init__(parent)

        self.setFixedSize(44, 22)
        self.setCursor(Qt.PointingHandCursor)

        self._checked = checked
        self._thumb_x = 3 if not checked else 29

    def isChecked(self):
        return self._checked

    def setChecked(self, checked):
        checked = bool(checked)

        if self._checked == checked:
            return

        self._checked = checked
        self._thumb_x = 29 if checked else 3

        self.update()
        self.toggled.emit(checked)

    def mousePressEvent(self, event):

        if event.button() == Qt.LeftButton:
            self.setChecked(not self._checked)

        super().mousePressEvent(event)

    def paintEvent(self, event):

        from PySide6.QtGui import (
            QPainter,
            QColor,
            QBrush,
            QPen
        )

        painter = QPainter(self)
        painter.setRenderHint(
            QPainter.Antialiasing
        )

        # ----------------------------------------------------------
        # TRACK
        # ----------------------------------------------------------

        if self._checked:
            track_color = QColor("#00aaff")
        else:
            track_color = QColor("#555555")

        painter.setPen(
            QPen(track_color, 1)
        )

        painter.setBrush(
            QBrush(track_color)
        )

        painter.drawRoundedRect(
            1,
            3,
            42,
            16,
            8,
            8
        )

        # ----------------------------------------------------------
        # THUMB
        # ----------------------------------------------------------

        painter.setPen(Qt.NoPen)

        painter.setBrush(
            QBrush(QColor("#ffffff"))
        )

        painter.drawEllipse(
            self._thumb_x,
            5,
            12,
            12
        )

class SettingRow(QWidget):

    def __init__(self, text, checked=False, parent=None):
        super().__init__(parent)

        # Ligne compacte
        self.setFixedHeight(22)

        self.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Fixed
        )

        layout = QHBoxLayout(self)
        layout.setContentsMargins(
            0, 0, 0, 0
        )
        layout.setSpacing(0)

        self.label = QLabel(text)

        self.label.setFixedHeight(22)

        self.label.setAlignment(
            Qt.AlignLeft | Qt.AlignVCenter
        )

        self.label.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Fixed
        )

        self.checkbox = Switch(
            checked
        )

        layout.addWidget(
            self.label
        )

        layout.addStretch(0)

        layout.addWidget(
            self.checkbox
        )


class SettingsMenu(QFrame):

    save_requested = Signal()
    open_requested = Signal()
    start_all_requested = Signal()

    show_clock_changed = Signal(bool)
    sort_urgent_changed = Signal(bool)
    vibration_changed = Signal(bool)
    lock_changed = Signal(bool)
    auto_delete_changed = Signal(bool)
    auto_delete_delay_changed = Signal(int)
    show_timer_mode_changed = Signal(bool)

    closed = Signal()
    opened = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.parent_window = parent
        self.is_open = False

        self.setObjectName(
            "settingsPanel"
        )

        self.setStyleSheet("""
            QFrame#settingsPanel {
                background: #111;
                border: 1px solid #0af;
                border-top-left-radius: 16px;
                border-top-right-radius: 16px;
            }

            QLabel {
                color: white;
                background: transparent;
                border: none;
                font-size: 13px;
                padding: 0px;
                margin: 0px;
            }

            QPushButton {
                padding: 5px 12px;
                border: none;
                border-radius: 6px;
                background: #0af;
                color: #000;
                font-weight: bold;
            }

            QPushButton:hover {
                background: #666;
                color: #0af;
            }

            QPushButton:pressed {
                padding-top: 6px;
            }

            QSlider::groove:horizontal {
                height: 4px;
                background: #333;
                border-radius: 2px;
            }

            QSlider::handle:horizontal {
                width: 16px;
                height: 16px;
                margin: -6px 0;
                border-radius: 8px;
                background: #0af;
            }

            QSlider::sub-page:horizontal {
                background: #0af;
                border-radius: 2px;
            }
        """)

        # ==========================================================
        # LAYOUT PRINCIPAL
        # ==========================================================

        layout = QVBoxLayout()

        layout.setContentsMargins(
            68, 2, 64, 2
        )

        layout.setSpacing(4)

        layout.setAlignment(
            Qt.AlignTop
        )

        # ==========================================================
        # DRAWER HANDLE
        # ==========================================================

        self.handleZone = QFrame()
        self.handleZone.setFixedSize(42, 60)

        self.handleZone.setStyleSheet("""
            QFrame {
                background: transparent;
                border: none;
            }
        """)

        self.handleZone.mousePressEvent = self._handle_close_pressed

        self.drawerHandle = QFrame(self.handleZone)
        self.drawerHandle.setFixedSize(42, 4)
        self.drawerHandle.move(0, 28)

        self.drawerHandle.setStyleSheet("""
            QFrame {
                background: rgba(255,255,255,0.2);
                border: none;
                border-radius: 2px;
            }
        """)

        handleRow = QHBoxLayout()
        handleRow.setContentsMargins(0, 0, 0, 0)
        handleRow.setAlignment(Qt.AlignCenter)

        handleRow.addWidget(self.handleZone)

        layout.addLayout(handleRow)

        # ==========================================================
        # ACTIONS
        # ==========================================================

        actions = QHBoxLayout()

        actions.setContentsMargins(
            0, 0, 0, 1
        )

        actions.setSpacing(4)

        actions.addStretch()

        self.saveButton = QPushButton(
            "💾 Save"
        )

        self.openButton = QPushButton(
            "📂 Open"
        )

        self.startAllButton = QPushButton(
            "▶ Start ALL timers"
        )

        self.startAllButton.clicked.connect(
            self.start_all_requested.emit
        )

        self.closeButton = QPushButton(
            "✕"
        )

        self.infoButton = QPushButton("ⓘ")

        self.infoButton.setFixedSize(
            28,
            28
        )

        self.infoButton.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #0af;
                font-size: 20px;
                font-weight: bold;
                padding: 0px;
                margin: 0px;
            }

            QPushButton:hover {
                color: #4cf;
            }
        """)

        for button in (
            self.saveButton,
            self.openButton,
            self.startAllButton
        ):
            button.setFixedHeight(28)

        self.closeButton.setFixedSize(
            28, 28
        )

        self.closeButton.setStyleSheet("""
            QPushButton {
                background-color: #ff0000;
                color: #000000;
                border: none;
                border-radius: 6px;
                font-size: 16px;
                font-weight: bold;
                padding: 0px;
                margin: 0px;
            }

            QPushButton:hover {
                background-color: #666;
                color: #ff0000;
            }
        """)

        self.saveButton.clicked.connect(
            self.save_requested.emit
        )

        self.openButton.clicked.connect(
            self.open_requested.emit
        )

        self.startAllButton.clicked.connect(
            self.start_all_requested.emit
        )

        self.closeButton.clicked.connect(
            self.close_drawer
        )

        actions.addWidget(
            self.saveButton
        )

        actions.addWidget(
            self.openButton
        )

        actions.addWidget(
            self.startAllButton
        )

        actions.addWidget(
            self.closeButton
        )

        actions.addSpacing(
            6
        )

        actions.addWidget(
            self.infoButton
        )

        self.infoButton.clicked.connect(
            self.show_info_dialog
        )

        actions.addStretch()

        layout.addLayout(
            actions
        )

        # ==========================================================
        # SETTINGS
        # ==========================================================

        self.showClockRow = SettingRow(
            "Show Clock",
            True
        )

        self.showClockRow.label.setText(
            "Hide Clock"
        )

        self.showTimerModeRow = SettingRow(
            "Show Timer Mode",
            True
        )

        self.showTimerModeRow.label.setText(
            "Hide Timer Mode"
        )

        self.sortUrgentRow = SettingRow(
            "Sort urgent timer first",
            False
        )

        self.vibrationRow = SettingRow(
            "Vibration (smartphone only)",
            False
        )

        self.lockRow = SettingRow(
            "Lock desk",
            False
        )

        self.lockRow.label.setText(
            "Lock desk"
        )

        self.autoDeleteRow = SettingRow(
            "Auto delete expired timer",
            False
        )

        self.showClockCheck = (
            self.showClockRow.checkbox
        )

        self.showClockCheck.toggled.connect(
            self.show_clock_changed.emit
        )

        self.showTimerModeCheck = (
            self.showTimerModeRow.checkbox
        )

        self.showClockCheck.toggled.connect(
            lambda checked: self.showClockRow.label.setText(
                "Hide Clock" if checked else "Show Clock"
            )
        )

        self.sortUrgentCheck = (
            self.sortUrgentRow.checkbox
        )

        self.vibrationCheck = (
            self.vibrationRow.checkbox
        )
        self.vibrationCheck.setEnabled(False)

        self.lockCheck = (
            self.lockRow.checkbox
        )

        self.autoDeleteCheck = (
            self.autoDeleteRow.checkbox
        )

        self.showClockCheck.toggled.connect(
            self.show_clock_changed.emit
        )

        self.sortUrgentCheck.toggled.connect(
            self.sort_urgent_changed.emit
        )

        self.vibrationCheck.toggled.connect(
            self.vibration_changed.emit
        )

        self.lockCheck = (
            self.lockRow.checkbox
        )

        self.lockCheck.toggled.connect(
            self.lock_changed.emit
        )

        self.lockCheck.toggled.connect(
            lambda checked: self.lockRow.label.setText(
                "Unlock desk" if checked else "Lock desk"
            )
        )

        self.autoDeleteCheck.toggled.connect(
            self._auto_delete_toggled
        )

        self.showTimerModeCheck.toggled.connect(
            self.show_timer_mode_changed.emit
        )

        self.showTimerModeCheck.toggled.connect(
            lambda checked: self.showTimerModeRow.label.setText(
                "Hide Timer Mode" if checked else "Show Timer Mode"
            )
        )

        layout.addWidget(
            self.showClockRow
        )

        layout.addWidget(
            self.showTimerModeRow
        )

        layout.addWidget(
            self.sortUrgentRow
        )

        layout.addWidget(
            self.vibrationRow
        )

        layout.addWidget(
            self.lockRow
        )

        layout.addWidget(
            self.autoDeleteRow
        )

        # ==========================================================
        # AUTO DELETE DELAY
        # ==========================================================

        self.autoDeleteDelayContainer = QFrame()

        self.autoDeleteDelayContainer.setStyleSheet("""
            QFrame {
                background: transparent;
                border: none;
            }
        """)

        self.autoDeleteDelayContainer.setFixedHeight(
            22
        )

        delayLayout = QHBoxLayout()

        delayLayout.setContentsMargins(
            0, 0, 0, 0
        )

        delayLayout.setSpacing(20)

        self.autoDeleteDelayLabelTitle = QLabel(
            "Time before auto delete"
        )

        self.autoDeleteSlider = QSlider(
            Qt.Horizontal
        )

        self.autoDeleteSlider.setMinimum(
            0
        )

        self.autoDeleteSlider.setMaximum(
            120
        )

        self.autoDeleteSlider.setValue(
            10
        )

        self.autoDeleteDelayLabel = QLabel(
            "10s"
        )

        self.autoDeleteDelayLabel.setFixedWidth(
            35
        )

        delayLayout.addWidget(
            self.autoDeleteDelayLabelTitle
        )

        delayLayout.addWidget(
            self.autoDeleteSlider
        )

        delayLayout.addWidget(
            self.autoDeleteDelayLabel
        )

        self.autoDeleteDelayContainer.setLayout(
            delayLayout
        )

        layout.addWidget(
            self.autoDeleteDelayContainer
        )

        self.autoDeleteDelayContainer.hide()

        self.autoDeleteSlider.valueChanged.connect(
            self._auto_delete_delay_changed
        )

        self.setLayout(
            layout
        )

        # ==========================================================
        # ANIMATION
        # ==========================================================

        self.animation = QPropertyAnimation(
            self,
            b"geometry"
        )

        self.animation.setDuration(
            300
        )

        self.animation.setEasingCurve(
            QEasingCurve.OutCubic
        )

        self.hide()

    # ==============================================================
    # AUTO DELETE
    # ==============================================================

    def _auto_delete_delay_changed(
        self,
        value
    ):

        self.autoDeleteDelayLabel.setText(
            f"{value}s"
        )

        self.auto_delete_delay_changed.emit(
            value
        )

    # ==============================================================
    # AUTO DELETE VISIBILITY
    # ==============================================================

    def _auto_delete_toggled(
        self,
        checked
    ):

        self.autoDeleteDelayContainer.setVisible(
            checked
        )

        self.auto_delete_changed.emit(
            checked
        )

    # ==========================================================
    # INFORMATION / TERMS OF USE
    # ==========================================================

    def show_info_dialog(self):

        dialog = QDialog(self)
        dialog.setWindowTitle("INFO - SPP-Timers")
        dialog.setMinimumWidth(420)

        layout = QVBoxLayout(dialog)

        text = QLabel(
            """
        <h3>Privacy / Disclaimer</h3>
        <p>
          This application is free to use.<br>
          Your data always remains on your device <br>
          Nothing is upladed, stored, or shared with any server or third party.<br>
          All files remain your property and responsibility locally, on your device only.
        </p>
        <p>
          By using this application, you accept full responsibility for your usage.<br>
          This tool is provided "as is" without warranty of any kind.
        </p>
        <p>
          All content, code, and assets in this application are protected by copyright.<br>
          © Chris SEVESSAND / SARL SEVESSand Co
          <br>
          Commercial use, unauthorized reproduction or redistribution is prohibited<br>
          <br>
          For any development idea, please reach the author.<br>
          ... And have fun!
        </p>
        <p>
          Version: 1.0.0<br>
        </p>

            """
        )

        text.setWordWrap(True)

        layout.addWidget(text)

        dialog.exec()

    # ==============================================================
    # OPEN
    # ==============================================================

    def open_drawer(self):

        if not self.parent_window:
            return

        parent_rect = (
            self.parent_window.rect()
        )

        width = min(
            520,
            int(
                parent_rect.width() * 0.98
            )
        )

        self.layout().activate()

        height = (
            self.layout()
            .sizeHint()
            .height()
        )

        x = int(
            (
                parent_rect.width()
                - width
            ) / 2
        )

        closed_y = (
            parent_rect.height()
            + 10
        )

        open_y = (
            parent_rect.height()
            - height
            - 25
        )

        start_rect = QRect(
            x,
            closed_y,
            width,
            height
        )

        end_rect = QRect(
            x,
            open_y,
            width,
            height
        )

        self.setGeometry(
            start_rect
        )

        self.raise_()
        self.show()

        self.animation.stop()

        self.animation.setStartValue(
            start_rect
        )

        self.animation.setEndValue(
            end_rect
        )

        self.animation.start()

        self.is_open = True
        self.opened.emit()

    # ==============================================================
    # CLOSE
    # ==============================================================

    def close_drawer(self):

        if not self.is_open:
            return

        current = self.geometry()

        parent_height = (
            self.parent_window.height()
        )

        end_rect = QRect(
            current
        )

        end_rect.moveTop(
            parent_height + 10
        )

        self.animation.stop()

        self.animation.setStartValue(
            current
        )

        self.animation.setEndValue(
            end_rect
        )

        try:
            self.animation.finished.disconnect(
                self._finish_close
            )
        except RuntimeError:
            pass

        self.animation.finished.connect(
            self._finish_close
        )

        self.animation.start()

    def _handle_close_pressed(self, event):

        if event.button() == Qt.LeftButton:
            self.close_drawer()

    def _finish_close(self):

        try:
            self.animation.finished.disconnect(
                self._finish_close
            )
        except RuntimeError:
            pass

        self.hide()

        self.is_open = False

        self.closed.emit()

    # ==============================================================
    # TOGGLE
    # ==============================================================

    def toggle(self):

        if self.is_open:
            self.close_drawer()
        else:
            self.open_drawer()

    # ==============================================================
    # RESIZE
    # ==============================================================

    def update_position(self):

        if not self.is_open:
            return

        self.open_drawer()

    # ==============================================================
    # REPOSITION
    # ==============================================================

    def reposition(self):

        if (
            not self.parent_window
            or not self.is_open
        ):
            return

        parent_rect = (
            self.parent_window.rect()
        )

        width = min(
            520,
            int(
                parent_rect.width() * 0.98
            )
        )

        height = self.height()

        x = int(
            (
                parent_rect.width()
                - width
            ) / 2
        )

        y = (
            parent_rect.height()
            - height
            - 25
        )

        self.setGeometry(
            x,
            y,
            width,
            height
        )