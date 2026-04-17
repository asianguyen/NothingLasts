import tkinter as tk
import numpy as np
from Petoi_MindPlusLib import *


points_coords = [(85,85)]
points = []
lines = []

pad = 80
width = 1000
height = 600
r = 3
draw_left = pad
draw_top = pad
draw_right = width - pad
draw_bottom = height - pad

current_vector = np.array([85, 85])

def click(event):
    if len(points_coords) >= 5:
        label = tk.Label(root, text="Maximum number of points reached.")
        label.pack()
        return  
    
    if not inside_box(event.x, event.y):
        return

    x, y = event.x, event.y

    if not calculate_angle((x,y)):
        return
    else:
        points_coords.append((x, y))
        point = canvas.create_oval(x-r, y-r, x+r, y+r, fill="black")
        points.append(point)

    if len(points_coords) > 1:
        x1, y1 = points_coords[-2]
        
        line = canvas.create_line(x1, y1, x, y, fill="black")
        lines.append(line)

def clear():
    for point in points:
        canvas.delete(point)
    points_coords.clear()
    points_coords.append((85,85))
    points.clear()
    for line in lines:
        canvas.delete(line)
    lines.clear()


def save_path():
    print("Robot path:", points_coords)

def inside_box(x,y):
    return draw_left <= x <= draw_right and draw_top <= y <= draw_bottom

def draw_border():
    color = "red"
    canvas.create_rectangle(0, 0, width, draw_top, outline = color, fill= color)
    canvas.create_rectangle(0, draw_bottom, width, height, outline = color, fill= color)
    canvas.create_rectangle(0, 0, draw_left, height, outline = color, fill= color)
    canvas.create_rectangle(draw_right, 0, width, height, outline = color, fill= color)

def calculate_angle(position) -> bool:
    if len(points_coords) < 2:
        return True

    x1, y1 = points_coords[-1]
    x2, y2 = position

    dx = x2 - x1
    dy = y2 - y1

    newest_vec = np.array([dx, dy])

    dot_prod = np.dot(current_vector, newest_vec)
    norms = np.linalg.norm(current_vector) * np.linalg.norm(newest_vec)
    cos = dot_prod / norms if norms != 0 else 0
    angle = np.degrees(np.arccos(cos))

    angle = 180 - angle

    if angle >= 30:
        current_vector[:] = newest_vec
        return True
    
    return False



root = tk.Tk()
root.title("Robot Path Drawer")

canvas = tk.Canvas(root, width=width, height=height, bg="white")
canvas.pack(fill="both")

canvas.bind("<Button-1>", click)
canvas.create_oval(85-r, 85-r, 85+r, 85+r, fill="black")

frame = tk.Frame(root)
frame.pack()

tk.Button(frame, text="Clear", command=clear).pack(side="left")
tk.Button(frame, text="Save Path", command=save_path).pack(side="left")
draw_border()

root.mainloop()