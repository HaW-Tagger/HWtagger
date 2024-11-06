from PySide6 import QtCore
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QLabel, QTreeView


class ScaledLabel(QLabel):
    def __init__(self, *args, **kwargs):
        QLabel.__init__(self)
        self._pixmap = self.pixmap()
        self._resised = False

    def resizeEvent(self, event):
        self.setPixmap(self._pixmap)

    def setPixmap(self, pixmap):  # overiding setPixmap
        if not pixmap: return
        self._pixmap = pixmap
        return QLabel.setPixmap(self, self._pixmap.scaled(
            self.frameSize(),
            QtCore.Qt.AspectRatioMode.KeepAspectRatio))

class ConflictsTreeView(QTreeView):
    rightClicked = Signal()
    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.RightButton:
            self.rightClicked.emit()
        else:
            super().mouseReleaseEvent(event)




