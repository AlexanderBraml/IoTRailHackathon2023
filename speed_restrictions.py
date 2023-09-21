#!/usr/bin/env python
# -*- coding: utf-8 -*-

# connection details for the main brick and NFC bricklet
BRICK_HOST = "192.168.10.249"
BRICK_PORT = 4223
BRICK_UID = "22Nw"

# connection details for the Loconet server
LOCONET_HOST = "192.168.10.70"
LOCONET_PORT = 1234

# start and end NFC tags for the construction area
START_CONSTRUCTION_TAG = "0x04 0x71 0x9D 0xB2 0xB2 0x6C 0x81"
END_CONSTRUCTION_TAG = "0x04 0x4B 0x9D 0xB2 0xB2 0x6C 0x81"

# start switch + tag of the branch
START_SWITCH_TAG = "0x04 0x9F 0x27 0x22 0xBC 0x73 0x80"
START_SWITCH_ID = 2

# end switch + tag of the branch
END_SWITCH_TAG = "0x04 0xEE 0xD8 0xE2 0x1D 0x70 0x80"
END_SWITCH_ID = 3

import socket
from tinkerforge.ip_connection import IPConnection
from tinkerforge.bricklet_nfc import BrickletNFC

# helper functions to generate Loconet commands


def convert_address(address):
    part_one = address % 128
    part_two = int((address - part_one) / 128)
    return [part_one, part_two]


def calculate_checksum(parts):
    return 255 - (parts[0] ^ parts[1] ^ parts[2])


def verify_command(parts):
    return True if parts[0] ^ parts[1] ^ parts[2] ^ parts[3] else False


def get_binary_command(parts):
    command = (
        f"SEND "
        + f"{parts[0]:02X}"
        + f" "
        + f"{parts[1]:02X}"
        + f" "
        + f"{parts[2]:02X}"
        + f" "
        + f"{parts[3]:02X}"
        + f" \r"
    ).encode()
    return command


def get_answer(parts):
    parts.append(calculate_checksum(parts))
    if verify_command(parts):
        return (
            f"{parts[0]:02X}"
            + f" "
            + f"{parts[1]:02X}"
            + f" "
            + f"{parts[2]:02X}"
            + f" "
            + f"{parts[3]:02X}"
        ).encode()


# Loconet: confirm that changing the switch position was successful
def confirm_success(soc, parts, direction):
    condition1 = False
    condition2 = False
    ret = ""
    while not (condition1 and condition2):
        data = soc.recv(1024)
        if data:
            if b"SENT OK" in data:
                condition1 = True
            if (direction == "straight" or direction == "none") and get_answer(
                [parts[0], parts[1], parts[2] + 48]
            ) in data:
                condition2 = True
                ret = "straight"
            elif (direction == "branch" or direction == "none") and get_answer(
                parts
            ) in data:
                condition2 = True
                ret = "branch"
            if condition1 & condition2:
                return ret


# Loconet: get the position of a switch at given address
def get_switch_position(soc, address):
    split_address = convert_address(address)
    command = [188, split_address[0], split_address[1]]
    command.append(calculate_checksum(command))
    if verify_command(command):
        soc.sendall(get_binary_command(command))
        return confirm_success(soc, [180, 60, 0], "none")


# Loconet: set the speed of the train
def set_speed(soc, speed):
    command = [160, 1, speed]
    command.append(calculate_checksum(command))
    if verify_command(command):
        soc.sendall(get_binary_command(command))
        return True


# Loconet: get speed helper
def check_answer(soc):
    condition1 = False
    ret = ""
    while not condition1:
        data = soc.recv(1024)
        pos = data.find(b"E7 0E")
        if pos > 0:
            speed = data[pos + 15 : pos + 17]
            direction = "{0:07b}".format(int(data[pos + 18 : pos + 20]))
            condition1 = True
    return int(speed, 16), direction[2:3]


# Loconet: get speed
def get_speed(soc):
    command = [191, 0, 4]
    command.append(calculate_checksum(command))
    if verify_command(command):
        soc.sendall(get_binary_command(command))
        return check_answer(soc)


# detect start of branch (conditional on direction)
def is_branch_start(tag_id, direction):
    global loconet_socket
    return (
        direction == "1"
        and tag_id == START_SWITCH_TAG
        and get_switch_position(loconet_socket, START_SWITCH_ID) == "branch"
    ) or (
        direction == "0"
        and tag_id == END_SWITCH_TAG
        and get_switch_position(loconet_socket, END_SWITCH_ID) == "branch"
    )


# detect end of branch (conditional on direction)
def is_branch_end(tag_id, direction):
    global loconet_socket
    return (
        direction == "1"
        and tag_id == END_SWITCH_TAG
        and get_switch_position(loconet_socket, END_SWITCH_ID) == "branch"
    ) or (
        direction == "0"
        and tag_id == START_SWITCH_TAG
        and get_switch_position(loconet_socket, START_SWITCH_ID) == "branch"
    )


# detect start of construction site (conditional on direction)
def is_construction_start(tag_id, direction):
    return (direction == "1" and tag_id == START_CONSTRUCTION_TAG) or (
        direction == "0" and tag_id == END_CONSTRUCTION_TAG
    )


# detect end of construction site (conditional on direction)
def is_construction_end(tag_id, direction):
    return (direction == "1" and tag_id == END_CONSTRUCTION_TAG) or (
        direction == "0" and tag_id == START_CONSTRUCTION_TAG
    )


# check the speed restriction imposed when entering the branch
def check_branch_restriction(tag_id):
    global loconet_socket, last_speed
    speed, direction = get_speed(loconet_socket)
    if is_branch_start(tag_id, direction):
        print("Entering branch: Start of speed restriction!")
        last_speed = speed
        set_speed(loconet_socket, 20)
    elif is_branch_end(tag_id, direction):
        print("Leaving branch: End of speed restriction!")
        set_speed(loconet_socket, last_speed)


# check the speed restriction at the construction site
def check_construction_restriction(tag_id):
    global loconet_socket, last_speed
    speed, direction = get_speed(loconet_socket)
    if is_construction_start(tag_id, direction):
        print("Entering construction area: Start of speed restriction!")
        last_speed = speed
        set_speed(loconet_socket, 20)
    elif is_construction_end(tag_id, direction):
        print("Leaving construction area: End of speed restriction!")
        set_speed(loconet_socket, last_speed)


# Callback function: NFC reader found a new tag
def cb_reader_state_changed(state, idle, nfc):
    global last_tag_id
    if state == nfc.READER_STATE_REQUEST_TAG_ID_READY:
        ret = nfc.reader_get_tag_id()
        tag_id = " ".join(
            map(str, map("0x{:02X}".format, ret.tag_id))
        )  # map tag ID to a string

        # check restrictions if the tag was not already read directly before
        if last_tag_id == None or tag_id != last_tag_id:
            print("Found tag of type " + str(ret.tag_type) + " with ID " + tag_id)
            check_construction_restriction(tag_id)
            check_branch_restriction(tag_id)

        last_tag_id = tag_id

    if idle:
        nfc.reader_request_tag_id()


if __name__ == "__main__":
    global last_tag_id, loconet_socket, last_speed
    last_tag_id = None
    last_speed = 0

    # Create Loconet socket and connect to it
    loconet_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    loconet_socket.connect((LOCONET_HOST, LOCONET_PORT))

    ipcon = IPConnection()  # Create IP connection
    nfc = BrickletNFC(BRICK_UID, ipcon)  # Create device object
    ipcon.connect(BRICK_HOST, BRICK_PORT)  # Connect to brickd

    # Register reader state changed callback to function cb_reader_state_changed
    nfc.register_callback(
        nfc.CALLBACK_READER_STATE_CHANGED,
        lambda x, y: cb_reader_state_changed(x, y, nfc),
    )

    # Enable reader mode and decrease timeout
    nfc.set_mode(nfc.MODE_READER)
    nfc.set_maximum_timeout(20)

    input("Press key to exit\n")
    ipcon.disconnect()
    loconet_socket.close()
