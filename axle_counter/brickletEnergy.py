from tinkerforge.ip_connection import IPConnection
from tinkerforge.brick_master import BrickMaster
from tinkerforge.bricklet_energy_monitor import BrickletEnergyMonitor

HOST = "localhost"
PORT = 4223
UID_master = "64siN1"
UID_Energy = "Usb"

class Measurement:
    def __init__(self):
        self.current_event = []
        self.isWorking = True

    def cb_current(self, _, current, *args):
        current = abs(current)
        if current > 50:
            self.current_event.append(current)
        else:
            # abort if there are not enough values in the current event list
            if len(self.current_event) < 4:
                return
            diffs = []
            # find the biggest change in current
            for idx, meas in enumerate(self.current_event):
                if idx+1 < len(self.current_event):
                    diffs.append(abs(self.current_event[idx+1] - meas))

            # find where in the event it happened
            index = diffs.index(max(diffs))

            # if it's in the first part of the event, it worked, if not the switch is blocked
            if (part:=len(self.current_event)/index) < 13:
                print(f"Weiche hat Endlage erreicht, #Debug: {part}")
                self.isWorking = True
            else:
                print(f"Weiche ist blockiert, #Debug: {part}")
                self.isWorking = False

            self.current_event = []


if __name__ == "__main__":
    ipcon = IPConnection() # Create IP connection
    master = BrickMaster(UID_master, ipcon) # Create device object
    ipcon.connect(HOST, PORT)

    measurement = Measurement()
    bricklet = BrickletEnergyMonitor(UID_Energy, ipcon)

    bricklet.register_callback(bricklet.CALLBACK_ENERGY_DATA, measurement.cb_current)

    bricklet.set_energy_data_callback_configuration(15, False)

    input("Press any key to cancel")
    ipcon.disconnect()
