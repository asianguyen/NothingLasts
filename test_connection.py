# -*- coding: UTF-8 -*-
from petoi_import import *
from PetoiRobot.ardSerial import goodPorts

autoConnect()

print("\n--- DEBUG ---")
print("goodPorts:", goodPorts)
print("Number of connected ports:", len(goodPorts))
print("-------------\n")

if not goodPorts:
    print("ERROR: No ports connected. Robot won't respond.")
    print("Make sure Bittle is on and Bluetooth is paired.")
else:
    print("Standing up...")
    sendSkillStr('kup', 2)

    print("Walking forward...")
    sendSkillStr('kwkF', 3)

    print("Sitting down...")
    sendSkillStr('ksit', 1)

    closePort()