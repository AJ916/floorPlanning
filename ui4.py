import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import patches  # Add this line
import numpy as np

# Import your existing floor plan module - uncomment and update with your module name
from expansion.backend.maxSize import FloorPlan

class ShapeDialog:
    def __init__(self, parent, title, width=10, height=5):
        self.result = None

        # Create a top level dialog
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Width and height entries
        ttk.Label(self.dialog, text="Width:").grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        self.width_var = tk.StringVar(value=str(width))
        ttk.Entry(self.dialog, textvariable=self.width_var, width=10).grid(row=0, column=1, padx=10, pady=10)

        ttk.Label(self.dialog, text="Height:").grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
        self.height_var = tk.StringVar(value=str(height))
        ttk.Entry(self.dialog, textvariable=self.height_var, width=10).grid(row=1, column=1, padx=10, pady=10)

        # Buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)

        ttk.Button(button_frame, text="OK", command=self.on_ok).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)

        # Center the dialog
        self.center_dialog()

        # Wait for the dialog to close
        self.dialog.wait_window(self.dialog)

    def center_dialog(self):
        self.dialog.update_idletasks()

        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()

        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)

        self.dialog.geometry(f"{width}x{height}+{x}+{y}")

    def on_ok(self):
        try:
            width = int(self.width_var.get())
            height = int(self.height_var.get())

            if width <= 0 or height <= 0:
                raise ValueError("Width and height must be positive integers.")

            self.result = (width, height)
            self.dialog.destroy()

        except ValueError as e:
            messagebox.showerror("Invalid Input", str(e))


class RoomDialog:
    def __init__(self, parent, title, name="", width=3, height=3, max_expansion=1):
        self.result = None

        # Create a top level dialog
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Room name, width, height, and max expansion entries
        ttk.Label(self.dialog, text="Room Name:").grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        self.name_var = tk.StringVar(value=name)
        ttk.Entry(self.dialog, textvariable=self.name_var, width=20).grid(row=0, column=1, padx=10, pady=10)

        ttk.Label(self.dialog, text="Width:").grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
        self.width_var = tk.StringVar(value=str(width))
        ttk.Entry(self.dialog, textvariable=self.width_var, width=10).grid(row=1, column=1, padx=10, pady=10)

        ttk.Label(self.dialog, text="Height:").grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)
        self.height_var = tk.StringVar(value=str(height))
        ttk.Entry(self.dialog, textvariable=self.height_var, width=10).grid(row=2, column=1, padx=10, pady=10)

        # New field for max expansion
        ttk.Label(self.dialog, text="Max Expansion:").grid(row=3, column=0, padx=10, pady=10, sticky=tk.W)
        self.max_expansion_var = tk.StringVar(value=str(max_expansion))
        ttk.Entry(self.dialog, textvariable=self.max_expansion_var, width=10).grid(row=3, column=1, padx=10, pady=10)
        ttk.Label(self.dialog, text="(0 = No expansion)").grid(row=3, column=2, padx=5, pady=10, sticky=tk.W)

        # Buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.grid(row=4, column=0, columnspan=3, pady=10)  # Updated row and columnspan

        ttk.Button(button_frame, text="OK", command=self.on_ok).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)

        # Center the dialog
        self.center_dialog()

        # Wait for the dialog to close
        self.dialog.wait_window(self.dialog)

    def center_dialog(self):
        self.dialog.update_idletasks()

        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()

        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)

        self.dialog.geometry(f"{width}x{height}+{x}+{y}")

    def on_ok(self):
        try:
            name = self.name_var.get().strip()
            width = int(self.width_var.get())
            height = int(self.height_var.get())
            max_expansion = int(self.max_expansion_var.get())

            if not name:
                raise ValueError("Room name cannot be empty.")

            if width <= 0 or height <= 0:
                raise ValueError("Width and height must be positive integers.")

            if max_expansion < 0:
                raise ValueError("Max expansion cannot be negative.")

            self.result = (name, width, height, max_expansion)
            self.dialog.destroy()

        except ValueError as e:
            messagebox.showerror("Invalid Input", str(e))

class AdjacencyDialog:
    def __init__(self, parent, title, room_names):
        self.result = None
        self.room_names = room_names

        # Create a top level dialog
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Room selection comboboxes
        ttk.Label(self.dialog, text="Room 1:").grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        self.room1_var = tk.StringVar()
        self.room1_combo = ttk.Combobox(self.dialog, textvariable=self.room1_var, values=room_names, state="readonly",
                                        width=20)
        self.room1_combo.grid(row=0, column=1, padx=10, pady=10)
        if room_names:
            self.room1_combo.current(0)

        ttk.Label(self.dialog, text="Room 2:").grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
        self.room2_var = tk.StringVar()
        self.room2_combo = ttk.Combobox(self.dialog, textvariable=self.room2_var, values=room_names, state="readonly",
                                        width=20)
        self.room2_combo.grid(row=1, column=1, padx=10, pady=10)
        if len(room_names) > 1:
            self.room2_combo.current(1)
        elif room_names:
            self.room2_combo.current(0)

        # Buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)

        ttk.Button(button_frame, text="OK", command=self.on_ok).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)

        # Center the dialog
        self.center_dialog()

        # Wait for the dialog to close
        self.dialog.wait_window(self.dialog)

    def center_dialog(self):
        self.dialog.update_idletasks()

        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()

        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)

        self.dialog.geometry(f"{width}x{height}+{x}+{y}")

    def on_ok(self):
        room1 = self.room1_var.get()
        room2 = self.room2_var.get()

        if not room1 or not room2:
            messagebox.showerror("Invalid Selection", "Please select both rooms.")
            return

        if room1 == room2:
            messagebox.showerror("Invalid Selection", "Please select two different rooms.")
            return

        self.result = (room1, room2)
        self.dialog.destroy()


class FloorPlanApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Floor Plan Generator")
        self.root.geometry("1200x800")

        self.shape_dimensions = []
        self.rooms = []
        self.adjacencies = []
        self.floor_plan = None

        self.create_widgets()

    def create_widgets(self):
        # Create notebook (tabbed interface)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create tabs
        self.setup_tab = ttk.Frame(self.notebook)
        self.rooms_tab = ttk.Frame(self.notebook)
        self.adjacency_tab = ttk.Frame(self.notebook)
        self.result_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.setup_tab, text="1. Floor Shape")
        self.notebook.add(self.rooms_tab, text="2. Rooms")
        self.notebook.add(self.adjacency_tab, text="3. Adjacencies")
        self.notebook.add(self.result_tab, text="4. Generate & View")

        # Setup the tabs
        self.setup_floor_shape_tab()
        self.setup_rooms_tab()
        self.setup_adjacency_tab()
        self.setup_result_tab()

    def setup_floor_shape_tab(self):
        # Create a frame for the floor shape input
        shape_frame = ttk.LabelFrame(self.setup_tab, text="Floor Shape")
        shape_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        ttk.Label(shape_frame, text="Define the floor shape as a stack of rectangles (from top to bottom):").pack(
            pady=5)

        # Create a frame for the shape dimensions list
        self.shape_list_frame = ttk.Frame(shape_frame)
        self.shape_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Create a treeview to display shape dimensions
        self.shape_tree = ttk.Treeview(self.shape_list_frame, columns=("Width", "Height"), show="headings")
        self.shape_tree.heading("Width", text="Width")
        self.shape_tree.heading("Height", text="Height")
        self.shape_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Add scrollbar
        shape_scrollbar = ttk.Scrollbar(self.shape_list_frame, orient=tk.VERTICAL, command=self.shape_tree.yview)
        shape_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.shape_tree.configure(yscrollcommand=shape_scrollbar.set)

        # Create a frame for the buttons
        buttons_frame = ttk.Frame(shape_frame)
        buttons_frame.pack(fill=tk.X, pady=10)

        # Create add, edit, and delete buttons
        ttk.Button(buttons_frame, text="Add Rectangle", command=self.add_shape).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Edit Rectangle", command=self.edit_shape).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Delete Rectangle", command=self.delete_shape).pack(side=tk.LEFT, padx=5)

        # Add button to continue to next tab
        ttk.Button(self.setup_tab, text="Continue to Rooms →",
                   command=lambda: self.notebook.select(1)).pack(side=tk.RIGHT, padx=10, pady=10)

        # Default shape dimensions from your provided code
        default_dimensions = [
            (12, 4),  # Top rectangle: 12 wide, 4 high
            (18, 6),  # Middle rectangle: 18 wide, 6 high
            (22, 6)  # Bottom rectangle: 22 wide, 6 high
        ]

        # Add default dimensions
        for width, height in default_dimensions:
            self.shape_dimensions.append((width, height))
            self.shape_tree.insert("", tk.END, values=(width, height))

    def setup_rooms_tab(self):
        # Create a frame for the rooms input
        rooms_frame = ttk.LabelFrame(self.rooms_tab, text="Rooms")
        rooms_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        ttk.Label(rooms_frame, text="Define rooms with their names, dimensions, and max expansion:").pack(pady=5)

        # Create a frame for the rooms list
        self.rooms_list_frame = ttk.Frame(rooms_frame)
        self.rooms_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Create a treeview to display rooms
        self.rooms_tree = ttk.Treeview(self.rooms_list_frame, columns=("Name", "Width", "Height", "MaxExpansion"),
                                       show="headings")
        self.rooms_tree.heading("Name", text="Room Name")
        self.rooms_tree.heading("Width", text="Width")
        self.rooms_tree.heading("Height", text="Height")
        self.rooms_tree.heading("MaxExpansion", text="Max Expansion")
        self.rooms_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Add scrollbar
        rooms_scrollbar = ttk.Scrollbar(self.rooms_list_frame, orient=tk.VERTICAL, command=self.rooms_tree.yview)
        rooms_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.rooms_tree.configure(yscrollcommand=rooms_scrollbar.set)

        # Create a frame for the buttons
        buttons_frame = ttk.Frame(rooms_frame)
        buttons_frame.pack(fill=tk.X, pady=10)

        # Create add, edit, and delete buttons
        ttk.Button(buttons_frame, text="Add Room", command=self.add_room).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Edit Room", command=self.edit_room).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Delete Room", command=self.delete_room).pack(side=tk.LEFT, padx=5)

        # Add buttons to navigate between tabs
        navigation_frame = ttk.Frame(self.rooms_tab)
        navigation_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(navigation_frame, text="← Back to Floor Shape",
                   command=lambda: self.notebook.select(0)).pack(side=tk.LEFT)
        ttk.Button(navigation_frame, text="Continue to Adjacencies →",
                   command=lambda: self.notebook.select(2)).pack(side=tk.RIGHT)

        # Default rooms with max expansion values
        default_rooms = [
            ("Living Room", 8, 4, 20),
            ("Kitchen", 6, 4, 10),
            ("Bedroom 1", 5, 4, 10),
            ("Bedroom 2", 5, 4, 10),
            ("Bathroom", 3, 4, 5),
            ("Hallway", 2, 4, 10),
            ("secretRoom", 2, 3, 0)
        ]

        # Add default rooms
        for name, width, height, max_expansion in default_rooms:
            self.rooms.append((name, width, height, max_expansion))
            self.rooms_tree.insert("", tk.END, values=(name, width, height, max_expansion))

    def setup_adjacency_tab(self):
        # Create a frame for the adjacency input
        adjacency_frame = ttk.LabelFrame(self.adjacency_tab, text="Room Adjacencies")
        adjacency_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        ttk.Label(adjacency_frame, text="Define which rooms should be adjacent to each other:").pack(pady=5)

        # Create a frame for the adjacency list
        self.adjacency_list_frame = ttk.Frame(adjacency_frame)
        self.adjacency_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Create a treeview to display adjacencies
        self.adjacency_tree = ttk.Treeview(self.adjacency_list_frame, columns=("Room1", "Room2"), show="headings")
        self.adjacency_tree.heading("Room1", text="Room 1")
        self.adjacency_tree.heading("Room2", text="Room 2")
        self.adjacency_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Add scrollbar
        adjacency_scrollbar = ttk.Scrollbar(self.adjacency_list_frame, orient=tk.VERTICAL,
                                            command=self.adjacency_tree.yview)
        adjacency_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.adjacency_tree.configure(yscrollcommand=adjacency_scrollbar.set)

        # Create a frame for the buttons
        buttons_frame = ttk.Frame(adjacency_frame)
        buttons_frame.pack(fill=tk.X, pady=10)

        # Create add and delete buttons
        ttk.Button(buttons_frame, text="Add Adjacency", command=self.add_adjacency).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Delete Adjacency", command=self.delete_adjacency).pack(side=tk.LEFT, padx=5)

        # Add buttons to navigate between tabs
        navigation_frame = ttk.Frame(self.adjacency_tab)
        navigation_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(navigation_frame, text="← Back to Rooms",
                   command=lambda: self.notebook.select(1)).pack(side=tk.LEFT)
        ttk.Button(navigation_frame, text="Continue to Generate →",
                   command=lambda: self.notebook.select(3)).pack(side=tk.RIGHT)

        # Default adjacencies from your provided code
        default_adjacencies = [
            ("Living Room", "Kitchen"),
            ("Living Room", "Bathroom"),
            ("Kitchen", "Bedroom 1"),
            ("Bedroom 1", "Bedroom 2"),
            ("Bedroom 2", "Hallway"),
            ("Hallway", "Bathroom"),
            ("secretRoom", "Bedroom 2")
        ]

        # Add default adjacencies
        for room1, room2 in default_adjacencies:
            self.adjacencies.append((room1, room2))
            self.adjacency_tree.insert("", tk.END, values=(room1, room2))

    def setup_result_tab(self):
        # Create a frame for generation options
        options_frame = ttk.LabelFrame(self.result_tab, text="Generation Options")
        options_frame.pack(fill=tk.X, padx=10, pady=10)

        # Create a frame for the options
        options_inner_frame = ttk.Frame(options_frame)
        options_inner_frame.pack(fill=tk.X, padx=10, pady=10)

        # Max attempts
        ttk.Label(options_inner_frame, text="Max Attempts:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.max_attempts_var = tk.StringVar(value="50000")
        ttk.Entry(options_inner_frame, textvariable=self.max_attempts_var, width=10).grid(row=0, column=1, padx=5,
                                                                                          pady=5, sticky=tk.W)

        # Enable expansion
        self.enable_expansion_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_inner_frame, text="Enable Room Expansion", variable=self.enable_expansion_var).grid(
            row=1, column=0, columnspan=2, padx=5, pady=5, sticky=tk.W)

        # Generate button
        ttk.Button(options_frame, text="Generate Floor Plan", command=self.generate_floor_plan).pack(pady=10)

        # Create a frame for the visualization
        self.visualization_frame = ttk.LabelFrame(self.result_tab, text="Floor Plan Visualization")
        self.visualization_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Message indicating no visualization yet
        self.empty_label = ttk.Label(self.visualization_frame,
                                     text="No floor plan generated yet. Click 'Generate Floor Plan' to create one.")
        self.empty_label.pack(pady=50)

        # Create a frame for the stats and room info
        self.info_frame = ttk.Frame(self.result_tab)
        self.info_frame.pack(fill=tk.X, padx=10, pady=10)

        # Add a button to navigate back
        ttk.Button(self.result_tab, text="← Back to Adjacencies",
                   command=lambda: self.notebook.select(2)).pack(side=tk.LEFT, padx=10, pady=10)

    def add_shape(self):
        dialog = ShapeDialog(self.root, "Add Rectangle")
        if dialog.result:
            width, height = dialog.result
            self.shape_dimensions.append((width, height))
            self.shape_tree.insert("", tk.END, values=(width, height))

    def edit_shape(self):
        selected_items = self.shape_tree.selection()
        if not selected_items:
            messagebox.showwarning("No Selection", "Please select a rectangle to edit.")
            return

        item = selected_items[0]
        values = self.shape_tree.item(item, "values")

        dialog = ShapeDialog(self.root, "Edit Rectangle", int(values[0]), int(values[1]))
        if dialog.result:
            width, height = dialog.result
            index = self.shape_tree.index(item)
            self.shape_dimensions[index] = (width, height)
            self.shape_tree.item(item, values=(width, height))

    def delete_shape(self):
        selected_items = self.shape_tree.selection()
        if not selected_items:
            messagebox.showwarning("No Selection", "Please select a rectangle to delete.")
            return

        item = selected_items[0]
        index = self.shape_tree.index(item)
        self.shape_dimensions.pop(index)
        self.shape_tree.delete(item)

    def add_room(self):
        dialog = RoomDialog(self.root, "Add Room")
        if dialog.result:
            name, width, height, max_expansion = dialog.result
            # Check if a room with this name already exists
            if any(room[0] == name for room in self.rooms):
                messagebox.showwarning("Duplicate Name", f"A room named '{name}' already exists.")
                return

            self.rooms.append((name, width, height, max_expansion))
            self.rooms_tree.insert("", tk.END, values=(name, width, height, max_expansion))

    def edit_room(self):
        selected_items = self.rooms_tree.selection()
        if not selected_items:
            messagebox.showwarning("No Selection", "Please select a room to edit.")
            return

        item = selected_items[0]
        values = self.rooms_tree.item(item, "values")
        old_name = values[0]

        # Check if max_expansion exists in values (for backward compatibility)
        max_expansion = int(values[3]) if len(values) > 3 else 1

        dialog = RoomDialog(self.root, "Edit Room", old_name, int(values[1]), int(values[2]), max_expansion)
        if dialog.result:
            name, width, height, max_expansion = dialog.result

            # Check if the new name conflicts with any existing room (except itself)
            if name != old_name and any(room[0] == name for room in self.rooms):
                messagebox.showwarning("Duplicate Name", f"A room named '{name}' already exists.")
                return

            index = self.rooms_tree.index(item)
            self.rooms[index] = (name, width, height, max_expansion)
            self.rooms_tree.item(item, values=(name, width, height, max_expansion))

            # Update adjacencies if the room name changed
            if name != old_name:
                for i, (room1, room2) in enumerate(self.adjacencies):
                    if room1 == old_name:
                        self.adjacencies[i] = (name, room2)
                    if room2 == old_name:
                        self.adjacencies[i] = (room1, name)

    def delete_room(self):
        selected_items = self.rooms_tree.selection()
        if not selected_items:
            messagebox.showwarning("No Selection", "Please select a room to delete.")
            return

        item = selected_items[0]
        room_name = self.rooms_tree.item(item, "values")[0]
        index = self.rooms_tree.index(item)

        # Delete the room
        self.rooms.pop(index)
        self.rooms_tree.delete(item)

        # Delete associated adjacencies
        adjacencies_to_remove = []
        for i, (room1, room2) in enumerate(self.adjacencies):
            if room1 == room_name or room2 == room_name:
                adjacencies_to_remove.append(i)

        for i in sorted(adjacencies_to_remove, reverse=True):
            self.adjacencies.pop(i)

        # Update the adjacency tree
        for item in self.adjacency_tree.get_children():
            values = self.adjacency_tree.item(item, "values")
            if values[0] == room_name or values[1] == room_name:
                self.adjacency_tree.delete(item)

    def add_adjacency(self):
        # Get all room names
        room_names = [room[0] for room in self.rooms]

        if len(room_names) < 2:
            messagebox.showwarning("Not Enough Rooms", "You need at least two rooms to define adjacencies.")
            return

        dialog = AdjacencyDialog(self.root, "Add Adjacency", room_names)
        if dialog.result:
            room1, room2 = dialog.result

            # Check if this adjacency already exists
            if (room1, room2) in self.adjacencies or (room2, room1) in self.adjacencies:
                messagebox.showwarning("Duplicate Adjacency",
                                       f"An adjacency between '{room1}' and '{room2}' already exists.")
                return

            self.adjacencies.append((room1, room2))
            self.adjacency_tree.insert("", tk.END, values=(room1, room2))

    def delete_adjacency(self):
        selected_items = self.adjacency_tree.selection()
        if not selected_items:
            messagebox.showwarning("No Selection", "Please select an adjacency to delete.")
            return

        item = selected_items[0]
        index = self.adjacency_tree.index(item)
        self.adjacencies.pop(index)
        self.adjacency_tree.delete(item)

    def generate_floor_plan(self):
        # Check if we have valid inputs
        if not self.shape_dimensions:
            messagebox.showerror("Error", "Please define at least one rectangle for the floor shape.")
            return

        if not self.rooms:
            messagebox.showerror("Error", "Please add at least one room.")
            return

        try:
            max_attempts = int(self.max_attempts_var.get())
            if max_attempts <= 0:
                raise ValueError("Max attempts must be a positive integer.")
        except ValueError as e:
            messagebox.showerror("Invalid Input", str(e))
            return

        try:
            # Create the floor plan with the shape dimensions from UI
            self.floor_plan = FloorPlan(self.shape_dimensions)

            # Add rooms from UI with max expansion parameter
            for room_data in self.rooms:
                if len(room_data) == 4:  # New format with max_expansion
                    name, width, height, max_expansion = room_data
                    self.floor_plan.add_room(name, width, height, max_expansion=max_expansion)
                else:  # Old format without max_expansion for backward compatibility
                    name, width, height = room_data
                    self.floor_plan.add_room(name, width, height)

            # Add adjacencies from UI
            for room1, room2 in self.adjacencies:
                self.floor_plan.add_adjacency(room1, room2)

            # Try to place rooms using your existing function
            success = self.floor_plan.place_rooms_with_constraints(
                max_attempts=max_attempts,
                enable_expansion=self.enable_expansion_var.get()
            )

            # Clear the visualization frame
            for widget in self.visualization_frame.winfo_children():
                widget.destroy()

            if not success:
                # Display an error message if placement failed
                ttk.Label(self.visualization_frame, text="Failed to place all rooms with the given constraints.\n"
                                                         "Try increasing max attempts or enabling room expansion.").pack(
                    pady=50)
                return

            # Create a matplotlib figure for visualization
            fig, ax = plt.subplots(figsize=(10, 8))

            # Draw floor shape
            for region in self.floor_plan.floor_regions:
                rect = patches.Rectangle(
                    (region['x'], region['y']),
                    region['width'],
                    region['height'],
                    linewidth=2,
                    edgecolor='black',
                    facecolor='none',
                    linestyle='--'
                )
                ax.add_patch(rect)

            # Draw rooms with colors
            colors = plt.cm.tab20(np.linspace(0, 1, len(self.floor_plan.rooms)))
            room_colors = {}

            for i, room in enumerate(self.floor_plan.rooms):
                room_colors[room.name] = colors[i]
                if room.x is not None and room.y is not None:
                    rect = patches.Rectangle(
                        (room.x, room.y),
                        room.width,
                        room.height,
                        linewidth=1,
                        edgecolor='black',
                        facecolor=colors[i],
                        alpha=0.7
                    )
                    ax.add_patch(rect)

                    # Add room name and size
                    ax.text(
                        room.x + room.width / 2,
                        room.y + room.height / 2,
                        f"{room.name}\n{room.width}x{room.height}",
                        ha='center',
                        va='center',
                        fontsize=8
                    )

            # Add adjacency relationships as lines between room centers
            for room1_name, room2_name in self.floor_plan.adjacency_graph.edges:
                room1 = next(r for r in self.floor_plan.rooms if r.name == room1_name)
                room2 = next(r for r in self.floor_plan.rooms if r.name == room2_name)

                if room1.x is not None and room2.x is not None:
                    center1 = (room1.x + room1.width / 2, room1.y + room1.height / 2)
                    center2 = (room2.x + room2.width / 2, room2.y + room2.height / 2)

                    # Check if rooms share a wall
                    if room1.has_shared_wall_with(room2):
                        ax.plot([center1[0], center2[0]], [center1[1], center2[1]], 'g-', linewidth=1.5)
                    else:
                        ax.plot([center1[0], center2[0]], [center1[1], center2[1]], 'r:', linewidth=0.8)

            # Set axis properties
            max_width = max(region['x'] + region['width'] for region in self.floor_plan.floor_regions)
            max_height = sum(region['height'] for region in self.floor_plan.floor_regions)
            ax.set_xlim(-1, max_width + 1)
            ax.set_ylim(-1, max_height + 1)
            ax.set_aspect('equal')
            ax.set_title('Generated Floor Plan')
            ax.set_xlabel('Width')
            ax.set_ylabel('Height')

            # Create a canvas to display the plot in tkinter
            canvas = FigureCanvasTkAgg(fig, master=self.visualization_frame)
            canvas_widget = canvas.get_tk_widget()
            canvas_widget.pack(fill=tk.BOTH, expand=True)
            canvas.draw()

            # Add statistics about the generated floor plan
            stats_frame = ttk.LabelFrame(self.info_frame, text="Floor Plan Statistics")
            stats_frame.pack(fill=tk.X, padx=10, pady=5)

            # Calculate total area and used area
            total_area = sum(region['width'] * region['height'] for region in self.floor_plan.floor_regions)
            used_area = sum(room.width * room.height for room in self.floor_plan.rooms if room.x is not None)
            efficiency = (used_area / total_area) * 100 if total_area > 0 else 0

            ttk.Label(stats_frame, text=f"Total Floor Area: {total_area} sq units").pack(anchor=tk.W, padx=5, pady=2)
            ttk.Label(stats_frame, text=f"Used Area: {used_area} sq units").pack(anchor=tk.W, padx=5, pady=2)
            ttk.Label(stats_frame, text=f"Space Efficiency: {efficiency:.1f}%").pack(anchor=tk.W, padx=5, pady=2)

            # Calculate adjacency satisfaction
            score, adjacent_pairs = self.floor_plan.evaluate_adjacency_score()
            adjacency_satisfaction = (score / len(self.floor_plan.adjacency_graph.edges)) * 100 if len(
                self.floor_plan.adjacency_graph.edges) > 0 else 0

            ttk.Label(stats_frame, text=f"Adjacency Satisfaction: {adjacency_satisfaction:.1f}%").pack(
                anchor=tk.W, padx=5, pady=2)

            # Add room details
            room_details_frame = ttk.LabelFrame(self.info_frame, text="Room Details")
            room_details_frame.pack(fill=tk.X, padx=10, pady=5)

            # Create a treeview for room details
            room_details_tree = ttk.Treeview(
                room_details_frame,
                columns=("Room", "Position", "Size", "Area", "Adjacencies"),
                show="headings"
            )

            room_details_tree.heading("Room", text="Room")
            room_details_tree.heading("Position", text="Position (x,y)")
            room_details_tree.heading("Size", text="Size (w×h)")
            room_details_tree.heading("Area", text="Area")
            room_details_tree.heading("Adjacencies", text="Adjacent Rooms")

            room_details_tree.column("Room", width=100)
            room_details_tree.column("Position", width=100)
            room_details_tree.column("Size", width=80)
            room_details_tree.column("Area", width=80)
            room_details_tree.column("Adjacencies", width=200)

            room_details_tree.pack(fill=tk.X, expand=True, padx=5, pady=5)

            # Populate room details
            for room in self.floor_plan.rooms:
                if room.x is not None and room.y is not None:
                    # Find adjacencies for this room
                    adjacent_rooms = []
                    for room1_name, room2_name in self.floor_plan.adjacency_graph.edges:
                        if room1_name == room.name:
                            adjacent_rooms.append(room2_name)
                        elif room2_name == room.name:
                            adjacent_rooms.append(room1_name)

                    room_details_tree.insert(
                        "",
                        tk.END,
                        values=(
                            room.name,
                            f"({room.x}, {room.y})",
                            f"{room.width}×{room.height}",
                            room.width * room.height,
                            ", ".join(adjacent_rooms)
                        )
                    )

            # Add a button to save the floor plan image
            save_button = ttk.Button(
                self.info_frame,
                text="Save Floor Plan Image",
                command=lambda: self.save_floor_plan_image(fig)
            )
            save_button.pack(pady=10)

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while generating the floor plan: {str(e)}")
            import traceback
            traceback.print_exc()

    def save_floor_plan_image(self, fig):
        """Save the floor plan image to a file."""
        from tkinter import filedialog

        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG Image", "*.png"), ("JPEG Image", "*.jpg"), ("PDF Document", "*.pdf")]
        )

        if file_path:
            try:
                fig.savefig(file_path, dpi=300, bbox_inches='tight')
                messagebox.showinfo("Success", f"Floor plan saved to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save image: {str(e)}")


def main():
    """
    Main function to run the Floor Plan Generator application.
    """
    root = tk.Tk()
    root.title("Floor Plan Generator")

    # Set theme - 'clam', 'alt', 'default', or 'classic'
    style = ttk.Style()
    style.theme_use('clam')

    # Configure colors for better look and feel
    style.configure('TButton', background='#4CAF50', foreground='black')
    style.configure('TLabel', background='#f0f0f0', foreground='#333333')
    style.configure('TFrame', background='#f0f0f0')

    # Create the application
    app = FloorPlanApp(root)

    # Center the window on the screen
    window_width = 1200
    window_height = 800
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    center_x = int((screen_width - window_width) / 2)
    center_y = int((screen_height - window_height) / 2)
    root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')

    # Make it resizable
    root.minsize(800, 600)

    # Run the main loop
    root.mainloop()


# Run the application when the script is executed directly
if __name__ == "__main__":
    main()