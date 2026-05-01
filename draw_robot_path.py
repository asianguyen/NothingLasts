"""
Robot Path Drawer with Automatic Robot Control
Integrates your drawing pad with robot movement
"""

import json
import threading
import tkinter as tk
from tkinter import messagebox
import numpy as np

# Import robot control module
from robot_control import convert_path_to_robot_metrics, move_robot_to_points


class RobotPathDrawer:
    def __init__(self, root):
        self.root = root
        self.root.title("Robot Path Drawer")
        
        self.pad = 35
        self.width = 570
        self.height = 307
        self.r = 3
        
        self.draw_top = self.pad
        self.draw_left = self.pad
        self.draw_right = self.width - self.pad
        self.draw_bottom = self.height - self.pad
        
        self.points_coords = [(40, 40)]
        self.visual_points = []
        self.path_data = {}
        self.lines = []
        self.current_vector = np.array([40, 40])
        self.is_executing = False

        #------------ Bittle Name Input ------------
        name_frame = tk.Frame(root)
        name_frame.pack(pady=5)

        tk.Label(name_frame, text="Bittle Name:").pack(side="left", padx=5)

        self.bittle_name_var = tk.StringVar(value="BittleEA")
        self.bittle_name_entry = tk.Entry(name_frame, textvariable=self.bittle_name_var, width=20)
        self.bittle_name_entry.pack(side="left", padx=5)
        #--------------------------------------------
        
        self.canvas = tk.Canvas(root, width=self.width, height=self.height, bg="white")
        self.canvas.pack(fill="both")
        self.canvas.bind("<Button-1>", self.click)
        
        self.canvas.create_oval(
            40-self.r, 40-self.r, 
            40+self.r, 40+self.r, 
            fill="black"
        )
        
        self.draw_border()
        
        execute_draw_frame = tk.Frame(root)
        execute_draw_frame.pack(pady=10)
        
        self.clear_button = tk.Button(
            execute_draw_frame, 
            text="Clear", 
            command=self.clear)
        self.clear_button.pack(side="left", padx=5)
        
        self.save_button = tk.Button(
            execute_draw_frame, 
            text="Draw Path from Canvas", 
            command=self.save_and_execute_path)
        self.save_button.pack(side="left", padx=5)

        self.save_button = tk.Button(
            execute_draw_frame, 
            text="Follow Path from JSON", 
            command=self.save_and_execute_path)
        self.save_button.pack(side="left", padx=5)
        
        self.status_label = tk.Label(root, text="Ready. Click to add points (max 5).", font=("Arial", 10))
        self.status_label.pack(pady=5)
    
    def click(self, event):
        """Handle canvas click to add point"""
        if len(self.points_coords) >= 5:
            messagebox.showwarning("Limit Reached", "Maximum number of points (5) reached.")
            return
        
        if not self.inside_box(event.x, event.y):
            return
        
        x, y = event.x, event.y
        
        if not self.calculate_angle((x, y)):
            messagebox.showwarning("Angle Too Small", "Angle must be >= 30 degrees from previous direction.")
            return
        else:
            self.points_coords.append((x, y))
            point = self.canvas.create_oval(
                x-self.r, y-self.r, 
                x+self.r, y+self.r, 
                fill="black"
            )
            self.visual_points.append(point)
        
        if len(self.points_coords) > 1:
            x1, y1 = self.points_coords[-2]
            line = self.canvas.create_line(x1, y1, x, y, fill="black")
            self.lines.append(line)
        
        self.status_label.config(
            text=f"Points: {len(self.points_coords)} / 5"
        )
    
    def clear(self):
        """Clear canvas and reset points"""
        for point in self.visual_points:
            self.canvas.delete(point)
        
        self.points_coords.clear()
        self.points_coords.append((40, 40))
        self.visual_points.clear()
        
        for line in self.lines:
            self.canvas.delete(line)
        self.lines.clear()
        
        self.current_vector = np.array([40, 40])
        self.status_label.config(text="Canvas cleared. Ready to draw.")
    
    def save_and_execute_path(self):
        """Save path and automatically execute robot"""
        if len(self.points_coords) <= 1:
            messagebox.showwarning("No Path", "Draw at least 2 points before saving.")
            return
        
        if self.is_executing:
            messagebox.showinfo("Busy", "Robot is already executing. Please wait...")
            return
        
        path_data = convert_path_to_robot_metrics(self.points_coords)
        self.path_data = path_data

        with open("drawn_points.json", "w") as f:
            json.dump(self.points_coords, f)

        with open("drawn_points_physical.json", "w") as f:
            json.dump(path_data, f)
        
        print(f"\n{'='*60}")
        print(f"SAVED PATH: {self.points_coords}")
        print(f"Physical robot points: {path_data['robot_points']}")
        print(f"Total points: {len(self.points_coords)}")
        print(f"{'='*60}\n")
        
        self.status_label.config(text=f"✓ Saved {len(self.points_coords)} points. Starting robot...")
        messagebox.showinfo(
            "Path Saved", 
            f"Saved {len(self.points_coords)} points.\nStarting robot execution..."
        )
        
        self.save_button.config(state="disabled")
        self.clear_button.config(state="disabled")
        self.is_executing = True
        
        robot_thread = threading.Thread(target=self._execute_robot)
        robot_thread.daemon = True
        robot_thread.start()
    
    def _execute_robot(self):
        """Execute robot in separate thread"""
        try:
            bittle_name = self.bittle_name_var.get().strip()
            if not bittle_name:
                raise Exception("Please enter a Bittle name.")
            move_robot_to_points(self.path_data, bittle_name)
            
            self.status_label.config(text="✓ Robot execution completed!")
            messagebox.showinfo("Complete", "Robot has finished executing the path!")
            print("\n[SUCCESS] Robot execution completed!\n")
        
        except Exception as e:
            self.status_label.config(text=f"✗ Error: {str(e)}")
            messagebox.showerror("Error", f"Robot execution failed:\n{str(e)}")
            print(f"\n[ERROR] {str(e)}\n")
        
        finally:
            self.save_button.config(state="normal")
            self.clear_button.config(state="normal")
            self.is_executing = False
    
    def inside_box(self, x, y):
        """Check if point is inside drawing area"""
        return self.draw_left <= x <= self.draw_right and self.draw_top <= y <= self.draw_bottom
    
    def draw_border(self):
        """Draw boundary rectangles to show valid drawing area"""
        color = "red"
        # Top
        self.canvas.create_rectangle(0, 0, self.width, self.draw_top, outline=color, fill=color)
        # Bottom
        self.canvas.create_rectangle(0, self.draw_bottom, self.width, self.height, outline=color, fill=color)
        # Left
        self.canvas.create_rectangle(0, 0, self.draw_left, self.height, outline=color, fill=color)
        # Right
        self.canvas.create_rectangle(self.draw_right, 0, self.width, self.height, outline=color, fill=color)

    def _get_interior_angle(self, position):
        """Return interior angle for a candidate point, or None if unavailable."""
        if len(self.points_coords) < 2:
            return None

        x_prev2, y_prev2 = self.points_coords[-2]
        x_prev1, y_prev1 = self.points_coords[-1]
        x_new, y_new = position

        prev_vec = np.array([x_prev1 - x_prev2, y_prev1 - y_prev2], dtype=float)
        newest_vec = np.array([x_new - x_prev1, y_new - y_prev1], dtype=float)

        prev_norm = np.linalg.norm(prev_vec)
        new_norm = np.linalg.norm(newest_vec)
        if prev_norm == 0 or new_norm == 0:
            return None

        dot_prod = np.dot(prev_vec, newest_vec)
        cos_theta = np.clip(dot_prod / (prev_norm * new_norm), -1.0, 1.0)
        turn_angle = np.degrees(np.arccos(cos_theta))
        return float(180.0 - turn_angle)
    
    def calculate_angle(self, position) -> bool:
        """Check if interior angle between consecutive path segments is >= 30 degrees."""
        if len(self.points_coords) < 2:
            return True

        interior_angle = self._get_interior_angle(position)
        return bool(interior_angle is not None and interior_angle >= 30.0)


if __name__ == "__main__":
    root = tk.Tk()
    app = RobotPathDrawer(root)
    root.mainloop()
