from dataclasses import dataclass


@dataclass
class GUIPositionConfig:
    margin_top: int = 50
    mgn_left: int = 0
    radius: int = 300
    straigth_length: int = 500
    balise_width: int = 40
    balise_height: int = 30
    switch_straight_length: int = 75
    distance_other_rail: int = 50
    distance_other_rail_left: int = 130
    laser_width: int = 30
    laser_height: int = 45
    laser_distance_x: int = 50
    laser_distance_y: int = 5

    @property
    def laser_dims(self) -> tuple[int, int, int]:
        return self.margin_top + self.radius + self.laser_distance_y, 30, 45  # y, width, height
