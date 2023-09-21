#!/usr/bin/env python

import socket
from threading import Thread


def convert_address(address):
    part_one = address % 128
    part_two = int((address - part_one)/128)
    return [part_one, part_two]


def calculate_checksum(parts):
    return 255 - (parts[0] ^ parts[1] ^ parts[2])


def verify_command(parts):
    return True if parts[0] ^ parts[1] ^ parts[2] ^ parts[3] else False


def get_binary_command(parts):
    command = (f'SEND {parts[0]:02X} {parts[1]:02X} {parts[2]:02X} {parts[3]:02X} \r').encode()
    print(command)
    return command


def switch_command(soc, address, direction):
    split_address = convert_address(address)
    if direction == 'straight':
        command = [176, split_address[0], split_address[1] + 48]
        command.append(calculate_checksum(command))
    elif direction == 'branch':
        command = [176, split_address[0], split_address[1] + 16]
        command.append(calculate_checksum(command))
    if verify_command(command):
        soc.sendall(get_binary_command(command))
        return True


class Interlocking:
    HOST = '192.168.10.70'
    PORT = 1234
    initialize = []
    running = True
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))

    def wait_for_commands(self):
        point_address = int(input("Input 2 or 3 to choose switch"))
        while self.running:
            direction = input("Please enter direction (b)ranch or (s)straight:")
            if direction == 's':
                direction = 'straight'
            elif direction == 'b':
                direction = 'branch'

            switch_command(self.s, point_address, direction)  # self.point_movement[direction])
            #self.point_position[point_address] = switch_command(self.s, point_address, direction)


i = Interlocking()

t1 = Thread(target=i.wait_for_commands())
t1.start()
t1.join()
