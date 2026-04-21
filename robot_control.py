"""
Robot Control Module
Handles movement to saved coordinates from drawing pad
Customized for 1000x600 canvas with 80px border
"""

import time
import math
import json
from petoi_import import *


CANVAS_WIDTH = 1000
CANVAS_HEIGHT = 600
CANVAS_PAD = 80


def convert_canvas_to_robot(canvas_x, canvas_y, canvas_width=1000, canvas_height=600, pad=80):
    """
    Convert drawing pad coordinates to robot coordinates
    
    Canvas: 1000x600, with 80px border
    Drawing area: (80,80) to (920,520)
    
    Robot: Adjust based on your robot's coordinate system
    
    Args:
        canvas_x: X coordinate from drawing pad (80-920)
        canvas_y: Y coordinate from drawing pad (80-520)
        canvas_width: Canvas width (1000)
        canvas_height: Canvas height (600)
        pad: Border padding (80)
    
    Returns:
        (robot_x, robot_y) tuple in robot coordinate space
    """
    
    # Define drawing boundaries
    draw_left = pad
    draw_right = canvas_width - pad
    draw_top = pad
    draw_bottom = canvas_height - pad
    
    # Calculate actual drawing area dimensions
    draw_width = draw_right - draw_left      # 840
    draw_height = draw_bottom - draw_top      # 440
    
    # Normalize to 0-1 range within drawing area
    normalized_x = (canvas_x - draw_left) / draw_width
    normalized_y = (canvas_y - draw_top) / draw_height
    
    # Clamp to valid range
    normalized_x = max(0, min(1, normalized_x))
    normalized_y = max(0, min(1, normalized_y))
    
    # Convert to robot coordinates
    # Example: Scale to 0-100 range with Y-axis flipped
    robot_x = normalized_x * 57
    robot_y = (1 - normalized_y) * 31  # Flip Y-axis
    
    return robot_x, robot_y


def calculate_interior_angle(p0, p1, p2):
    """Calculate the interior angle formed at p1 by points p0 -> p1 -> p2."""
    v1 = (p1[0] - p0[0], p1[1] - p0[1])
    v2 = (p2[0] - p1[0], p2[1] - p1[1])

    norm1 = math.hypot(v1[0], v1[1])
    norm2 = math.hypot(v2[0], v2[1])
    if norm1 == 0 or norm2 == 0:
        return None

    cosine = (v1[0] * v2[0] + v1[1] * v2[1]) / (norm1 * norm2)
    cosine = max(-1.0, min(1.0, cosine))
    turn_angle = math.degrees(math.acos(cosine))
    return 180.0 - turn_angle


def convert_path_to_robot_metrics(points, canvas_width=CANVAS_WIDTH, canvas_height=CANVAS_HEIGHT, pad=CANVAS_PAD):
    """Convert canvas points into robot-space points and per-segment metrics."""
    robot_points = [convert_canvas_to_robot(x, y, canvas_width, canvas_height, pad) for x, y in points]

    segments = []
    for index in range(1, len(robot_points)):
        start = robot_points[index - 1]
        end = robot_points[index]
        distance = calculate_distance(start, end)

        interior_angle = None
        if index >= 2:
            interior_angle = calculate_interior_angle(robot_points[index - 2], start, end)

        segments.append(
            {
                "index": index,
                "start": start,
                "end": end,
                "distance": distance,
                "interior_angle": interior_angle,
            }
        )

    return {
        "canvas_points": points,
        "robot_points": robot_points,
        "segments": segments,
    }


def calculate_distance(p1, p2):
    """Calculate Euclidean distance between two points"""
    return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)


def smooth_path(points, threshold=2.0):
    """
    Reduce path points by removing those too close together
    
    Args:
        points: List of (x, y) tuples
        threshold: Minimum distance between kept points
    
    Returns:
        Smoothed list of points
    """
    if len(points) <= 2:
        return points
    
    smoothed = [points[0]]
    
    for point in points[1:]:
        distance = calculate_distance(smoothed[-1], point)
        if distance > threshold:
            smoothed.append(point)
    
    # Always include final point
    if smoothed[-1] != points[-1]:
        smoothed.append(points[-1])
    
    return smoothed


def move_robot_to_points(path_data):
    """
    Move robot through the saved points
    
    Args:
        path_data: Dictionary containing canvas and robot points along with segment metrics
    """
    if not path_data:
        print("[ERROR] No path data to process")
        return
    
    print(f"\n{'='*70}")
    print(f"ROBOT EXECUTION STARTED")
    print(f"{'='*70}\n")
    
    robot_points = path_data['robot_points']
    canvas_points = path_data['canvas_points']

    for i, (canvas_point, robot_point) in enumerate(zip(canvas_points, robot_points)):
        canvas_x, canvas_y = canvas_point
        robot_x, robot_y = robot_point
        print(f"  Point {i}: Canvas ({canvas_x:3d}, {canvas_y:3d}) → Robot ({robot_x:6.2f}, {robot_y:6.2f})")

    print()

    autoConnect()
    sendSkillStr('kup', 1)

    for segment in path_data['segments']:
        interior_angle = segment['interior_angle']
        angle_text = "n/a" if interior_angle is None else f"{interior_angle:6.2f}°"
        print(f"  Segment {segment['index']}: distance={segment['distance']:6.2f}, interior angle={angle_text}")


        print(f"[{i+1:2d}/{len(robot_points)}] Moving to ({segment['start'][0]:6.2f}, {segment['start'][1]:6.2f})")
        sendSkillStr('kwkF', segment['distance'] / 3.0) # 3 inches per second
        if segment['interior_angle'] is not None:
            sendSkillStr('kvtL', segment['interior_angle'] / 4.5) # 4.5 degrees per second
        

    print()
    
    # Optional: Smooth the path (reduce number of points)
    # original_count = len(robot_points)
    # robot_points = smooth_path(robot_points, threshold=1.0)
    # if len(robot_points) < original_count:
    #     print(f"Smoothed path: {original_count} points → {len(robot_points)} points")
    #     print()
    
    
    print(f"\n{'='*70}")
    print(f"ROBOT EXECUTION COMPLETED")
    print(f"{'='*70}\n")


# def load_points_from_file(filename="drawn_points.json"):
#     """Load saved points from JSON file"""
#     try:
#         with open(filename, "r") as f:
#             points = json.load(f)
#         print(f"Loaded {len(points)} points from {filename}")
#         return points
#     except FileNotFoundError:
#         print(f"[ERROR] File {filename} not found")
#         return []
#     except json.JSONDecodeError:
#         print(f"[ERROR] Invalid JSON in {filename}")
#         return []


# Test the module standalone
if __name__ == "__main__":
    # Test with sample points from your drawing pad
    test_points = [
        (85, 85),      # Starting point
        (200, 150),    # Second point
        (350, 120),    # Third point
        (500, 250),    # Fourth point
        (400, 400)     # Fifth point
    ]
    
    print("Testing robot control with sample points...\n")
    move_robot_to_points(test_points)
    
    # Or load from saved file:
    # print("Loading points from file...\n")
    # points = load_points_from_file()
    # if points:
    #     move_robot_to_points(points)
