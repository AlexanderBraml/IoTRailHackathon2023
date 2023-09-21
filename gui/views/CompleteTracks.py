from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QPainter

from gui.views.Balise import Balise
from gui.GUIPositionConfig import GUIPositionConfig
from gui.views.Laser import Laser
from gui.Position import Position
from gui.views.RailSwitch import RailSwitch


class CompleteTracks(QtWidgets.QWidget):
    def __init__(self, widget_config: GUIPositionConfig, parent):
        super(CompleteTracks, self).__init__(parent)

        self.setFixedSize(850, 500)

        self.wc: GUIPositionConfig = widget_config

        self.switch = RailSwitch(self.wc, self)
        self.balise_left = Balise(Position.LEFT, self.wc, self)
        self.balise_right = Balise(Position.RIGHT, self.wc, self)
        self.laser_left = Laser(Position.LEFT, self.wc, self)
        self.laser_right = Laser(Position.RIGHT, self.wc, self)

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QtCore.Qt.black)
        painter.setBrush(QtCore.Qt.white)

        # Train tracks
        painter.drawArc(self.wc.mgn_left, self.wc.margin_top, self.wc.radius, self.wc.radius, 90 * 16, 180 * 16)
        painter.drawArc(self.wc.mgn_left + self.wc.straigth_length, self.wc.margin_top, self.wc.radius, self.wc.radius,
                        -90 * 16, 180 * 16)
        end_corner_left_x = self.wc.mgn_left + self.wc.radius // 2
        end_corner_right_x = end_corner_left_x + self.wc.straigth_length
        painter.drawLine(end_corner_left_x, self.wc.radius + self.wc.margin_top,
                         end_corner_right_x, self.wc.radius + self.wc.margin_top)

        # Upper left line
        start_left_switch_x = end_corner_left_x + self.wc.switch_straight_length
        painter.drawLine(end_corner_left_x, self.wc.margin_top, start_left_switch_x, self.wc.margin_top)
        painter.drawLine(end_corner_right_x - self.wc.switch_straight_length, self.wc.margin_top,
                         end_corner_right_x, self.wc.margin_top)

        # Other rail
        painter.drawLine(end_corner_left_x + self.wc.distance_other_rail_left,
                         self.wc.margin_top + self.wc.distance_other_rail,
                         end_corner_right_x - self.wc.distance_other_rail_left,
                         self.wc.margin_top + self.
                         wc.distance_other_rail)

        painter.end()
