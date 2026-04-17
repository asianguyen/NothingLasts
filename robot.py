from Petoi.serial import connectPort, sendSkillStr, closePort
import numpy as np


connectPort('/dev/cu.BittleC9_SSP')
sendSkillStr('kup', 1)
sendSkillStr('kwkF', 5)
closePort()