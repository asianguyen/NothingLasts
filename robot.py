# -*- coding: UTF-8 -*-
import math
import time

from petoi_import import *

# ── Calibration (tune by running test_calibration() below) ────
# How many 'kwkF' steps does the robot take per screen pixel of distance?
STEPS_PER_PIXEL  = 0.04
# How many 'kwkL'/'kwkR' steps per degree of turn?
STEPS_PER_DEGREE = 0.12


class RobotController:
    def __init__(self):
        autoConnect()
        self.heading = 0.0

    def stand(self):
        sendSkillStr('kup', 1)

    def sit(self):
        sendSkillStr('ksit', 1)

    def walk_forward(self, steps: int):
        sendSkillStr('kwkF', steps * 0.25)

    def turn_left(self, steps: int):
        sendSkillStr('kwkL', steps * 0.25)

    def turn_right(self, steps: int):
        sendSkillStr('kwkR', steps * 0.25)

    def turn_to(self, target_deg: float):
        delta = (target_deg - self.heading + 360) % 360
        if delta > 180:
            delta -= 360

        steps = abs(int(delta * STEPS_PER_DEGREE))
        if steps == 0:
            return
        if delta > 0:
            self.turn_right(steps)
        else:
            self.turn_left(steps)
        self.heading = target_deg % 360

    def follow_path(self, points: list):
        if len(points) < 2:
            print("Need at least 2 points.")
            return

        self.stand()

        for i in range(1, len(points)):
            x1, y1 = points[i - 1]
            x2, y2 = points[i]

            dx =  (x2 - x1)
            dy = -(y2 - y1)     # invert y: screen down → world up

            target_deg = math.degrees(math.atan2(dy, dx))
            pixel_dist = math.hypot(dx, dy)
            fwd_steps  = max(1, int(pixel_dist * STEPS_PER_PIXEL))

            print(f"Segment {i}: turn to {target_deg:.1f}°, walk {fwd_steps} steps")
            self.turn_to(target_deg)
            self.walk_forward(fwd_steps)

        self.sit()

    def close(self):
        self.sit()
        closePort()


# ── Calibration helper ─────────────────────────────────────────

def test_calibration():
    robot = RobotController()
    robot.stand()
    print("Walking 10 forward steps — measure distance traveled.")
    robot.walk_forward(10)
    time.sleep(1)
    print("Turning 10 right steps — measure angle rotated.")
    robot.turn_right(10)
    robot.close()


if __name__ == '__main__':
    sample_path = [(85, 85), (300, 200), (600, 150), (800, 400)]
    robot = RobotController()
    try:
        robot.follow_path(sample_path)
    finally:
        robot.close()