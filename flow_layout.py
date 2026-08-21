from PySide6.QtCore import QRect, QSize, Qt
from PySide6.QtWidgets import QLayout, QWidgetItem


class FlowLayout(QLayout):

    def __init__(self, parent=None, margin=0, spacing=10):
        super().__init__(parent)

        self.setContentsMargins(margin, margin, margin, margin)
        self.setSpacing(spacing)

        self.items = []

    def addItem(self, item):
        self.items.append(item)

    def count(self):
        return len(self.items)

    def itemAt(self, index):
        if 0 <= index < len(self.items):
            return self.items[index]
        return None

    def takeAt(self, index):
        if 0 <= index < len(self.items):
            return self.items.pop(index)
        return None

    def expandingDirections(self):
        return Qt.Orientation(0)

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        return self.doLayout(
            QRect(0, 0, width, 0),
            True
        )

    def setGeometry(self, rect):
        super().setGeometry(rect)

        self.doLayout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()

        for item in self.items:
            size = size.expandedTo(item.minimumSize())

        margins = self.contentsMargins()

        size += QSize(
            margins.left() + margins.right(),
            margins.top() + margins.bottom()
        )

        return size

    def doLayout(self, rect, testOnly):

        spacing = self.spacing()

        # Construire les lignes
        lines = []
        currentLine = []
        currentWidth = 0
        currentHeight = 0

        for item in self.items:

            widget = item.widget()

            if widget is None:
                continue

            width = item.sizeHint().width()
            height = item.sizeHint().height()

            neededWidth = (
                width
                if not currentLine
                else currentWidth + spacing + width
            )

            if currentLine and neededWidth > rect.width():

                lines.append(
                    (currentLine, currentWidth, currentHeight)
                )

                currentLine = []
                currentWidth = 0
                currentHeight = 0

            currentLine.append(item)

            if currentWidth == 0:
                currentWidth = width
            else:
                currentWidth += spacing + width

            currentHeight = max(currentHeight, height)

        if currentLine:
            lines.append(
                (currentLine, currentWidth, currentHeight)
            )

        # Positionner les lignes centrées
        y = rect.y()

        for line, lineWidth, lineHeight in lines:

            x = rect.x() + (rect.width() - lineWidth) // 2

            for item in line:

                width = item.sizeHint().width()
                height = item.sizeHint().height()

                if not testOnly:
                    item.setGeometry(
                        QRect(
                            x,
                            y,
                            width,
                            height
                        )
                    )

                x += width + spacing

            y += lineHeight + spacing

        return y - rect.y() - spacing