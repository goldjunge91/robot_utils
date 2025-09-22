#!/usr/bin/env python3

# Copyright 2024 Husarion sp. z o.o.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import os
import signal
import sys

import requests
from ament_index_python.packages import get_package_share_directory

from robot_utils.flash_firmware_uart import FirmwareFlasherUART
from robot_utils.flash_firmware_usb import FirmwareFlasherUSB
from robot_utils.utils import find_device_port

# Global variable to hold the subprocess reference
subproc = None


def signal_handler(sig, frame):
    global subproc
    if subproc:
        print("Terminating the flashing process...")
        subproc.terminate()
    sys.exit(0)


def download_firmware(firmware_url, firmware_path):
    response = requests.get(firmware_url, allow_redirects=True)
    if response.status_code == 200:
        with open(firmware_path, "wb") as f:
            f.write(response.content)
        print("Firmware downloaded successfully.")
    else:
        raise Exception(f"Failed to download firmware: HTTP {response.status_code}")


def find_firmware_file(path, robot_model):
    robot_link = (
        "https://github.com/husarion/robot_ros2_firmware/releases/download/0.11.0/firmware.bin"
    )
    robot_xl_link = (
        "https://github.com/husarion/robot_firmware/releases/download/v1.4.0/firmware.bin"
    )
    robot_download_link = {"robot": robot_link, "robot_xl": robot_xl_link}

    if not path:
        print("Downloading firmware...")
        download_firmware(robot_download_link[robot_model], path)

    return path


def main(args=None):
    global subproc

    # Setting up the signal handler
    signal.signal(signal.SIGINT, signal_handler)

    parser = argparse.ArgumentParser(description="Flash robot Firmware")
    parser.add_argument(
        "--robot-model",
        required=True,
        default=os.getenv("ROBOT_MODEL_NAME"),
        choices=["robot", "robot_xl"],
        help="Specify the robot model",
    )
    parser.add_argument(
        "--usb",
        action="store_true",
        help="Flash via USB. Automatically set for robot XL; other robots use UART by default. (You can flash firmware to robot via USB-A from your PC)",
    )
    default_manipulator_serial_port = find_device_port("0403", "6015", "/dev/ttyUSB0")
    parser.add_argument(
        "-p",
        "--port",
        default=default_manipulator_serial_port,
        help="Specify the communication port",
    )
    parser.add_argument("-f", "--file", help="Specify the firmware file")
    args = parser.parse_args(args)

    port = args.port
    robot_model = args.robot_model
    if robot_model == "robot_xl":
        args.usb = True

    robot_utils = get_package_share_directory("robot_utils")
    robot_firmware = os.path.join(robot_utils, "firmware", "robot", "v0.11.0.bin")
    robot_xl_firmware = os.path.join(robot_utils, "firmware", "robot_xl", "v1.4.0.bin")
    firmware_dict = {"robot": robot_firmware, "robot_xl": robot_xl_firmware}
    firmware = args.file if args.file else firmware_dict[robot_model]

    try:
        if args.usb:
            FirmwareFlasherUSB(firmware, port)
        else:
            FirmwareFlasherUART(firmware)
        print("Firmware flashing completed successfully!")
    except Exception as e:
        print(f"ERROR: {e}")


if __name__ == "__main__":
    main()
