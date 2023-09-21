from tinkerforge.ip_connection import IPConnection
from tinkerforge.brick_master import BrickMaster
from tinkerforge.bricklet_voltage_current_v2 import BrickletVoltageCurrentV2

HOST = "localhost"
PORT = 4223
UID_master = "64siN1" # Change XXYYZZ to the UID of your Master Brick
UID_brickVoltage = "26iT"


class CurrentMeasurement:
    def __init__(self):
        pass

    def cb_current(self, current):
        print(current)
        if abs(current) >= 4.5 * 1000:
            print(f"Weiche hat {'linke' if current > 0 else 'rechte'} Endlage erreicht, Current Messung: {current}")
        if abs(current) < 4.5 * 1000:
            print(f"Weiche ist blockiert, Messung: {current}")

def printTest(data):
    print(data)

if __name__ == "__main__":
    ipcon = IPConnection() # Create IP connection
    master = BrickMaster(UID_master, ipcon) # Create device object
    ipcon.connect(HOST, PORT)

    bricklets = master.get_bricklets_enabled()

    measurement = CurrentMeasurement()

    brickVoltage = BrickletVoltageCurrentV2(UID_brickVoltage, ipcon)

    brickVoltage.register_callback(brickVoltage.CALLBACK_CURRENT, measurement.cb_current)

    brickVoltage.set_current_callback_configuration(1000, True, ">", 0.1*1000, 0)


    input("Press any key to cancel")
    ipcon.disconnect()
    # get list of current measurements
