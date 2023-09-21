from enum import Enum

from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout


class TrainState(Enum):
    RUN = 'Fahrt'
    STOPPED = 'Angehalten'
    SLOW = 'Langsamfahrt'
    DERAILED = 'Wagen verloren'


class TrainPosition(Enum):
    LEFT_CORNER = 'Kurve Links'
    UPPER_STRAIGHT = 'Gerade Oben'
    SLOW_STRAIGHT = 'Langsamfahrt-Zone'
    RIGHT_CORNER = 'Kurve Rechts'
    LOWER_STRAIGHT = 'Gerade Unten'


class StatusLabels(QWidget):
    def __init__(self):
        super().__init__()
        self.speed_label = QLabel('Aktuelle Geschwindigkeit: ')
        self.state_label = QLabel('Aktueller Status: ')
        self.position_label = QLabel('Aktuelle Position: ')

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.speed_label)
        self.layout.addWidget(self.state_label)
        self.layout.addWidget(self.position_label)

        self.setLayout(self.layout)
        self.setFixedSize(850, 200)

    def set_speed(self, speed: float) -> None:
        assert 0 <= speed <= 300
        self.speed_label.setText(f'Aktuelle Geschwindigkeit: {speed}')

    def set_state(self, state: TrainState) -> None:
        assert isinstance(state, TrainState)
        self.state_label.setText(f'Aktueller Status: {state.value}')

    def set_train_position(self, position: TrainPosition) -> None:
        assert isinstance(position, TrainPosition)
        self.position_label.setText(f'Aktuelle Position: {position.value}')
