import time
from threading import Thread

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QPainter

from gui import GUIPositionConfig
from gui.GUIPositionConfig import GUIPositionConfig
from gui.Position import Position


class Balise(QtWidgets.QWidget):
    def __init__(self, position: Position, widget_config: GUIPositionConfig, parent):
        super().__init__(parent)

        self.wc: GUIPositionConfig = widget_config

        self.color = QtCore.Qt.yellow

        self.position = position

        self.setFixedSize(850, 500)

    def paintBalise(self) -> None:
        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)

        end_corner_left_x = self.wc.mgn_left + self.wc.radius // 2
        end_corner_right_x = end_corner_left_x + self.wc.straigth_length

        painter.setPen(QtCore.Qt.black)
        painter.setBrush(self.color)
        if self.position == Position.RIGHT:
            painter.drawRect(end_corner_right_x, self.wc.margin_top - self.wc.balise_height // 2,
                             self.wc.balise_width, self.wc.balise_height)
        elif self.position == Position.LEFT:
            painter.drawRect(end_corner_left_x, self.wc.margin_top - self.wc.balise_height // 2,
                             self.wc.balise_width, self.wc.balise_height)

        painter.end()

    def blink(self, times: int = 3) -> None:
        def blink_target(times: int) -> None:
            for _ in range(times):
                time.sleep(0.3)
                self.color = QtCore.Qt.red
                self.repaint()
                time.sleep(0.3)
                self.color = QtCore.Qt.yellow
                self.repaint()

        thread = Thread(target=blink_target, args=(times,))
        thread.start()

    def paintEvent(self, event):
        self.paintBalise()
