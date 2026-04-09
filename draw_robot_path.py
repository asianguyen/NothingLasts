import tkinter as tk

points_coords = []
points = []
lines = []
pad = 80
width = 1000
height = 600
draw_left = pad
draw_top = pad
draw_right = width - pad
draw_bottom = height - pad

def click(event):
    if len(points_coords) >= 5:
        return  
    
    if not inside_box(event.x, event.y):
        return

    x, y = event.x, event.y
    points_coords.append((x, y))

    r = 3
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


root = tk.Tk()
root.title("Robot Path Drawer")

canvas = tk.Canvas(root, width=width, height=height, bg="white")
canvas.pack(fill="both")

canvas.bind("<Button-1>", click)

frame = tk.Frame(root)
frame.pack()

tk.Button(frame, text="Clear", command=clear).pack(side="left")
tk.Button(frame, text="Save Path", command=save_path).pack(side="left")
draw_border()

root.mainloop()