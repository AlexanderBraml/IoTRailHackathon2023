import time
from threading import Thread

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QPainter

from gui.GUIPositionConfig import GUIPositionConfig
from gui.Position import Position


class Laser(QtWidgets.QWidget):
    def __init__(self, position: Position, widget_config: GUIPositionConfig, parent):
        super().__init__(parent)

        self.wc: GUIPositionConfig = widget_config
        self._switched: bool = False
        self.position = position

        self.color = QtCore.Qt.blue

        self.setFixedSize(850, 500)

    def paintLaser(self) -> None:
        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)

        end_corner_left_x = self.wc.mgn_left + self.wc.radius // 2
        end_corner_right_x = end_corner_left_x + self.wc.straigth_length

        painter.setPen(QtCore.Qt.black)
        painter.setBrush(self.color)

        laser_left_x = end_corner_left_x + self.wc.laser_distance_x
        laser_right_x = end_corner_right_x - self.wc.laser_distance_x

        if self.position == Position.LEFT:
            painter.drawRect(laser_left_x, *self.wc.laser_dims)
            painter.drawRect(laser_left_x + self.wc.laser_width + 5, *self.wc.laser_dims)
        elif self.position == Position.RIGHT:
            painter.drawRect(laser_right_x, *self.wc.laser_dims)
            painter.drawRect(laser_right_x - self.wc.laser_width - 5, *self.wc.laser_dims)

        painter.end()

    def blink(self, times: int = 3) -> None:
        def blink_target(times: int) -> None:
            for _ in range(times):
                time.sleep(0.3)
                self.color = QtCore.Qt.red
                self.repaint()
                time.sleep(0.3)
                self.color = QtCore.Qt.blue
                self.repaint()

        thread = Thread(target=blink_target, args=(times,))
        thread.start()

    def paintEvent(self, event):
        self.paintLaser()
