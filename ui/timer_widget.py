from datetime import datetime, timedelta

from ui.modeswitchtime import ModeSwitchTime

from PySide6.QtCore import QTimer, Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QPushButton,
    QLineEdit,
    QComboBox,
    QHBoxLayout,
    QSizePolicy,
    QVBoxLayout,
    QSizePolicy
)


class TimerWidget(QFrame):
    delete_requested = Signal(object)

    def __init__(self):
        super().__init__()

        self.setObjectName("timerWidget")

        self.setFrameShape(QFrame.Box)
        self.setFrameShadow(QFrame.Plain)
        self.setLineWidth(1)

        self.target = None
        self.duration_seconds = None
        self.started_at = None
        self.mode = "target"
        self.running = False

        self.auto_delete = False
        self.auto_delete_delay = 10
        self.blink_state = False

        # ==========================================================
        # MODE TARGET / DURATION
        # ==========================================================

        self.modeSwitch = ModeSwitchTime()

        self.modeSwitch.setContentsMargins(0, 0, 0, 0)
        
        self.modeSwitch.mode_changed.connect(
            self.set_mode
        )

        # ==========================================================
        # STYLE GENERAL DU TIMER
        # ==========================================================

        self.setStyleSheet("""
            QFrame#timerWidget {
                background-color: #111;
                border: 1px solid #00aaff;
                border-radius: 8px;
            }

            QFrame#timerWidget QLabel {
                border: none;
                background: transparent;
            }

            QFrame#timerWidget QLineEdit {
                background-color: #000;
                color: white;
                border: 1px solid #333;
                padding: 2px 4px;
                border-radius: 5px;
            }

            QFrame#timerWidget QComboBox {
                background-color: #000;
                color: white;
                border: 1px solid #333;
                padding: 2px 2px;
                border-radius: 5px;
            }

            QFrame#timerWidget QComboBox::drop-down {
                width: 12px;
                border: none;
            }
        """)

        # ==========================================================
        # NOM
        # ==========================================================

        self.name = QLineEdit("New event")
        self.name.setFixedHeight(26)

        # ==========================================================
        # HEURE / DUREE
        # ==========================================================

        self.hourCombo = QComboBox()
        self.minuteCombo = QComboBox()
        self.secondCombo = QComboBox()

        self.hourCombo.setEditable(True)
        self.minuteCombo.setEditable(True)
        self.secondCombo.setEditable(True)

        self.hourCombo.lineEdit().setAlignment(
            Qt.AlignCenter
        )

        self.minuteCombo.lineEdit().setAlignment(
            Qt.AlignCenter
        )

        self.secondCombo.lineEdit().setAlignment(
            Qt.AlignCenter
        )    
        
        for hour in range(24):
            self.hourCombo.addItem(f"{hour:02}")

        for minute in range(60):
            self.minuteCombo.addItem(f"{minute:02}")

        for second in range(60):
            self.secondCombo.addItem(f"{second:02}")

        self.hourCombo.setCurrentIndex(0)
        self.minuteCombo.setCurrentIndex(0)
        self.secondCombo.setCurrentIndex(0)

        for combo in (
            self.hourCombo,
            self.minuteCombo,
            self.secondCombo
        ):
            combo.setFixedSize(46, 28)

        # ==========================================================
        # BOUTON PLAY
        # ==========================================================

        self.startButton = QPushButton("▶")
        self.startButton.setFixedSize(26, 26)

        self.startButton.setStyleSheet("""
            QPushButton {
                background-color: #00aaff;
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
                color: #00aaff;
            }
        """)

        # ==========================================================
        # BOUTON DELETE
        # ==========================================================

        self.deleteButton = QPushButton("✕")
        self.deleteButton.setFixedSize(26, 26)

        self.deleteButton.setStyleSheet("""
            QPushButton {
                background-color: #ff0000;
                color: #ffffff;
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

        # ==========================================================
        # CONNEXIONS
        # ==========================================================

        self.startButton.clicked.connect(
            self.start
        )

        self.deleteButton.clicked.connect(
            lambda: self.delete_requested.emit(self)
        )

        # ==========================================================
        # COMPTEUR
        # ==========================================================

        self.counter = QLabel("--:--:--")
        self.counter.setMinimumWidth(120)
        self.counter.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Preferred
        )       
        self.counter.setAlignment(Qt.AlignCenter)
        self.counter.setFixedHeight(30)

        self.counter.setStyleSheet("""
            color: #00aaff;
            font-size: 28px;
            font-weight: bold;
        """)

        # ==========================================================
        # LIGNE CONTROLES
        # ==========================================================

        controls = QHBoxLayout()
        controls.setContentsMargins(0, 0, 0, 0)
        controls.setSpacing(4)

        controls.addStretch()

        controls.addWidget(self.hourCombo)

        separator1 = QLabel(":")
        separator1.setAlignment(Qt.AlignCenter)
        controls.addWidget(separator1)

        controls.addWidget(self.minuteCombo)

        separator2 = QLabel(":")
        separator2.setAlignment(Qt.AlignCenter)
        controls.addWidget(separator2)

        controls.addWidget(self.secondCombo)

        controls.addWidget(self.startButton)
        controls.addWidget(self.deleteButton)

        controls.addStretch()

        # ==========================================================
        # LAYOUT DU TIMER
        # ==========================================================

        layout = QVBoxLayout()

        layout.setContentsMargins(8, 3, 8, 3)
        layout.setSpacing(2)

        layout.addWidget(self.name)
        layout.addLayout(controls)

        # ==========================================================
        # COMPTEUR + MODE SWITCH
        # ==========================================================

        counterRow = QHBoxLayout()

        counterRow.setContentsMargins(0, 0, 0, 0)
        counterRow.setSpacing(24)

        counterRow.addStretch()
        counterRow.addWidget(self.modeSwitch)
        counterRow.addWidget(self.counter)
        counterRow.addStretch()

        layout.addLayout(counterRow)

        self.setLayout(layout)

        # ==========================================================
        # TIMER
        # ==========================================================

    # ==============================================================
    # COULEUR DU CADRE
    # ==============================================================

    def set_border_color(self, color):

        self.setStyleSheet(f"""
            QFrame#timerWidget {{
                background-color: #111;
                border: 2px solid {color};
                border-radius: 8px;
            }}

            QFrame#timerWidget QLabel {{
                border: none;
                background: transparent;
            }}

            QFrame#timerWidget QLineEdit,
            QFrame#timerWidget QComboBox {{
                background-color: #000;
                color: white;
                border: 1px solid #333;
                padding: 2px 2px;
                border-radius: 5px;
            }}
        """)

    # ==============================================================
    # LOCK DESK
    # ==============================================================

    def set_locked(self, locked):

        self.name.setReadOnly(locked)

        self.hourCombo.setEnabled(not locked)
        self.minuteCombo.setEnabled(not locked)
        self.secondCombo.setEnabled(not locked)

        self.startButton.setEnabled(not locked)
        self.deleteButton.setEnabled(not locked)

    # ==============================================================
    # MODE TARGET / DURATION
    # ==============================================================

    def set_mode(self, mode):

        self.mode = mode

        if self.running:
            self.start()

    # ==========================================================
    # EXPORT JSON
    # ==========================================================

    def to_event_data(self):
        """
        Convertit ce TimerWidget vers le format JSON SPP-Timers 1.0.
        """

        time_value = (
            f"{self.hourCombo.currentText()}:"
            f"{self.minuteCombo.currentText()}:"
            f"{self.secondCombo.currentText()}"
        )

        return {
            "id": str(id(self)),
            "name": self.name.text(),
            "time": time_value,
            "target": (
                int(self.target.timestamp() * 1000)
                if self.target is not None
                else None
            ),
            "fired": False,
            "deleteIn": None,
            "remaining": None,
            "expiredAt": None,
            "duration": None
        }

    def from_event_data(self, event_data):
        
        """
        Charge un événement au format JSON SPP-Timers 1.0.
        """

        self.name.setText(
            event_data.get("name", "")
        )

        time_value = event_data.get(
            "time",
            "00:00:00"
        )

        try:
            hour, minute, second = (
                int(value)
                for value in time_value.split(":")
            )

            self.hourCombo.setCurrentIndex(hour)
            self.minuteCombo.setCurrentIndex(minute)
            self.secondCombo.setCurrentIndex(second)

        except (ValueError, TypeError):
            self.hourCombo.setCurrentIndex(0)
            self.minuteCombo.setCurrentIndex(0)
            self.secondCombo.setCurrentIndex(0)

        target = event_data.get("target")

        if target is not None:
            self.target = datetime.fromtimestamp(
                target / 1000
            )
        else:
            self.target = None

        self.running = False

        self.update(
            datetime.now(),
            datetime.now().replace(microsecond=0)
        )

    # ==========================================================
    # START
    # ==========================================================

    def start(self):

        now = datetime.now()

        self.started_at = now
        self.countdown_start = (
            now.replace(microsecond=0)
            + timedelta(seconds=1)
        )

        self.expired_at = None
        self.running = True

        hours = self.hourCombo.currentIndex()
        minutes = self.minuteCombo.currentIndex()
        seconds = self.secondCombo.currentIndex()

        # ==========================================================
        # DURATION
        # ==========================================================

        if self.mode == "duration":

            duration_seconds = (
                hours * 3600
                + minutes * 60
                + seconds
            )

            self.duration_seconds = duration_seconds

            self.target = self.countdown_start + timedelta(
                seconds=duration_seconds
            )

        # ==========================================================
        # TARGET TIME
        # ==========================================================

        else:

            self.target = now.replace(
                hour=hours,
                minute=minutes,
                second=seconds,
                microsecond=0
            )

            if self.target <= now:

                self.target = self.target.replace(
                    day=self.target.day + 1
                )

    def update(self, now, current_second):

        # ==========================================================
        # TIMER ARRETE
        # ==========================================================

        if self.target is None:
            self.counter.setText("--:--:--")
            return

        if not self.running:

            hours = self.hourCombo.currentIndex()
            minutes = self.minuteCombo.currentIndex()
            seconds_value = self.secondCombo.currentIndex()

            # ------------------------------------------------------
            # DURATION
            # ------------------------------------------------------

            if self.mode == "duration":

                seconds = (
                    hours * 3600
                    + minutes * 60
                    + seconds_value
                )

            # ------------------------------------------------------
            # TARGET TIME
            # ------------------------------------------------------

            else:

                target = now.replace(
                    hour=hours,
                    minute=minutes,
                    second=seconds_value,
                    microsecond=0
                )

                if target <= now:
                    target += timedelta(days=1)

                seconds = int(
                    (target - now).total_seconds()
                )

            # Affichage
            h = seconds // 3600
            m = (seconds % 3600) // 60
            s = seconds % 60

            self.counter.setText(
                f"{h:02}:{m:02}:{s:02}"
            )

            return

        # ==========================================================
        # TIMER EN COURS
        # ==========================================================

        if not self.target:
            return

        remaining = self.target - now

        # ==========================================================
        # TEMPS NORMAL
        # ==========================================================

        # Nombre de secondes civiles restantes.
        #
        # Exemple :
        # target = 12:35:00
        #
        # 12:34:59.xxx -> 1
        # 12:35:00.xxx -> 0
        #
        # Le zéro appartient donc toujours au décompte.

        if current_second <= self.target.replace(
            microsecond=0
        ):

            if self.mode == "duration":

                # --------------------------------------------------
                # PHASE 1 : ARMEMENT
                # --------------------------------------------------

                if now < self.countdown_start:

                    seconds = self.duration_seconds

                # --------------------------------------------------
                # PHASE 2 : DECOMPTE SYNCHRONISE
                # --------------------------------------------------

                else:

                    elapsed_seconds = int(
                        (
                            current_second
                            - self.countdown_start
                        ).total_seconds()
                    )

                    seconds = (
                        self.duration_seconds
                        - elapsed_seconds
                    )

            else:

                target_second = self.target.replace(
                    microsecond=0
                )

                seconds = int(
                    (target_second - current_second).total_seconds()
                )

            # ------------------------------------------------------
            # CIBLE ATTEINTE : 00
            # ------------------------------------------------------

            if seconds <= 0:

                self.counter.setText(
                    "00:00:00"
                )

                self.counter.setStyleSheet("""
                    color:#f00;
                    font-size:28px;
                    font-weight:bold;
                """)

                self.blink_state = not self.blink_state

                if self.blink_state:
                    self.set_border_color("#f00")
                else:
                    self.set_border_color("#111")

                return

            h = seconds // 3600
            m = (seconds % 3600) // 60
            s = seconds % 60

            self.counter.setText(
                f"{h:02}:{m:02}:{s:02}"
            )
            
            # ------------------------------------------------------
            # COULEURS SPP
            # ------------------------------------------------------

            if seconds <= 5:
                color = "#f00"

            elif seconds <= 10:
                color = "#f80"

            elif seconds <= 20:
                color = "#ff0"

            else:
                color = "#0af"

            self.counter.setStyleSheet(f"""
                color:{color};
                font-size:28px;
                font-weight:bold;
            """)

            self.set_border_color(color)

            return

        # ==========================================================
        # OVERTIME
        # ==========================================================

        self.modeSwitch.hide()

        # La cible est dépassée.
        #
        # Le zéro a déjà été affiché pendant la seconde de la cible.
        # L'OVERTIME commence donc à la seconde suivante :
        #
        # 12:35:00.xxx -> 0
        # 12:35:01.xxx -> +1
        # 12:35:02.xxx -> +2

        overtime_seconds = int(
            (
                current_second
                - self.target.replace(microsecond=0)
            ).total_seconds()
        )

        if overtime_seconds < 1:
            overtime_seconds = 1

        self.counter.setText(
            f"+{overtime_seconds} OVERTIME"
        )

        self.counter.setStyleSheet("""
            color:#00ff88;
            font-size:20px;
            font-weight:bold;
        """)

        self.set_border_color("#00ff88")

        # ==========================================================
        # AUTO DELETE
        # ==========================================================

        if self.auto_delete:

            remaining_before_delete = (
                self.auto_delete_delay
                - overtime_seconds
            )

            # ------------------------------------------------------
            # CLIGNOTEMENT
            # ------------------------------------------------------

            if remaining_before_delete <= 1:

                self.blink_state = not self.blink_state

                if self.blink_state:
                    self.set_border_color("#ffffff")
                else:
                    self.set_border_color("#00ff88")

            # ------------------------------------------------------
            # DESTRUCTION
            # ------------------------------------------------------

            if overtime_seconds >= self.auto_delete_delay:

                self.delete_requested.emit(
                    self
                )

        return
            
        # ==========================================================
        # COMPTEUR NORMAL
        # ==========================================================

        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60

        self.counter.setText(
            f"{h:02}:{m:02}:{s:02}"
        )

        # ==========================================================
        # COULEURS SPP
        # ==========================================================

        if seconds <= 5:
            color = "#f00"

        elif seconds <= 10:
            color = "#f80"

        elif seconds <= 20:
            color = "#ff0"

        else:
            color = "#0af"

        self.set_border_color(color)
            
        self.counter.setStyleSheet(f"""
            color:{color};
            font-size:28px;
            font-weight:bold;
        """)

        self.set_border_color(color)