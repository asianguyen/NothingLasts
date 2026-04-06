import tkinter as tk

points = []

def click(event):
    if len(points) >= 5:
        return  

    x, y = event.x, event.y
    points.append((x, y))

    r = 3
    canvas.create_oval(x-r, y-r, x+r, y+r, fill="black")

    if len(points) > 1:
        x1, y1 = points[-2]
        canvas.create_line(x1, y1, x, y)

def clear():
    points.clear()
    canvas.delete("all")

def save_path():
    print("Robot path:", points)

root = tk.Tk()
root.title("Robot Path Drawer")

canvas = tk.Canvas(root, width=600, height=400, bg="white")
canvas.pack()

canvas.bind("<Button-1>", click)

frame = tk.Frame(root)
frame.pack()

tk.Button(frame, text="Clear", command=clear).pack(side="left")
tk.Button(frame, text="Save Path", command=save_path).pack(side="left")

root.mainloop()