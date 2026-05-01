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
        
        self.pad = 30
        self.width = 570
        self.height = 307
        self.r = 3
        
        self.draw_top = self.pad
        self.draw_left = self.pad
        self.draw_right = self.width - self.pad
        self.draw_bottom = self.height - self.pad
        
        self.points_coords = [(35, 35)]
        self.visual_points = []
        self.path_data = {}
        self.lines = []
        self.current_vector = np.array([35, 35])
        self.is_executing_r1 = False
        self.is_executing_r2 = False

        #------------ Robot 1 (Creator) Calibration ------------
        r1_frame = tk.Frame(root)
        r1_frame.pack(pady=3)

        tk.Label(r1_frame, text="Robot 1 (Creator)", font=("Arial", 9, "bold")).pack(side="left", padx=5)
        tk.Label(r1_frame, text="Name:").pack(side="left", padx=(10, 2))
        self.bittle_name_var = tk.StringVar(value="BittleB3")
        tk.Entry(r1_frame, textvariable=self.bittle_name_var, width=12).pack(side="left", padx=2)

        tk.Label(r1_frame, text="Turn Scale:").pack(side="left", padx=(10, 2))
        self.turn_scale_var = tk.StringVar(value="27.0")
        tk.Entry(r1_frame, textvariable=self.turn_scale_var, width=6).pack(side="left", padx=2)

        tk.Label(r1_frame, text="Walk Scale:").pack(side="left", padx=(10, 2))
        self.walk_scale_var = tk.StringVar(value="3.85")
        tk.Entry(r1_frame, textvariable=self.walk_scale_var, width=6).pack(side="left", padx=2)

        #------------ Robot 2 (Eraser) Calibration ------------
        r2_frame = tk.Frame(root)
        r2_frame.pack(pady=3)

        tk.Label(r2_frame, text="Robot 2 (Eraser) ", font=("Arial", 9, "bold")).pack(side="left", padx=5)
        tk.Label(r2_frame, text="Name:").pack(side="left", padx=(10, 2))
        self.bittle2_name_var = tk.StringVar(value="Bittle8F")
        tk.Entry(r2_frame, textvariable=self.bittle2_name_var, width=12).pack(side="left", padx=2)

        tk.Label(r2_frame, text="Turn Scale:").pack(side="left", padx=(10, 2))
        self.turn_scale2_var = tk.StringVar(value="31.7")
        tk.Entry(r2_frame, textvariable=self.turn_scale2_var, width=6).pack(side="left", padx=2)

        tk.Label(r2_frame, text="Walk Scale:").pack(side="left", padx=(10, 2))
        self.walk_scale2_var = tk.StringVar(value="3.5")
        tk.Entry(r2_frame, textvariable=self.walk_scale2_var, width=6).pack(side="left", padx=2)
        #----------------------------------------------------------
        
        self.canvas = tk.Canvas(root, width=self.width, height=self.height, bg="white")
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.click)
        
        self.canvas.create_oval(
            35-self.r, 35-self.r, 
            35+self.r, 35+self.r, 
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
            command=self.save_and_execute_path_create)
        self.save_button.pack(side="left", padx=5)

        self.follow_button = tk.Button(
            execute_draw_frame,
            text="Follow Path",
            command=self.save_and_execute_path_erase)
        self.follow_button.pack(side="left", padx=5)
        
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
        self.points_coords.append((35, 35))
        self.visual_points.clear()
        
        for line in self.lines:
            self.canvas.delete(line)
        self.lines.clear()
        
        self.current_vector = np.array([35, 35])
        self.status_label.config(text="Canvas cleared. Ready to draw.")
    
    def save_and_execute_path_create(self):
        """Save path and automatically execute robot"""
        if len(self.points_coords) <= 1:
            messagebox.showwarning("No Path", "Draw at least 2 points before saving.")
            return
        
        if self.is_executing_r1:
            messagebox.showinfo("Busy", "Robot 1 is already executing. Please wait...")
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
        self.is_executing_r1 = True

        robot_thread = threading.Thread(target=self._execute_create_robot)
        robot_thread.daemon = True
        robot_thread.start()

    def save_and_execute_path_erase(self):
        """Save path and automatically execute robot"""
        if len(self.points_coords) <= 1:
            messagebox.showwarning("No Path", "Draw at least 2 points before saving.")
            return
        
        if self.is_executing_r1:
            messagebox.showinfo("Busy", "Robot 1 is already executing. Please wait...")
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
        self.is_executing_r1 = True

        robot_thread = threading.Thread(target=self._execute_erase_robot)
        robot_thread.daemon = True
        robot_thread.start()
    
    def _execute_create_robot(self):
        """Execute Robot 1 (creator) in separate thread"""
        try:
            bittle_name = "BittleB3" 
            turn_scale = 27.0
            walk_scale = 3.85
            move_robot_to_points(self.path_data, bittle_name, turn_scale, walk_scale)

            self.status_label.config(text="✓ Robot 1 execution completed!")
            messagebox.showinfo("Complete", "Robot 1 has finished executing the path!")
            print("\n[SUCCESS] Robot 1 execution completed!\n")

        except Exception as e:
            self.status_label.config(text=f"✗ Error: {str(e)}")
            messagebox.showerror("Error", f"Robot 1 execution failed:\n{str(e)}")
            print(f"\n[ERROR] {str(e)}\n")

        finally:
            self.save_button.config(state="normal")
            self.clear_button.config(state="normal")
            self.is_executing_r1 = False
    
    def _execute_erase_robot(self):
        """Execute Robot 1 (creator) in separate thread"""
        try:
            bittle_name = "Bittle8F"  
            turn_scale = 31.7
            walk_scale = 3.5
            move_robot_to_points(self.path_data, bittle_name, turn_scale, walk_scale)

            self.status_label.config(text="✓ Robot 1 execution completed!")
            messagebox.showinfo("Complete", "Robot 1 has finished executing the path!")
            print("\n[SUCCESS] Robot 1 execution completed!\n")

        except Exception as e:
            self.status_label.config(text=f"✗ Error: {str(e)}")
            messagebox.showerror("Error", f"Robot 1 execution failed:\n{str(e)}")
            print(f"\n[ERROR] {str(e)}\n")

        finally:
            self.save_button.config(state="normal")
            self.clear_button.config(state="normal")
            self.is_executing_r1 = False

    # def execute_from_json(self):
    #     """Load path from JSON and execute with Robot 2 (eraser)"""
    #     if self.is_executing_r2:
    #         messagebox.showinfo("Busy", "Robot 2 is already executing. Please wait...")
    #         return

    #     try:
    #         with open("drawn_points_physical.json", "r") as f:
    #             path_data = json.load(f)
    #     except FileNotFoundError:
    #         messagebox.showerror("Error", "No saved path found. Draw and save a path with Robot 1 first.")
    #         return
    #     except json.JSONDecodeError:
    #         messagebox.showerror("Error", "drawn_points_physical.json is corrupted.")
    #         return

    #     self.follow_button.config(state="disabled")
    #     self.is_executing_r2 = True
    #     self.status_label.config(text="Starting Robot 2 (eraser)...")

    #     def _run():
    #         try:
    #             bittle_name = self.bittle2_name_var.get().strip()
    #             if not bittle_name:
    #                 raise Exception("Please enter a Robot 2 name.")
    #             turn_scale = float(self.turn_scale2_var.get())
    #             walk_scale = float(self.walk_scale2_var.get())
    #             move_robot_to_points(path_data, bittle_name, turn_scale, walk_scale)
    #             self.status_label.config(text="✓ Robot 2 execution completed!")
    #             messagebox.showinfo("Complete", "Robot 2 has finished following the path!")
    #             print("\n[SUCCESS] Robot 2 execution completed!\n")
    #         except Exception as e:
    #             self.status_label.config(text=f"✗ Error: {str(e)}")
    #             messagebox.showerror("Error", f"Robot 2 execution failed:\n{str(e)}")
    #             print(f"\n[ERROR] {str(e)}\n")
    #         finally:
    #             self.follow_button.config(state="normal")
    #             self.is_executing_r2 = False

    #     robot_thread = threading.Thread(target=_run)
    #     robot_thread.daemon = True
    #     robot_thread.start()
    
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
    root.resizable(False, False)
    root.mainloop()
