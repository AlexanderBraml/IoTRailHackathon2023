import sys
import time
from threading import Thread

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout

from gui.views.CompleteTracks import CompleteTracks
from gui.GUIPositionConfig import GUIPositionConfig
from gui.Position import Position
from gui.views.StatusLabels import StatusLabels, TrainState, TrainPosition


class GUI(QWidget):
    def __init__(self):
        super().__init__()

        config = GUIPositionConfig()
        self.complete_tracks = CompleteTracks(config, self)

        self.labels = StatusLabels()

        self.layout_layout = QVBoxLayout(self)
        self.layout_layout.addWidget(self.labels)
        self.layout_layout.addWidget(self.complete_tracks)

        self.setLayout(self.layout_layout)
        self.setFixedSize(850, 700)
        self.setWindowTitle('Team 1')

    def blink_balise(self, position: Position, times: int = 2) -> None:
        if position == Position.LEFT:
            self.complete_tracks.balise_left.blink(times)
        elif position == Position.RIGHT:
            self.complete_tracks.balise_right.blink(times)

    def blink_laser(self, position: Position, times: int = 2) -> None:
        if position == Position.LEFT:
            self.complete_tracks.laser_left.blink(times)
        elif position == Position.RIGHT:
            self.complete_tracks.laser_right.blink(times)

    def set_switch(self, switched: bool) -> None:
        self.complete_tracks.switch.switched = switched

    def set_speed(self, speed: float) -> None:
        self.labels.set_speed(speed)

    def set_state(self, state: TrainState) -> None:
        self.labels.set_state(state)

    def set_position(self, position: TrainPosition) -> None:
        self.labels.set_train_position(position)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    gui = GUI()
    gui.show()


    def test_interactive():
        gui.set_speed(10)
        gui.set_state(TrainState.RUN)
        gui.set_position(TrainPosition.LEFT_CORNER)
        time.sleep(14)
        gui.set_speed(15)
        gui.set_switch(True)
        time.sleep(2)
        gui.set_state(TrainState.SLOW)
        gui.set_position(TrainPosition.SLOW_STRAIGHT)
        time.sleep(1)
        gui.blink_balise(Position.LEFT, 3)
        gui.set_speed(5)
        time.sleep(5)
        gui.blink_balise(Position.RIGHT, 3)
        time.sleep(1)
        gui.set_speed(15)
        gui.set_state(TrainState.RUN)
        gui.set_position(TrainPosition.RIGHT_CORNER)
        time.sleep(1)
        gui.set_switch(False)
        time.sleep(3)
        gui.blink_laser(Position.RIGHT, 2)
        gui.set_position(TrainPosition.LOWER_STRAIGHT)
        time.sleep(2)
        gui.blink_laser(Position.LEFT, 2)
        time.sleep(1)
        gui.set_state(TrainState.DERAILED)
        gui.set_position(TrainPosition.LEFT_CORNER)
        time.sleep(3)
        gui.set_speed(0)
        gui.set_state(TrainState.STOPPED)


    t = Thread(target=test_interactive)
    t.start()

    app.exec_()
    t.join()
