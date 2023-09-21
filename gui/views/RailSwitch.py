from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QPainter

from gui import GUIPositionConfig
from gui.GUIPositionConfig import GUIPositionConfig


class RailSwitch(QtWidgets.QWidget):
    def __init__(self, widget_config: GUIPositionConfig, parent):
        super().__init__(parent)

        self.wc: GUIPositionConfig = widget_config
        self._switched: bool = False

        self.setFixedSize(850, 500)

    def paintSwitch(self) -> None:
        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QtCore.Qt.black)
        painter.setBrush(QtCore.Qt.white)

        end_corner_left_x = self.wc.mgn_left + self.wc.radius // 2
        end_corner_right_x = end_corner_left_x + self.wc.straigth_length
        start_left_switch_x = end_corner_left_x + self.wc.switch_straight_length

        if self.switched:
            painter.drawLine(start_left_switch_x, self.wc.margin_top,
                             end_corner_left_x + self.wc.distance_other_rail_left,
                             self.wc.margin_top + self.wc.distance_other_rail)
            painter.drawLine(end_corner_right_x - self.wc.distance_other_rail_left,
                             self.wc.margin_top + self.wc.distance_other_rail,
                             end_corner_right_x - self.wc.switch_straight_length, self.wc.margin_top)
        else:
            painter.drawLine(start_left_switch_x, self.wc.margin_top,
                             end_corner_right_x - self.wc.switch_straight_length, self.wc.margin_top)

        painter.end()

    def paintEvent(self, event):
        self.paintSwitch()

    @property
    def switched(self):
        return self._switched

    @switched.setter
    def switched(self, value):
        self._switched = value
        self.repaint()
