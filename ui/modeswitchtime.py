from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPainter, QFont, QColor
from PySide6.QtWidgets import QWidget


class ModeSwitchTime(QWidget):

    mode_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.mode = "target"

        # Plus large pour contenir MODE + sélecteur
        self.setFixedSize(68, 54)
        self.setCursor(Qt.PointingHandCursor)

    def paintEvent(self, event):

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # ----------------------------------------------------------
        # CADRE
        # ----------------------------------------------------------

        painter.setPen(
            QColor("#00bfff")
        )
        painter.setBrush(
            Qt.NoBrush
        )

        painter.drawRoundedRect(
            1,
            1,
            self.width() - 2,
            self.height() - 2,
            6,
            6
        )

        # ----------------------------------------------------------
        # LABEL MODE
        # ----------------------------------------------------------

        font = QFont("Arial", 8)
        font.setBold(False)
        painter.setFont(font)

        painter.setPen(
            QColor("#008cff")
        )

        letters = ["M", "O", "D", "E"]

        for i, letter in enumerate(letters):

            painter.drawText(
                4,
                8 + i * 10,
                12,
                10,
                Qt.AlignCenter,
                letter
            )

        # ----------------------------------------------------------
        # TEXTE
        # ----------------------------------------------------------

        font = QFont("Arial", 6)
        font.setBold(False)
        painter.setFont(font)

        # Duration rouge si sélectionné
        if self.mode == "duration":
            painter.setPen(
                QColor("#ff0000")
            )
        else:
            painter.setPen(Qt.white)

        painter.drawText(
            18,
            2,
            self.width() - 20,
            18,
            Qt.AlignCenter,
            "Duration"
        )

        # Target rouge si sélectionné
        if self.mode == "target":
            painter.setPen(
                QColor("#ff0000")
            )
        else:
            painter.setPen(Qt.white)

        painter.drawText(
            18,
            self.height() - 20,
            self.width() - 20,
            18,
            Qt.AlignCenter,
            "Target"
        )

        # ----------------------------------------------------------
        # RAIL
        # ----------------------------------------------------------

        rail_x = 43
        rail_top = 20
        rail_bottom = self.height() - 20

        painter.setPen(Qt.NoPen)
        painter.setBrush(
            QColor("#888888")
        )

        painter.drawRoundedRect(
            rail_x - 2,
            rail_top,
            4,
            rail_bottom - rail_top,
            2,
            2
        )

        # ----------------------------------------------------------
        # CURSEUR
        # ----------------------------------------------------------

        if self.mode == "duration":
            knob_y = rail_top
        else:
            knob_y = rail_bottom

        painter.setBrush(
            QColor("#ff0000")
        )

        painter.drawEllipse(
            rail_x - 5,
            knob_y - 5,
            10,
            10
        )

    def mousePressEvent(self, event):

        if event.button() != Qt.LeftButton:
            return

        if self.mode == "target":
            self.mode = "duration"
        else:
            self.mode = "target"

        self.mode_changed.emit(
            self.mode
        )

        self.update()