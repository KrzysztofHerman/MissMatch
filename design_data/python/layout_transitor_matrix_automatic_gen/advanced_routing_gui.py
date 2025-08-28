#!/usr/bin/env python3
"""
GUI Avanzada para diseño de ruteo de gates - VERSIÓN MANHATTAN ESTRICTA
- Dummies solo en columnas izquierda y derecha
- Orientación correcta: |DRAIN|GATE(POLY)|SOURCE|
- Ruteo estrictamente Manhattan (solo H/V)
- Exporta diccionario Python al portapapeles
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import json
import math
from datetime import datetime

class EnhancedManhattanRouter:
    """Enhanced Manhattan router with multiple turns and preview support"""
    
    def __init__(self, grid_snap=0.05):
        self.grid_snap = grid_snap
        self.segments = []
        self.points = []  # Store all routing points
        self.current_point = None
        self.routing_state = 'IDLE'  # IDLE, ROUTING, ADDING_POINTS
        self.route_points = []  # Store waypoints
        
    def start_route(self, x, y):
        """Start a new route"""
        self.segments = []
        self.points = []
        self.current_point = self.snap_to_grid(x, y)
        self.points.append(self.current_point)
        return self.current_point
    
    def snap_to_grid(self, x, y):
        """Snap coordinates to grid"""
        x_snap = round(x / self.grid_snap) * self.grid_snap
        y_snap = round(y / self.grid_snap) * self.grid_snap
        return (x_snap, y_snap)
    
    def add_point(self, x, y):
        """Add a point to the route (allows multiple turns)"""
        if not self.current_point:
            return []
        
        target = self.snap_to_grid(x, y)
        
        # Don't add if same as current point
        if target == self.current_point:
            return []
        
        # Store the point
        self.points.append(target)
        
        # Create Manhattan segments from current to target
        segments_added = self.create_manhattan_path(self.current_point, target)
        
        self.segments.extend(segments_added)
        self.current_point = target
        
        return segments_added
    
    def get_preview_segments(self, x, y):
        """Get preview segments for current mouse position without committing"""
        if not self.current_point:
            return []
        
        target = self.snap_to_grid(x, y)
        
        # Don't preview if same as current point
        if target == self.current_point:
            return []
        
        # Create preview segments from current point to target
        return self.create_manhattan_path(self.current_point, target)
    
    def create_manhattan_path(self, start, end):
        """Create Manhattan path between two points"""
        segments = []
        curr_x, curr_y = start
        end_x, end_y = end
        
        dx = abs(end_x - curr_x)
        dy = abs(end_y - curr_y)
        
        # Create L-shaped path
        if dx > 0.01 and dy > 0.01:
            # Both horizontal and vertical needed
            # Default: horizontal first, then vertical
            # (User can control by adding intermediate points)
            
            # Horizontal segment
            h_end = (end_x, curr_y)
            segments.append({
                'type': 'horizontal',
                'start': (curr_x, curr_y),
                'end': h_end
            })
            
            # Vertical segment
            segments.append({
                'type': 'vertical',
                'start': h_end,
                'end': (end_x, end_y)
            })
        elif dx > 0.01:
            # Only horizontal
            segments.append({
                'type': 'horizontal',
                'start': (curr_x, curr_y),
                'end': (end_x, end_y)
            })
        elif dy > 0.01:
            # Only vertical
            segments.append({
                'type': 'vertical',
                'start': (curr_x, curr_y),
                'end': (end_x, end_y)
            })
        
        return segments
    
    def finish_route(self):
        """Finish the route and return all segments"""
        result = self.segments.copy()
        self.segments = []
        self.points = []
        self.current_point = None
        return result
    
    def get_route_info(self):
        """Get comprehensive route information"""
        if len(self.points) < 2:
            return None
        
        # Calculate total lengths
        h_length = 0
        v_length = 0
        
        for seg in self.segments:
            if seg['type'] == 'horizontal':
                h_length += abs(seg['end'][0] - seg['start'][0])
            else:
                v_length += abs(seg['end'][1] - seg['start'][1])
        
        # Get exit point and direction
        start_point = self.points[0]
        exit_point = self.points[-1] if self.points else start_point
        
        # Determine primary exit direction
        exit_direction = self.determine_exit_direction(start_point, exit_point)
        
        return {
            'points': self.points.copy(),
            'segments': self.segments.copy(),
            'h_length': h_length,
            'v_length': v_length,
            'exit_point': exit_point,
            'exit_direction': exit_direction,
            'start_point': start_point
        }
    
    def determine_exit_direction(self, start, end):
        """Determine primary exit direction"""
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        
        # Based on larger displacement
        if abs(dx) > abs(dy):
            return 'right' if dx > 0 else 'left'
        else:
            return 'up' if dy < 0 else 'down'  # Note: canvas Y increases downward
    
    def get_current_segments(self):
        """Get all current segments (for debugging)"""
        return self.segments.copy()
    
    def get_points(self):
        """Get all routing points"""
        return self.points.copy()


class AdvancedRoutingGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Gate Routing Designer - Manhattan Routing")
        
        # Array parameters
        self.array_rows = 5
        self.array_cols = 5
        self.dummy_mode = 'full'  # 'none', 'sides', or 'full'
        
        # ====== CONFIGURABLE TRANSISTOR DIMENSIONS (µm) ======
        # These should match your PDK requirements
        self.transistor_W = 1.03    # Width (µm) - configurable
        self.transistor_L = 0.35    # Length (µm) - configurable
        
        # Spacing parameters (µm)
        self.guardring_width = 0.5   # Guardring width
        self.guardring_spacing = 2.0  # Distance from transistor to guardring (configurable, default 2µm)
        
        # For GUI visualization - transistor appears as a box
        # The actual transistor dimensions from PDK
        self.transistor_width = self.transistor_W    # Physical width in X direction
        self.transistor_height = self.transistor_L * 4  # Approximate height for visualization
        
        # Calculate pitch dynamically based on dimensions
        # Pitch = transistor_dimension + 2*spacing + guardring_width (shared)
        self.pitch_x = self.transistor_width + 2 * self.guardring_spacing + self.guardring_width
        self.pitch_y = self.transistor_height + 2 * self.guardring_spacing + self.guardring_width
        
        # Add routing configuration
        self.exit_pitch = 1.0  # µm - Pitch between exit points
        self.exit_alignment = 'auto'  # 'auto', 'top', 'bottom', 'left', 'right'
        self.allow_multi_turn = True  # Allow multiple 90° turns

        # Metal widths
        self.metal3_width = 0.2  # µm
        
        # Display parameters
        self.zoom_level = 50.0    # pixels/µm
        self.grid_spacing = 0.5   # µm
        self.canvas_width = 800
        self.canvas_height = 600
        
        # Canvas offset for pan
        self.canvas_offset_x = 50
        self.canvas_offset_y = 50
        
        # State
        self.transistors = {}
        self.routing_segments = []
        self.drawing = False
        self.selected_transistor = None
        self.selected_segment = None
        self.mouse_start = None
        self.manhattan_router = None
        self.routing_state = 'IDLE'  # IDLE, ROUTING, ADDING_POINTS
        self.route_points = []        # Store waypoints during routing
        self.temp_segments = []       # Store temporary visual segments

        self.routing_active = False
        self.current_route = []
        self.last_point = None

        self.gate_size = 0.15  
        self.drain_source_size = 0.15
        
        
        # Edit mode
        self.edit_mode = 'draw'
        
        # Auto clone mode
        self.auto_clone_enabled = True
        
        # Colors (unchanged)
        self.colors = {
            'bg': '#f8f8f8',
            'grid': '#e0e0e0',
            'grid_major': '#c0c0c0',
            'transistor': '#d0d0d0',
            'dummy': '#a0a0a0',
            'gate': '#ff4444',
            'gate_selected': '#ffaa44',
            'routing': '#0066ff',
            'routing_selected': '#00aaff',
            'routing_preview': '#88ccff',
            'guardring': '#666666',
            'text': '#333333',
            'drain': '#44ff44',
            'source': '#4444ff'
        }
        
        self.setup_ui()
        self.create_array()
        self.draw_canvas()
        
        # Show configuration in instructions
        self.show_configuration_info()

    def show_configuration_info(self):
        """Display current configuration"""
        instructions = f"""MANHATTAN ROUTING - SCALABLE CONFIGURATION
        
    Current Configuration:
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    • Device Type: {self.device_type_var.get() if hasattr(self, 'device_type_var') else 'nmos'}
    • Transistor Width (W): {self.transistor_W:.2f} µm
    • Transistor Length (L): {self.transistor_L:.2f} µm
    • Guardring Spacing: {self.guardring_spacing:.2f} µm
    • Array: {self.array_rows}x{self.array_cols}
    • Dummy Mode: {self.dummy_mode_var.get()}
    • Calculated Pitch X: {self.pitch_x:.2f} µm
    • Calculated Pitch Y: {self.pitch_y:.2f} µm

    Array Structure:
    """
        
        # Show array structure based on dummy mode
        dummy_mode = self.dummy_mode_var.get()
        if dummy_mode == 'full':
            instructions += """
    [D] [D]    [D]    [D]    [D]    [D]
    [D] [G0,0] [G0,1] [G0,2] [G0,3] [D]
    [D] [G1,0] [G1,1] [G1,2] [G1,3] [D]
    [D] [G2,0] [G2,1] [G2,2] [G2,3] [D]
    [D] [G3,0] [G3,1] [G3,2] [G3,3] [D]
    [D] [D]    [D]    [D]    [D]    [D]
    """
        elif dummy_mode == 'sides':
            instructions += """
    [D] [G0,0] [G0,1] [G0,2] [G0,3] [D]
    [D] [G1,0] [G1,1] [G1,2] [G1,3] [D]
    [D] [G2,0] [G2,1] [G2,2] [G2,3] [D]
    [D] [G3,0] [G3,1] [G3,2] [G3,3] [D]
    """
        else:
            instructions += """
    [G0,0] [G0,1] [G0,2] [G0,3]
    [G1,0] [G1,1] [G1,2] [G1,3]
    [G2,0] [G2,1] [G2,2] [G2,3]
    [G3,0] [G3,1] [G3,2] [G3,3]
    """
        
        instructions += """
    D = Dummy transistor
    G = Active transistor with GUI coordinates

    Coordinate Mapping:
    • GUI: Row 0 = TOP, Row N = BOTTOM
    • KLayout: Row 0 = BOTTOM, Row N = TOP
    • Mapping: KL_row = (N-1) - GUI_row

    Tips:
    • Routes snap to 50nm grid
    • Auto-clone enabled by default
    • Column 0 routes clone to other columns
    """
        
        self.report_text.delete(1.0, tk.END)
        self.report_text.insert(1.0, instructions)
  
    def show_dimension_dialog(self):
        """Show dialog to configure transistor dimensions"""
        import tkinter.simpledialog as sd
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Configure Transistor Dimensions")
        dialog.geometry("400x300")
        
        # Width input
        ttk.Label(dialog, text="Transistor Width W (µm):").grid(row=0, column=0, padx=10, pady=5, sticky='e')
        w_var = tk.DoubleVar(value=self.transistor_W)
        ttk.Entry(dialog, textvariable=w_var, width=10).grid(row=0, column=1, padx=10, pady=5)
        
        # Length input
        ttk.Label(dialog, text="Transistor Length L (µm):").grid(row=1, column=0, padx=10, pady=5, sticky='e')
        l_var = tk.DoubleVar(value=self.transistor_L)
        ttk.Entry(dialog, textvariable=l_var, width=10).grid(row=1, column=1, padx=10, pady=5)
        
        # Spacing input
        ttk.Label(dialog, text="Guardring Spacing (µm):").grid(row=2, column=0, padx=10, pady=5, sticky='e')
        spacing_var = tk.DoubleVar(value=self.guardring_spacing)
        ttk.Entry(dialog, textvariable=spacing_var, width=10).grid(row=2, column=1, padx=10, pady=5)
        
        # Info display
        info_label = ttk.Label(dialog, text="", foreground="blue")
        info_label.grid(row=3, column=0, columnspan=2, padx=10, pady=10)
        
        def update_info(*args):
            """Update calculated pitch display"""
            try:
                w = w_var.get()
                l = l_var.get()
                spacing = spacing_var.get()
                pitch_x = w + 2 * spacing + self.guardring_width
                pitch_y = l * 4 + 2 * spacing + self.guardring_width  # Approximate height
                info_label.config(text=f"Calculated pitch: X={pitch_x:.2f}µm, Y={pitch_y:.2f}µm")
            except:
                pass
        
        w_var.trace('w', update_info)
        l_var.trace('w', update_info)
        spacing_var.trace('w', update_info)
        update_info()
        
        def apply_dimensions():
            """Apply new dimensions and recreate array"""
            self.transistor_W = w_var.get()
            self.transistor_L = l_var.get()
            self.guardring_spacing = spacing_var.get()
            
            # Recalculate derived parameters
            self.transistor_width = self.transistor_W
            self.transistor_height = self.transistor_L * 4
            self.pitch_x = self.transistor_width + 2 * self.guardring_spacing + self.guardring_width
            self.pitch_y = self.transistor_height + 2 * self.guardring_spacing + self.guardring_width
            
            # Clear and recreate
            self.routing_segments.clear()
            self.create_array()
            self.draw_canvas()
            self.show_configuration_info()
            
            dialog.destroy()
            
            messagebox.showinfo("Configuration Updated", 
                            f"New configuration:\n"
                            f"W={self.transistor_W:.2f}µm, L={self.transistor_L:.2f}µm\n"
                            f"Pitch: X={self.pitch_x:.2f}µm, Y={self.pitch_y:.2f}µm")
        
        ttk.Button(dialog, text="Apply", command=apply_dimensions).grid(row=4, column=0, padx=10, pady=10)
        ttk.Button(dialog, text="Cancel", command=dialog.destroy).grid(row=4, column=1, padx=10, pady=10)

    def setup_ui(self):
        """Configure user interface with dimension configuration"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="5")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Toolbar
        toolbar = ttk.Frame(main_frame)
        toolbar.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        # Add routing configuration section
        ttk.Separator(toolbar, orient='vertical').pack(side=tk.LEFT, fill='y', padx=10)
        ttk.Label(toolbar, text="Exit:").pack(side=tk.LEFT, padx=5)
        
        # Exit alignment selector
        self.exit_align_var = tk.StringVar(value='auto')
        exit_frame = ttk.Frame(toolbar)
        exit_frame.pack(side=tk.LEFT)
        
        ttk.Radiobutton(exit_frame, text="Auto", 
                        variable=self.exit_align_var, 
                        value='auto').pack(side=tk.LEFT)
        ttk.Radiobutton(exit_frame, text="Top", 
                        variable=self.exit_align_var, 
                        value='top').pack(side=tk.LEFT)
        ttk.Radiobutton(exit_frame, text="Right", 
                        variable=self.exit_align_var, 
                        value='right').pack(side=tk.LEFT)
        ttk.Radiobutton(exit_frame, text="Bottom", 
                        variable=self.exit_align_var, 
                        value='bottom').pack(side=tk.LEFT)
        ttk.Radiobutton(exit_frame, text="Left", 
                        variable=self.exit_align_var, 
                        value='left').pack(side=tk.LEFT)
        
        # Exit pitch control
        ttk.Label(toolbar, text="Pitch:").pack(side=tk.LEFT, padx=5)
        self.exit_pitch_var = tk.DoubleVar(value=1.0)
        ttk.Spinbox(toolbar, from_=0.5, to=5.0, increment=0.1, width=6,
                    textvariable=self.exit_pitch_var,
                    command=self.update_exit_pitch).pack(side=tk.LEFT)
        ttk.Label(toolbar, text="µm").pack(side=tk.LEFT)
        
        
        # Manhattan routing indicator
        manhattan_label = ttk.Label(toolbar, text="MANHATTAN ROUTING", 
                                font=('Arial', 10, 'bold'), foreground='green')
        manhattan_label.pack(side=tk.LEFT, padx=10)
        
        ttk.Separator(toolbar, orient='vertical').pack(side=tk.LEFT, fill='y', padx=5)

        ttk.Button(toolbar, text="⚙ Configure", 
                command=self.show_dimension_dialog).pack(side=tk.LEFT, padx=5)
        
        ttk.Separator(toolbar, orient='vertical').pack(side=tk.LEFT, fill='y', padx=5)
        
        # Array controls
        ttk.Label(toolbar, text="Array:").pack(side=tk.LEFT, padx=5)
        
        self.rows_var = tk.IntVar(value=self.array_rows)
        ttk.Spinbox(toolbar, from_=2, to=20, width=5, textvariable=self.rows_var,
                command=self.update_array).pack(side=tk.LEFT)
        
        ttk.Label(toolbar, text="x").pack(side=tk.LEFT, padx=2)
        
        self.cols_var = tk.IntVar(value=self.array_cols)
        ttk.Spinbox(toolbar, from_=2, to=20, width=5, textvariable=self.cols_var,
                command=self.update_array).pack(side=tk.LEFT)
        
        ttk.Separator(toolbar, orient='vertical').pack(side=tk.LEFT, fill='y', padx=10)
        ttk.Label(toolbar, text="Dummies:").pack(side=tk.LEFT, padx=5)
        self.dummy_mode_var = tk.StringVar(value='sides')
        dummy_frame = ttk.Frame(toolbar)
        dummy_frame.pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(dummy_frame, text="None", 
                        variable=self.dummy_mode_var, 
                        value='none',
                        command=self.update_array).pack(side=tk.LEFT)
        ttk.Radiobutton(dummy_frame, text="Sides", 
                        variable=self.dummy_mode_var, 
                        value='sides',
                        command=self.update_array).pack(side=tk.LEFT)
        ttk.Radiobutton(dummy_frame, text="Full Ring", 
                        variable=self.dummy_mode_var, 
                        value='full',
                        command=self.update_array).pack(side=tk.LEFT)
        
        # Auto-clone checkbox
        self.auto_clone_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(toolbar, text="Auto-Clone Patterns", variable=self.auto_clone_var,
                        command=self.toggle_auto_clone).pack(side=tk.LEFT, padx=10)
        
        # Device type selector (if you have PMOS support)
        if hasattr(self, 'device_type_var'):
            ttk.Separator(toolbar, orient='vertical').pack(side=tk.LEFT, fill='y', padx=10)
            ttk.Label(toolbar, text="Device:").pack(side=tk.LEFT, padx=5)
            device_frame = ttk.Frame(toolbar)
            device_frame.pack(side=tk.LEFT)
            ttk.Radiobutton(device_frame, text="NMOS", 
                            variable=self.device_type_var, 
                            value='nmos').pack(side=tk.LEFT)
            ttk.Radiobutton(device_frame, text="PMOS", 
                            variable=self.device_type_var, 
                            value='pmos').pack(side=tk.LEFT)
        else:
            # Initialize if not exists
            self.device_type_var = tk.StringVar(value='nmos')

        # Separador
        ttk.Separator(toolbar, orient='vertical').pack(side=tk.LEFT, fill='y', padx=10)
        
        # Controles de zoom
        ttk.Label(toolbar, text="Zoom:").pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="-", width=3, 
                  command=self.zoom_out).pack(side=tk.LEFT)
        self.zoom_label = ttk.Label(toolbar, text=f"{self.zoom_level:.0f}x")
        self.zoom_label.pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="+", width=3, 
                  command=self.zoom_in).pack(side=tk.LEFT)
        ttk.Button(toolbar, text="Fit", 
                  command=self.zoom_fit).pack(side=tk.LEFT, padx=5)
        
        # Separador
        ttk.Separator(toolbar, orient='vertical').pack(side=tk.LEFT, fill='y', padx=10)
        
        # Modo de edición
        ttk.Label(toolbar, text="Mode:").pack(side=tk.LEFT, padx=5)
        self.mode_var = tk.StringVar(value='draw')
        ttk.Radiobutton(toolbar, text="Draw", variable=self.mode_var, 
                       value='draw').pack(side=tk.LEFT)
        ttk.Radiobutton(toolbar, text="Delete", variable=self.mode_var, 
                       value='delete').pack(side=tk.LEFT)
        
        # Frame del canvas
        canvas_frame = ttk.Frame(main_frame)
        canvas_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Canvas con scrollbars
        h_scrollbar = ttk.Scrollbar(canvas_frame, orient="horizontal")
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        v_scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical")
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        self.canvas = tk.Canvas(canvas_frame, 
                               width=self.canvas_width,
                               height=self.canvas_height,
                               bg=self.colors['bg'],
                               xscrollcommand=h_scrollbar.set,
                               yscrollcommand=v_scrollbar.set)
        self.canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        h_scrollbar.config(command=self.canvas.xview)
        v_scrollbar.config(command=self.canvas.yview)
        
        # Bind eventos del canvas
        self.canvas.bind("<Button-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)
        self.canvas.bind("<Button-3>", self.on_right_click)
        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)
        self.canvas.bind("<Control-MouseWheel>", self.on_ctrl_mouse_wheel)
        self.canvas.bind("<Motion>", self.on_mouse_move)

        self.root.bind("<Escape>", self.on_key_press)

            
        # Panel derecho
        right_panel = ttk.Frame(main_frame)
        right_panel.grid(row=1, column=1, sticky=(tk.N, tk.S), padx=5)
        
        # Información de coordenadas
        coord_frame = ttk.LabelFrame(right_panel, text="Coordinates", padding="10")
        coord_frame.pack(fill=tk.X, pady=5)
        
        self.coord_label = ttk.Label(coord_frame, text="X: 0.00 µm\nY: 0.00 µm")
        self.coord_label.pack()
        
        # Botones de acción
        action_frame = ttk.LabelFrame(right_panel, text="Actions", padding="10")
        action_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(action_frame, text="Clear All Routes",
                  command=self.clear_all_routes).pack(fill=tk.X, pady=2)
        ttk.Button(action_frame, text="Load Pattern",
                  command=self.load_pattern).pack(fill=tk.X, pady=2)
        ttk.Button(action_frame, text="Save Pattern",
                  command=self.save_pattern).pack(fill=tk.X, pady=2)
        ttk.Button(action_frame, text="Generate Report",
                  command=self.generate_report).pack(fill=tk.X, pady=2)
        ttk.Button(action_frame, text="Copy Pattern Dict",
                command=self.copy_pattern_dict).pack(fill=tk.X, pady=2)
        ttk.Button(action_frame, text="Route Drains/Sources",
              command=self.create_drain_source_routes).pack(fill=tk.X, pady=2)
        
        # Estadísticas
        stats_frame = ttk.LabelFrame(right_panel, text="Statistics", padding="10")
        stats_frame.pack(fill=tk.X, pady=5)
        
        self.stats_label = ttk.Label(stats_frame, text="Segments: 0\nRouted: 0/0")
        self.stats_label.pack()
        
        # Reporte
        report_frame = ttk.LabelFrame(right_panel, text="Report", padding="5")
        report_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.report_text = scrolledtext.ScrolledText(report_frame, width=40, height=20)
        self.report_text.pack(fill=tk.BOTH, expand=True)
        
        # Configurar grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        canvas_frame.columnconfigure(0, weight=1)
        canvas_frame.rowconfigure(0, weight=1)
    
    def update_exit_pitch(self):
        """Update exit pitch value"""
        self.exit_pitch = self.exit_pitch_var.get()
        print(f"Exit pitch set to: {self.exit_pitch} µm")

    def um_to_canvas(self, x_um, y_um):
        """Convierte coordenadas de micrómetros a pixels del canvas"""
        x = x_um * self.zoom_level + self.canvas_offset_x
        y = y_um * self.zoom_level + self.canvas_offset_y
        return x, y
    
    def canvas_to_um(self, x, y):
        """Convierte coordenadas del canvas a micrómetros"""
        x_um = (x - self.canvas_offset_x) / self.zoom_level
        y_um = (y - self.canvas_offset_y) / self.zoom_level
        return x_um, y_um
    
    def create_array(self):
        """Create array with configurable dummy arrangement"""
        self.transistors.clear()
        rows = self.rows_var.get()
        cols = self.cols_var.get()
        
        dummy_mode = self.dummy_mode_var.get()
        
        # Calculate total dimensions based on dummy mode
        if dummy_mode == 'none':
            total_rows = rows
            total_cols = cols
        elif dummy_mode == 'sides':
            total_rows = rows
            total_cols = cols + 2  # Add side columns
        else:  # full ring
            total_rows = rows + 2  # Add top and bottom
            total_cols = cols + 2  # Add sides
        
        for row in range(total_rows):
            for col in range(total_cols):
                # Determine if dummy based on mode
                is_dummy = False
                
                if dummy_mode == 'sides':
                    is_dummy = (col == 0 or col == total_cols-1)
                elif dummy_mode == 'full':
                    is_dummy = (row == 0 or row == total_rows-1 or 
                            col == 0 or col == total_cols-1)
                
                # Calculate position
                x = col * self.pitch_x
                y = row * self.pitch_y
                
                # Calculate active indices (for non-dummy transistors)
                if is_dummy:
                    active_row = -1
                    active_col = -1
                else:
                    if dummy_mode == 'none':
                        active_row = row
                        active_col = col
                    elif dummy_mode == 'sides':
                        active_row = row
                        active_col = col - 1
                    else:  # full ring
                        active_row = row - 1
                        active_col = col - 1
                
                self.transistors[(row, col)] = {
                    'row': row,
                    'col': col,
                    'active_row': active_row,
                    'active_col': active_col,
                    'x': x,
                    'y': y,
                    'is_dummy': is_dummy,
                    'routed': False
                }


    def draw_canvas(self):
        """Dibuja todo el canvas"""
        self.canvas.delete("all")
        
        # Calcular límites
        if self.transistors:
            max_x = max(t['x'] for t in self.transistors.values()) + self.pitch_x
            max_y = max(t['y'] for t in self.transistors.values()) + self.pitch_y
        else:
            max_x = max_y = 100
        
        # Dibujar grid
        self.draw_grid(max_x, max_y)
        
        # Dibujar transistores
        for t in self.transistors.values():
            self.draw_transistor(t)
        
        # Dibujar rutas
        for segment in self.routing_segments:
            self.draw_segment(segment)
        
        # Dibujar indicadores de dirección
        self.draw_direction_indicators()
        
        # Actualizar scroll region
        bbox = self.canvas.bbox("all")
        if bbox:
            self.canvas.configure(scrollregion=bbox)
    
    def draw_grid(self, max_x, max_y):
        """Dibuja el grid en micrómetros"""
        # Grid menor (cada 0.5 µm)
        for x in range(int(-10), int(max_x + 10)):
            if x % 5 == 0:
                color = self.colors['grid_major']
                width = 2
            else:
                color = self.colors['grid']
                width = 1
            
            x1, y1 = self.um_to_canvas(x * self.grid_spacing, -10)
            x2, y2 = self.um_to_canvas(x * self.grid_spacing, max_y + 10)
            self.canvas.create_line(x1, y1, x2, y2, fill=color, width=width, tags="grid")
        
        for y in range(int(-10), int(max_y + 10)):
            if y % 5 == 0:
                color = self.colors['grid_major']
                width = 2
            else:
                color = self.colors['grid']
                width = 1
            
            x1, y1 = self.um_to_canvas(-10, y * self.grid_spacing)
            x2, y2 = self.um_to_canvas(max_x + 10, y * self.grid_spacing)
            self.canvas.create_line(x1, y1, x2, y2, fill=color, width=width, tags="grid")
        
        # Etiquetas de coordenadas (cada 5 µm)
        for x in range(0, int(max_x) + 5, 5):
            cx, cy = self.um_to_canvas(x, -2)
            self.canvas.create_text(cx, cy, text=f"{x}", font=('Arial', 8),
                                   anchor='n', tags="grid")
        
        for y in range(0, int(max_y) + 5, 5):
            cx, cy = self.um_to_canvas(-2, y)
            self.canvas.create_text(cx, cy, text=f"{y}", font=('Arial', 8),
                                   anchor='e', tags="grid")
    
    def draw_transistor(self, t):
        """Draw transistor with LARGER terminals for better visibility"""
        x, y = t['x'], t['y']
        
        # Convert to canvas
        x1, y1 = self.um_to_canvas(x, y)
        x2, y2 = self.um_to_canvas(x + self.transistor_width, 
                                    y + self.transistor_height)
        
        # Device type
        device_type = self.device_type_var.get() if hasattr(self, 'device_type_var') else 'nmos'
        
        # Color based on type and dummy status
        if t['is_dummy']:
            fill_color = self.colors['dummy']
        else:
            fill_color = '#e0d0d0' if device_type == 'pmos' else self.colors['transistor']
        
        # Draw transistor rectangle
        rect = self.canvas.create_rectangle(x1, y1, x2, y2,
                                        fill=fill_color,
                                        outline='black',
                                        width=2,
                                        tags=f"transistor_{t['row']}_{t['col']}")
        
        # DRAIN (left) - TAMAÑO AUMENTADO
        drain_x = x + self.transistor_width * 0.2
        drain_y = y + self.transistor_height / 2
        dx1, dy1 = self.um_to_canvas(drain_x - self.drain_source_size, 
                                    drain_y - self.drain_source_size)
        dx2, dy2 = self.um_to_canvas(drain_x + self.drain_source_size, 
                                    drain_y + self.drain_source_size)
        self.canvas.create_oval(dx1, dy1, dx2, dy2,
                            fill='#44ff44', outline='darkgreen', width=2,
                            tags=f"drain_{t['row']}_{t['col']}")
        
        # GATE (center) - LÍNEA MÁS GRUESA Y VISIBLE
        gate_x = x + self.transistor_width / 2
        gate_color = '#4444ff' if device_type == 'pmos' else self.colors['gate']
        gx1, gy1 = self.um_to_canvas(gate_x - self.gate_size, y + 0.1)
        gx2, gy2 = self.um_to_canvas(gate_x + self.gate_size, y + self.transistor_height - 0.1)
        self.canvas.create_rectangle(gx1, gy1, gx2, gy2,
                                fill=gate_color,
                                outline='darkred' if device_type == 'nmos' else 'darkblue',
                                width=3,  # Más grueso
                                tags=f"gate_{t['row']}_{t['col']}")
        
        # SOURCE (right) - TAMAÑO AUMENTADO
        source_x = x + self.transistor_width * 0.8
        source_y = y + self.transistor_height / 2
        sx1, sy1 = self.um_to_canvas(source_x - self.drain_source_size, 
                                    source_y - self.drain_source_size)
        sx2, sy2 = self.um_to_canvas(source_x + self.drain_source_size, 
                                    source_y + self.drain_source_size)
        self.canvas.create_oval(sx1, sy1, sx2, sy2,
                            fill='#4444ff', outline='darkblue', width=2,
                            tags=f"source_{t['row']}_{t['col']}")
        
        # Label
        if t['is_dummy']:
            label = f"D[{t['row']},{t['col']}]"
        else:
            active_row = t['active_row']
            active_col = t['active_col']
            if active_row >= 0 and active_col >= 0:
                label = f"G[{active_row},{active_col}]"
            else:
                label = "ERR"
        
        lx, ly = self.um_to_canvas(x + self.transistor_width/2, y + self.transistor_height + 0.2)
        self.canvas.create_text(lx, ly, text=label, font=('Arial', 10, 'bold'),
                            anchor='n', tags=f"label_{t['row']}_{t['col']}")

    def draw_direction_indicators(self):
        """Dibuja indicadores de dirección de salida"""
        if not self.transistors:
            return
        
        # Encontrar centro del array
        active_transistors = [t for t in self.transistors.values() if not t['is_dummy']]
        if not active_transistors:
            return
        
        min_y = min(t['y'] for t in active_transistors)
        max_y = max(t['y'] for t in active_transistors) + self.transistor_height
        center_y = (min_y + max_y) / 2
        
        # Línea de centro
        x1, y1 = self.um_to_canvas(-5, center_y)
        x2, y2 = self.um_to_canvas(max(t['x'] for t in self.transistors.values()) + 10, center_y)
        self.canvas.create_line(x1, y1, x2, y2, fill='red', width=2, dash=(5, 5))
        
        # Etiquetas
        tx, ty = self.um_to_canvas(-8, min_y)
        self.canvas.create_text(tx, ty, text="↑ UP", fill='blue', 
                               font=('Arial', 10, 'bold'), anchor='w')
        
        tx, ty = self.um_to_canvas(-8, max_y)
        self.canvas.create_text(tx, ty, text="↓ DOWN", fill='blue', 
                               font=('Arial', 10, 'bold'), anchor='w')
        
        tx, ty = self.um_to_canvas(-8, center_y)
        self.canvas.create_text(tx, ty, text="CENTER", fill='red', 
                               font=('Arial', 10, 'bold'), anchor='w')
    
    def draw_segment(self, segment):
        """Modified to handle different route types with different colors"""
        x1, y1 = self.um_to_canvas(segment['x1'], segment['y1'])
        x2, y2 = self.um_to_canvas(segment['x2'], segment['y2'])
        
        # Choose color based on route type
        route_type = segment.get('route_type', 'gate')
        if route_type == 'drain':
            color = '#44ff44'  # Green for drain
        elif route_type == 'source':
            color = '#4444ff'  # Blue for source
        elif route_type in ['drain_via', 'source_via']:
            color = '#ff44ff'  # Magenta for vias
        else:
            color = self.colors.get('routing', '#0066ff')  # Default gate color
        
        if segment.get('selected', False):
            color = self.colors['routing_selected']
        
        width = max(2, int(self.metal3_width * self.zoom_level))
        
        # Draw via markers as circles
        if segment['type'] == 'via':
            radius = 5
            self.canvas.create_oval(x1-radius, y1-radius, x2+radius, y2+radius,
                                    fill=color, outline='black',
                                    tags=f"segment_{segment['id']}")
        else:
            line = self.canvas.create_line(x1, y1, x2, y2,
                                        fill=color,
                                        width=width,
                                        capstyle='projecting',
                                        tags=f"segment_{segment['id']}")
            segment['canvas_id'] = line
    
    def find_transistor_at(self, x_um, y_um):
        """Find transistor at coordinates - with LARGER hit area"""
        for t in self.transistors.values():
            gate_x = t['x'] + self.transistor_width / 2
            gate_y = t['y'] + self.transistor_height / 2
            
            # Área de click más grande
            if (abs(x_um - gate_x) < 0.3 and  # Aumentado de 0.2 a 0.3
                abs(y_um - gate_y) < 0.3):
                return t
        return None
    
    def find_segment_at(self, x_um, y_um):
        """Encuentra el segmento más cercano al punto"""
        min_dist = float('inf')
        closest_segment = None
        
        for segment in self.routing_segments:
            dist = self.point_to_line_distance(
                x_um, y_um,
                segment['x1'], segment['y1'],
                segment['x2'], segment['y2']
            )
            
            if dist < min_dist and dist < 0.2:  # 0.2 µm threshold
                min_dist = dist
                closest_segment = segment
        
        return closest_segment
    
    def point_to_line_distance(self, px, py, x1, y1, x2, y2):
        """Calcula la distancia de un punto a una línea"""
        dx = x2 - x1
        dy = y2 - y1
        
        if dx == 0 and dy == 0:
            return math.sqrt((px - x1)**2 + (py - y1)**2)
        
        t = max(0, min(1, ((px - x1) * dx + (py - y1) * dy) / (dx**2 + dy**2)))
        
        cx = x1 + t * dx
        cy = y1 + t * dy
        
        return math.sqrt((px - cx)**2 + (py - cy)**2)
    
    def on_mouse_down(self, event):
        """Start column routing"""
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        x_um, y_um = self.canvas_to_um(x, y)
        
        mode = self.mode_var.get()
        
        if mode == 'draw':
            t = self.find_transistor_at(x_um, y_um)
            if t and not t['is_dummy']:
                # Start column routing
                self.start_column_routing(t)
        elif mode == 'delete':
            self.delete_column_route_at(x_um, y_um)


        def show_status(self, message):
            """Mostrar mensaje de estado"""
            print(f"Status: {message}")
            if hasattr(self, 'report_text'):
                self.report_text.insert(tk.END, f"\n{message}")
                self.report_text.see(tk.END)

    def start_column_routing(self, start_transistor):
        """Start routing for entire column"""
        col = start_transistor['active_col']
        
        # Get all transistors in this column
        column_transistors = []
        for t_key, t_info in self.transistors.items():
            if t_info['active_col'] == col and not t_info['is_dummy']:
                column_transistors.append(t_info)
        
        # Sort by row (top to bottom in GUI)
        column_transistors.sort(key=lambda t: t['active_row'])
        
        if len(column_transistors) < 2:
            print(f"Column {col} has less than 2 transistors, skipping")
            return
        
        # Create vertical route connecting all gates
        self.create_column_route(column_transistors, col)
        
        # Auto-clone to other columns if col == 0
        if col == 0 and self.auto_clone_enabled:
            self.clone_column_pattern()

    def clone_column_pattern(self):
        """Clone column 0 pattern to all other columns"""
        # Get column 0 segments
        col0_segments = [s for s in self.routing_segments if s.get('column') == 0]
        
        if not col0_segments:
            return
        
        # Get column 0 transistors for reference
        col0_transistors = []
        for t_key, t_info in self.transistors.items():
            if t_info['active_col'] == 0 and not t_info['is_dummy']:
                col0_transistors.append(t_info)
        
        if not col0_transistors:
            return
        
        # Reference X position
        ref_x = col0_transistors[0]['x'] + self.transistor_width / 2
        
        # Clone to other columns
        for target_col in range(1, self.array_cols):
            # Get target column transistors
            target_transistors = []
            for t_key, t_info in self.transistors.items():
                if t_info['active_col'] == target_col and not t_info['is_dummy']:
                    target_transistors.append(t_info)
            
            if not target_transistors:
                continue
            
            # Calculate X offset
            target_x = target_transistors[0]['x'] + self.transistor_width / 2
            x_offset = target_x - ref_x
            
            # Clone segments with offset
            for seg in col0_segments:
                # Find corresponding transistor in target column
                orig_t = self.transistors[seg['transistor']]
                target_t = None
                
                for t in target_transistors:
                    if t['active_row'] == orig_t['active_row']:
                        target_t = t
                        break
                
                if target_t:
                    new_segment = {
                        'id': len(self.routing_segments),
                        'transistor': (target_t['row'], target_t['col']),
                        'x1': seg['x1'] + x_offset,
                        'y1': seg['y1'],
                        'x2': seg['x2'] + x_offset,
                        'y2': seg['y2'],
                        'type': seg['type'],
                        'column': target_col
                    }
                    self.routing_segments.append(new_segment)
                    target_t['routed'] = True
        
        self.draw_canvas()
        self.update_stats()
        print(f"Cloned column 0 pattern to {self.array_cols - 1} columns")

    def create_column_route(self, column_transistors, col):
        """Create vertical route connecting all gates in column"""
        
        # Clear existing routes for this column
        self.routing_segments = [s for s in self.routing_segments 
                                if not any(self.transistors[s['transistor']]['active_col'] == col 
                                        for _ in [None] if s['transistor'] in self.transistors)]
        
        # Calculate route parameters
        first_t = column_transistors[0]
        last_t = column_transistors[-1]
        
        # X position for vertical route (offset from gates)
        route_x_offset = -1.0 if col < self.array_cols // 2 else 1.0  # Left for left half, right for right half
        
        # Create segments connecting all gates
        segments_added = []
        
        for i, t in enumerate(column_transistors):
            gate_x = t['x'] + self.transistor_width / 2
            gate_y = t['y'] + self.transistor_height / 2
            
            # Horizontal segment from gate to vertical bus
            h_segment = {
                'id': len(self.routing_segments) + len(segments_added),
                'transistor': (t['row'], t['col']),
                'x1': gate_x,
                'y1': gate_y,
                'x2': gate_x + route_x_offset,
                'y2': gate_y,
                'type': 'horizontal',
                'column': col
            }
            segments_added.append(h_segment)
            
            # Vertical segment connecting to next transistor
            if i < len(column_transistors) - 1:
                next_t = column_transistors[i + 1]
                next_gate_y = next_t['y'] + self.transistor_height / 2
                
                v_segment = {
                    'id': len(self.routing_segments) + len(segments_added),
                    'transistor': (t['row'], t['col']),
                    'x1': gate_x + route_x_offset,
                    'y1': gate_y,
                    'x2': gate_x + route_x_offset,
                    'y2': next_gate_y,
                    'type': 'vertical',
                    'column': col
                }
                segments_added.append(v_segment)
        
        # Add exit segment (extend beyond last transistor)
        exit_length = 3.0  # µm
        exit_y = last_t['y'] + self.transistor_height / 2 + exit_length
        
        exit_segment = {
            'id': len(self.routing_segments) + len(segments_added),
            'transistor': (last_t['row'], last_t['col']),
            'x1': last_t['x'] + self.transistor_width / 2 + route_x_offset,
            'y1': last_t['y'] + self.transistor_height / 2,
            'x2': last_t['x'] + self.transistor_width / 2 + route_x_offset,
            'y2': exit_y,
            'type': 'vertical',
            'column': col
        }
        segments_added.append(exit_segment)
        
        # Add all segments
        self.routing_segments.extend(segments_added)
        
        # Mark transistors as routed
        for t in column_transistors:
            t['routed'] = True
        
        self.draw_canvas()
        self.update_stats()
        print(f"Created column route for column {col} with {len(column_transistors)} transistors")


    def create_manhattan_segments(self, start, end):
        """Crear segmentos Manhattan entre dos puntos"""
        x1, y1 = start
        x2, y2 = end
        segments = []
        
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        
        if dx > 0.01 and dy > 0.01:
            # Necesitamos 2 segmentos (L shape)
            # Horizontal primero, luego vertical
            segments.append({
                'x1': x1, 'y1': y1,
                'x2': x2, 'y2': y1,
                'type': 'horizontal'
            })
            segments.append({
                'x1': x2, 'y1': y1,
                'x2': x2, 'y2': y2,
                'type': 'vertical'
            })
        elif dx > 0.01:
            # Solo horizontal
            segments.append({
                'x1': x1, 'y1': y1,
                'x2': x2, 'y2': y2,
                'type': 'horizontal'
            })
        elif dy > 0.01:
            # Solo vertical
            segments.append({
                'x1': x1, 'y1': y1,
                'x2': x2, 'y2': y2,
                'type': 'vertical'
            })
        
        return segments
    
    def on_key_press(self, event):
        """STATE 3: ESC para terminar ruteo actual"""
        if event.keysym == 'Escape' and self.routing_active:
            # Terminar ruteo actual
            self.routing_active = False
            
            if self.selected_transistor:
                # Marcar como ruteado
                self.selected_transistor['routed'] = True
                
                # Restaurar color del gate
                gate_tag = f"gate_{self.selected_transistor['row']}_{self.selected_transistor['col']}"
                self.canvas.itemconfig(gate_tag, fill=self.colors['gate'], width=3)
                
                # AUTO-CLONAR si es columna 0
                if self.selected_transistor['active_col'] == 0 and self.auto_clone_enabled:
                    self.auto_clone_to_row()
                
                self.show_status(f"Ruteo completado - {len(self.current_route)} segmentos")
            
            # Limpiar estado
            self.selected_transistor = None
            self.current_route = []
            self.last_point = None
            self.update_stats()


    def auto_clone_to_row(self):
        """Clonar patrón de columna 0 a las demás columnas de la misma fila"""
        if not self.selected_transistor:
            return
        
        source_row = self.selected_transistor['active_row']
        source_key = (self.selected_transistor['row'], self.selected_transistor['col'])
        
        # Obtener segmentos del transistor fuente
        source_segments = [s for s in self.routing_segments if s['transistor'] == source_key]
        
        if not source_segments:
            return
        
        # Offset del gate fuente
        source_gate_x = self.selected_transistor['x'] + self.transistor_width / 2
        
        cloned_count = 0
        
        # Clonar a todas las columnas de la misma fila
        for t_key, t_info in self.transistors.items():
            if (t_info['active_row'] == source_row and 
                t_info['active_col'] > 0 and  # No columna 0
                not t_info['is_dummy'] and
                not t_info.get('routed', False)):
                
                # Calcular offset X
                target_gate_x = t_info['x'] + self.transistor_width / 2
                x_offset = target_gate_x - source_gate_x
                
                # Copiar segmentos con offset X solamente
                for seg in source_segments:
                    new_segment = {
                        'id': len(self.routing_segments),
                        'transistor': t_key,
                        'x1': seg['x1'] + x_offset,
                        'y1': seg['y1'],  # Mantener Y igual
                        'x2': seg['x2'] + x_offset,
                        'y2': seg['y2'],  # Mantener Y igual
                        'type': seg['type']
                    }
                    self.routing_segments.append(new_segment)
                
                t_info['routed'] = True
                cloned_count += 1
        
        if cloned_count > 0:
            self.draw_canvas()
            self.update_stats()
            self.show_status(f"Patrón clonado a {cloned_count} transistores")


    def draw_temp_segment(self, segment):
        """Draw a temporary segment during routing"""
        # Handle segment format from EnhancedManhattanRouter
        if 'start' in segment and 'end' in segment:
            # New format from router
            x1, y1 = self.um_to_canvas(*segment['start'])
            x2, y2 = self.um_to_canvas(*segment['end'])
        else:
            # Legacy format
            x1, y1 = self.um_to_canvas(segment.get('x1', 0), segment.get('y1', 0))
            x2, y2 = self.um_to_canvas(segment.get('x2', 0), segment.get('y2', 0))
        
        # Draw the temporary line
        line = self.canvas.create_line(
            x1, y1, x2, y2,
            fill=self.colors.get('routing', '#0066ff'),
            width=max(2, int(self.metal3_width * self.zoom_level)),
            capstyle='projecting',
            tags="temp_route"
        )
        return line

    def delete_segment_section(self, segment):
        """Delete a section of routing (between waypoints)"""
        t_key = segment['transistor']
        
        # Find all segments for this transistor
        t_segments = [s for s in self.routing_segments 
                    if s['transistor'] == t_key]
        
        if not t_segments:
            return
        
        # Find the clicked segment index
        clicked_idx = next((i for i, s in enumerate(t_segments) 
                        if s['id'] == segment['id']), None)
        
        if clicked_idx is not None:
            # Delete from this segment to the end
            segments_to_remove = t_segments[clicked_idx:]
            
            for seg in segments_to_remove:
                self.routing_segments.remove(seg)
            
            # Update routed status if no segments left
            if not any(s['transistor'] == t_key for s in self.routing_segments):
                self.transistors[t_key]['routed'] = False
            
            self.draw_canvas()
            self.update_stats()

    def on_double_click(self, event):
        """Finish route on double-click"""
        if self.routing_state == 'ROUTING':
            self.finish_current_route()

    def on_mouse_drag(self, event):
        """Handle mouse drag with preview"""
        if not self.drawing or not self.selected_transistor:
            return
        
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        x_um, y_um = self.canvas_to_um(x, y)
        
        if self.manhattan_router:
            # Get preview segments
            preview_segments = self.manhattan_router.get_preview_segments(x_um, y_um)
            
            # Clear old preview
            self.canvas.delete("preview")
            
            # Draw preview segments
            for seg in preview_segments:
                x1, y1 = self.um_to_canvas(*seg['start'])
                x2, y2 = self.um_to_canvas(*seg['end'])
                
                self.canvas.create_line(
                    x1, y1, x2, y2,
                    fill=self.colors.get('routing_preview', '#88ccff'),
                    width=max(2, int(self.metal3_width * self.zoom_level)),
                    capstyle='projecting',
                    tags="preview"
                )
            
            # Update coordinates display
            self.coord_label.config(text=f"X: {x_um:.2f} µm\nY: {y_um:.2f} µm")

    def on_mouse_up(self, event):
        """Complete route with proper segment handling"""
        if not self.drawing or not self.selected_transistor:
            return
        
        self.drawing = False
        self.canvas.delete("preview")
        
        if self.manhattan_router:
            x = self.canvas.canvasx(event.x)
            y = self.canvas.canvasy(event.y)
            x_um, y_um = self.canvas_to_um(x, y)
            
            # Add final point
            self.manhattan_router.add_point(x_um, y_um)
            
            # Get all segments
            segments = self.manhattan_router.finish_route()
            
            if segments:
                # Store segments
                t_key = (self.selected_transistor['row'], self.selected_transistor['col'])
                
                for seg in segments:
                    segment_data = {
                        'id': len(self.routing_segments),
                        'transistor': t_key,
                        'x1': seg['start'][0],
                        'y1': seg['start'][1],
                        'x2': seg['end'][0],
                        'y2': seg['end'][1],
                        'type': seg['type']
                    }
                    
                    self.routing_segments.append(segment_data)
                    self.draw_segment(segment_data)
                
                self.selected_transistor['routed'] = True
                
                # Auto-clone if column 0 (NO MIRROR)
                active_col = self.selected_transistor['active_col']
                if active_col == 0 and self.auto_clone_enabled:
                    self.clone_pattern_to_row_no_mirror(
                        self.selected_transistor['row'],
                        self.selected_transistor['col']
                    )
            
            # Cleanup
            self.manhattan_router = None
        
        # Restore gate color
        if self.selected_transistor:
            gate_tag = f"gate_{self.selected_transistor['row']}_{self.selected_transistor['col']}"
            self.canvas.itemconfig(gate_tag, fill=self.colors['gate'])
        
        self.selected_transistor = None
        self.update_stats()

    def create_drain_source_routes(self):
        """Create row-wise drain and source connections"""
        print("\nCreating drain and source routes...")
        
        # Clear existing drain/source routes
        self.routing_segments = [s for s in self.routing_segments 
                                if s.get('route_type') not in ['drain', 'source']]
        
        # Group transistors by row
        rows = {}
        for t_key, t_info in self.transistors.items():
            if not t_info['is_dummy']:
                row = t_info['active_row']
                if row not in rows:
                    rows[row] = []
                rows[row].append(t_info)
        
        # Process each row
        for row in sorted(rows.keys()):
            row_transistors = rows[row]
            
            # Sort by column (left to right)
            row_transistors.sort(key=lambda t: t['active_col'])
            
            if len(row_transistors) < 1:
                continue
            
            # Create drain route for this row
            self.create_row_drain_route(row_transistors, row)
            
            # Create source route for this row
            self.create_row_source_route(row_transistors, row)
        
        self.draw_canvas()
        self.update_stats()
        print(f"Created drain/source routes for {len(rows)} rows")

    def create_row_drain_route(self, row_transistors, row):
        """Create horizontal route connecting all drains in row"""
        
        segments_added = []
        
        # Drain is on the left side of transistor (at 20% of width)
        for i, t in enumerate(row_transistors):
            drain_x = t['x'] + self.transistor_width * 0.2
            drain_y = t['y'] + self.transistor_height / 2
            
            # Vertical segment extending drain up
            drain_extension = 0.5  # µm
            v_segment = {
                'id': len(self.routing_segments) + len(segments_added),
                'transistor': (t['row'], t['col']),
                'x1': drain_x,
                'y1': drain_y,
                'x2': drain_x,
                'y2': drain_y - drain_extension,  # Extend upward
                'type': 'vertical',
                'route_type': 'drain',
                'row': row,
                'metal': 'M1'
            }
            segments_added.append(v_segment)
            
            # Horizontal segment connecting to next transistor's drain
            if i < len(row_transistors) - 1:
                next_t = row_transistors[i + 1]
                next_drain_x = next_t['x'] + self.transistor_width * 0.2
                
                h_segment = {
                    'id': len(self.routing_segments) + len(segments_added),
                    'transistor': (t['row'], t['col']),
                    'x1': drain_x,
                    'y1': drain_y - drain_extension,
                    'x2': next_drain_x,
                    'y2': drain_y - drain_extension,
                    'type': 'horizontal',
                    'route_type': 'drain',
                    'row': row,
                    'metal': 'M1'
                }
                segments_added.append(h_segment)
        
        # Add via location marker (M4 to M1) at first drain
        if row_transistors:
            first_t = row_transistors[0]
            via_x = first_t['x'] + self.transistor_width * 0.2
            via_y = first_t['y'] + self.transistor_height / 2 - 0.5
            
            via_marker = {
                'id': len(self.routing_segments) + len(segments_added),
                'transistor': (first_t['row'], first_t['col']),
                'x1': via_x,
                'y1': via_y,
                'x2': via_x,
                'y2': via_y,
                'type': 'via',
                'route_type': 'drain_via',
                'row': row,
                'metal': 'M4_to_M1'
            }
            segments_added.append(via_marker)
        
        self.routing_segments.extend(segments_added)

    def create_row_source_route(self, row_transistors, row):
        """Create horizontal route connecting all sources in row"""
        
        segments_added = []
        
        # Source is on the right side of transistor (at 80% of width)
        for i, t in enumerate(row_transistors):
            source_x = t['x'] + self.transistor_width * 0.8
            source_y = t['y'] + self.transistor_height / 2
            
            # Vertical segment extending source down
            source_extension = 0.5  # µm
            v_segment = {
                'id': len(self.routing_segments) + len(segments_added),
                'transistor': (t['row'], t['col']),
                'x1': source_x,
                'y1': source_y,
                'x2': source_x,
                'y2': source_y + source_extension,  # Extend downward
                'type': 'vertical',
                'route_type': 'source',
                'row': row,
                'metal': 'M1'
            }
            segments_added.append(v_segment)
            
            # Horizontal segment connecting to next transistor's source
            if i < len(row_transistors) - 1:
                next_t = row_transistors[i + 1]
                next_source_x = next_t['x'] + self.transistor_width * 0.8
                
                h_segment = {
                    'id': len(self.routing_segments) + len(segments_added),
                    'transistor': (t['row'], t['col']),
                    'x1': source_x,
                    'y1': source_y + source_extension,
                    'x2': next_source_x,
                    'y2': source_y + source_extension,
                    'type': 'horizontal',
                    'route_type': 'source',
                    'row': row,
                    'metal': 'M1'
                }
                segments_added.append(h_segment)
        
        # Add via location marker (M5 to M1) at last source
        if row_transistors:
            last_t = row_transistors[-1]
            via_x = last_t['x'] + self.transistor_width * 0.8
            via_y = last_t['y'] + self.transistor_height / 2 + 0.5
            
            via_marker = {
                'id': len(self.routing_segments) + len(segments_added),
                'transistor': (last_t['row'], last_t['col']),
                'x1': via_x,
                'y1': via_y,
                'x2': via_x,
                'y2': via_y,
                'type': 'via',
                'route_type': 'source_via',
                'row': row,
                'metal': 'M5_to_M1'
            }
            segments_added.append(via_marker)
        
        self.routing_segments.extend(segments_added)

    def on_mouse_click(self, event):
        """
        Alternative: Support multi-click routing for complex paths
        Left click: Add point
        Right click: Finish route
        """
        if event.num == 1:  # Left click
            x = self.canvas.canvasx(event.x)
            y = self.canvas.canvasy(event.y)
            x_um, y_um = self.canvas_to_um(x, y)
            
            if not self.drawing:
                # Start new route
                t = self.find_transistor_at(x_um, y_um)
                if t and not t['is_dummy']:
                    self.selected_transistor = t
                    self.drawing = True
                    
                    self.manhattan_router = EnhancedManhattanRouter()
                    gate_x = t['x'] + self.transistor_width / 2
                    gate_y = t['y'] + self.transistor_height / 2
                    self.manhattan_router.start_route(gate_x, gate_y)
                    
                    gate_tag = f"gate_{t['row']}_{t['col']}"
                    self.canvas.itemconfig(gate_tag, fill=self.colors['gate_selected'])
            else:
                # Add intermediate point
                if self.manhattan_router:
                    segments_added = self.manhattan_router.add_point(x_um, y_um)
                    
                    # Draw the confirmed segments
                    for seg in segments_added:
                        x1, y1 = self.um_to_canvas(*seg['start'])
                        x2, y2 = self.um_to_canvas(*seg['end'])
                        
                        self.canvas.create_line(
                            x1, y1, x2, y2,
                            fill=self.colors.get('routing', '#0066ff'),
                            width=max(2, int(self.metal3_width * self.zoom_level)),
                            capstyle='projecting',
                            tags=f"temp_route_{len(self.routing_segments)}"
                        )
        
        elif event.num == 3:  # Right click
            if self.drawing:
                # Finish current route
                self.finish_current_route()

    def finish_current_route(self):
        """Finish the current route and store it"""
        if not self.drawing or not self.manhattan_router:
            return
        
        segments = self.manhattan_router.finish_route()
        
        if segments:
            t_key = (self.selected_transistor['row'], self.selected_transistor['col'])
            
            # Clear temporary drawings
            self.canvas.delete("temp_route_*")
            
            # Store final segments
            for seg in segments:
                segment_data = {
                    'id': len(self.routing_segments),
                    'transistor': t_key,
                    'x1': seg['start'][0],
                    'y1': seg['start'][1],
                    'x2': seg['end'][0],
                    'y2': seg['end'][1],
                    'type': seg['type']
                }
                self.routing_segments.append(segment_data)
                self.draw_segment(segment_data)
            
            self.selected_transistor['routed'] = True
        
        # Cleanup
        self.drawing = False
        self.manhattan_router = None
        self.canvas.delete("preview")
        
        if self.selected_transistor:
            gate_tag = f"gate_{self.selected_transistor['row']}_{self.selected_transistor['col']}"
            self.canvas.itemconfig(gate_tag, fill=self.colors['gate'])
            self.selected_transistor = None
        
        self.update_stats()


    def on_right_click(self, event):
        """Manejo del click derecho - eliminar última ruta"""
        # Si estamos dibujando, cancelar
        if self.drawing:
            self.drawing = False
            self.canvas.delete("preview")
                
            if self.manhattan_router:
                self.manhattan_router = None
                
            if self.selected_transistor:
                gate_tag = f"gate_{self.selected_transistor['row']}_{self.selected_transistor['col']}"
                self.canvas.itemconfig(gate_tag, fill=self.colors['gate'])
                self.selected_transistor = None
                
            return
            
        # Si no estamos dibujando, eliminar última ruta
        if self.routing_segments:
            last_transistor = None
            for segment in reversed(self.routing_segments):
                if segment['transistor'] != last_transistor:
                    last_transistor = segment['transistor']
                    break
                
                if last_transistor:
                    self.routing_segments = [s for s in self.routing_segments 
                                        if s['transistor'] != last_transistor]
                    
                    row, col = last_transistor
                    if last_transistor in self.transistors:
                        self.transistors[last_transistor]['routed'] = False
                    
                self.draw_canvas()
                self.update_stats()
    
    def on_right_click(self, event):
        """Click derecho para ELIMINAR segmento"""
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        x_um, y_um = self.canvas_to_um(x, y)
        
        # Buscar segmento más cercano
        segment = self.find_segment_at(x_um, y_um)
        
        if segment:
            # Eliminar este segmento y todos los posteriores del mismo transistor
            t_key = segment['transistor']
            
            # Encontrar índice del segmento
            seg_index = self.routing_segments.index(segment)
            
            # Eliminar este y los siguientes del mismo transistor
            segments_to_remove = []
            for i in range(seg_index, len(self.routing_segments)):
                if self.routing_segments[i]['transistor'] == t_key:
                    segments_to_remove.append(self.routing_segments[i])
            
            for seg in segments_to_remove:
                self.routing_segments.remove(seg)
            
            # Actualizar estado del transistor
            if not any(s['transistor'] == t_key for s in self.routing_segments):
                if t_key in self.transistors:
                    self.transistors[t_key]['routed'] = False
            
            self.draw_canvas()
            self.update_stats()
            self.show_status(f"Eliminados {len(segments_to_remove)} segmentos")

    def on_right_click(self, event):
        """Manejo del click derecho - eliminar última ruta o mostrar menú"""
        # Si estamos dibujando, cancelar
        if self.drawing:
            self.drawing = False
            self.canvas.delete("preview")
            
            if self.manhattan_router:
                self.manhattan_router = None
            
            if self.selected_transistor:
                gate_tag = f"gate_{self.selected_transistor['row']}_{self.selected_transistor['col']}"
                self.canvas.itemconfig(gate_tag, fill=self.colors['gate'])
                self.selected_transistor = None
            
            return
        
        # Verificar si hay un transistor bajo el cursor
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        x_um, y_um = self.canvas_to_um(x, y)
        
        t = self.find_transistor_at(x_um, y_um)
        if t and t['routed'] and not t['is_dummy']:
            # Mostrar menú contextual
            self.show_context_menu(event, t)
        else:
            # Comportamiento original - eliminar última ruta
            if self.routing_segments:
                last_transistor = None
                for segment in reversed(self.routing_segments):
                    if segment['transistor'] != last_transistor:
                        last_transistor = segment['transistor']
                        break
                
                if last_transistor:
                    self.routing_segments = [s for s in self.routing_segments 
                                        if s['transistor'] != last_transistor]
                    
                    row, col = last_transistor
                    if last_transistor in self.transistors:
                        self.transistors[last_transistor]['routed'] = False
                    
                    self.draw_canvas()
                    self.update_stats()

    def show_context_menu(self, event, transistor):
        """Show context menu for transistor operations"""
        menu = tk.Menu(self.root, tearoff=0)
        
        # Use actual row/col for the menu operation
        row = transistor['row']
        col = transistor['col']
        active_row = transistor['active_row']
        active_col = transistor['active_col']
        
        menu.add_command(
            label=f"Clone pattern from [{active_row},{active_col}] to rest of row", 
            command=lambda: self.clone_pattern_to_row(row, col)
        )
        menu.add_separator()
        menu.add_command(
            label="Delete this route", 
            command=lambda: self.delete_transistor_route(transistor)
        )
        
        menu.post(event.x_root, event.y_root)

    def on_mouse_move(self, event):
        """Mostrar preview del segmento mientras mueves el mouse"""
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        x_um, y_um = self.canvas_to_um(x, y)
        
        # Actualizar coordenadas
        self.coord_label.config(text=f"X: {x_um:.2f} µm\nY: {y_um:.2f} µm")
        
        # Mostrar preview si estamos ruteando
        if self.routing_active and self.last_point:
            self.canvas.delete("preview")
            
            # Snap a grid
            target_x = round(x_um / 0.05) * 0.05
            target_y = round(y_um / 0.05) * 0.05
            
            # Preview de segmentos Manhattan
            segments = self.create_manhattan_segments(self.last_point, (target_x, target_y))
            
            for seg in segments:
                x1, y1 = self.um_to_canvas(seg['x1'], seg['y1'])
                x2, y2 = self.um_to_canvas(seg['x2'], seg['y2'])
                
                self.canvas.create_line(
                    x1, y1, x2, y2,
                    fill='#88ccff',
                    width=max(2, int(self.metal3_width * self.zoom_level)),
                    dash=(5, 5),
                    tags="preview"
                )
    
    def on_mouse_wheel(self, event):
        """Zoom con la rueda del mouse"""
        if event.delta > 0:
            self.zoom_in()
        else:
            self.zoom_out()
    
    def on_ctrl_mouse_wheel(self, event):
        """Pan horizontal con Ctrl+rueda"""
        self.canvas.xview_scroll(int(-event.delta/120), "units")
    
    def zoom_in(self):
        """Aumenta el zoom"""
        self.zoom_level *= 1.2
        self.zoom_level = min(self.zoom_level, 200)
        self.zoom_label.config(text=f"{self.zoom_level:.0f}x")
        self.draw_canvas()
    
    def zoom_out(self):
        """Reduce el zoom"""
        self.zoom_level /= 1.2
        self.zoom_level = max(self.zoom_level, 10)
        self.zoom_label.config(text=f"{self.zoom_level:.0f}x")
        self.draw_canvas()
    
    def zoom_fit(self):
        """Ajusta el zoom para ver todo el array"""
        if not self.transistors:
            return
        
        max_x = max(t['x'] for t in self.transistors.values()) + self.pitch_x
        max_y = max(t['y'] for t in self.transistors.values()) + self.pitch_y
        
        zoom_x = (self.canvas_width - 100) / max_x
        zoom_y = (self.canvas_height - 100) / max_y
        
        self.zoom_level = min(zoom_x, zoom_y)
        self.zoom_label.config(text=f"{self.zoom_level:.0f}x")
        self.draw_canvas()

    def delete_transistor_route(self, transistor):
        """Delete all routing segments for a specific transistor"""
        t_key = (transistor['row'], transistor['col'])
        self.routing_segments = [s for s in self.routing_segments 
                            if s['transistor'] != t_key]
        transistor['routed'] = False
        self.draw_canvas()
        self.update_stats()

    
    def update_array(self):
        """Update array when parameters change"""
        self.array_rows = self.rows_var.get()
        self.array_cols = self.cols_var.get()
        self.dummy_mode = self.dummy_mode_var.get()  # Changed from has_dummies
        
        self.routing_segments.clear()
        
        self.create_array()
        self.draw_canvas()
        self.update_stats()
        self.show_configuration_info()
    
    def delete_segment(self, segment):
        """Elimina un segmento específico"""
        self.routing_segments = [s for s in self.routing_segments 
                               if s['id'] != segment['id']]
        
        t_key = segment['transistor']
        has_segments = any(s['transistor'] == t_key for s in self.routing_segments)
        if not has_segments and t_key in self.transistors:
            self.transistors[t_key]['routed'] = False
        
        self.draw_canvas()
        self.update_stats()
    
    def clear_all_routes(self):
        """Elimina todas las rutas"""
        self.routing_segments.clear()
        
        for t in self.transistors.values():
            t['routed'] = False
        
        self.manhattan_router = None  # Limpiar router si existe
        
        self.draw_canvas()
        self.update_stats()
    
    def update_stats(self):
        """Actualiza las estadísticas"""
        total_segments = len(self.routing_segments)
        
        routed = sum(1 for t in self.transistors.values() 
                    if t['routed'] and not t['is_dummy'])
        total = sum(1 for t in self.transistors.values() 
                   if not t['is_dummy'])
        
        self.stats_label.config(text=f"Segments: {total_segments}\nRouted: {routed}/{total}")
    
    def save_pattern(self):
        """
        Guarda con coordenadas activas directamente
        """
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")]
        )
        
        if filename:
            pattern_dict = self.generate_pattern_dict()
            
            # Convertir a JSON con claves string
            json_pattern = {}
            for key, data in pattern_dict.items():
                if isinstance(key, tuple):
                    row, col = key
                    # Usar coordenadas ACTIVAS como clave
                    key_str = f"{row},{col}"
                else:
                    key_str = str(key)
                json_pattern[key_str] = data
            
            print("\n=== GUARDANDO PATRÓN (CORREGIDO) ===")
            print("Claves almacenadas (primeras 4):")
            for i, key in enumerate(list(json_pattern.keys())[:4]):
                data = json_pattern[key]
                print(f"  '{key}' -> GUI[{data.get('gui_row', '?')},{data.get('gui_col', '?')}]")
            print("=" * 50)
            
            pattern_data = {
                'metadata': {
                    'array_rows': self.array_rows,
                    'array_cols': self.array_cols,
                    'dummy_mode': self.dummy_mode_var.get(),
                    'device_type': getattr(self, 'device_type_var', tk.StringVar(value='nmos')).get(),
                    'transistor_W': self.transistor_W,
                    'transistor_L': self.transistor_L,
                    'guardring_spacing': self.guardring_spacing,
                    'pitch_x': self.pitch_x,
                    'pitch_y': self.pitch_y,
                    'timestamp': datetime.now().isoformat(),
                    'coordinate_system': 'active_no_flip',  # Marcador importante
                    'version': '3.0_fixed'
                },
                'pattern_data': json_pattern
            }
            
            # Guardar ambos archivos
            with open(filename, 'w') as f:
                json.dump(pattern_data, f, indent=2)
            
            with open('temp_pattern.json', 'w') as f:
                json.dump(pattern_data, f, indent=2)
            

    def load_pattern(self):
        """Load pattern and apply dimension configuration"""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            with open(filename, 'r') as f:
                pattern_data = json.load(f)
            
            meta = pattern_data['metadata']
            
            # Apply dimensions from file
            if 'transistor_W' in meta:
                self.transistor_W = meta['transistor_W']
            if 'transistor_L' in meta:
                self.transistor_L = meta['transistor_L']
            if 'guardring_spacing' in meta:
                self.guardring_spacing = meta.get('guardring_spacing', 2.0)
            
            # Handle dummy mode
            if 'dummy_mode' in meta:
                self.dummy_mode_var.set(meta['dummy_mode'])
            elif 'has_dummies' in meta:
                # Backward compatibility
                self.dummy_mode_var.set('sides' if meta['has_dummies'] else 'none')
            
            # Handle device type
            if 'device_type' in meta and hasattr(self, 'device_type_var'):
                self.device_type_var.set(meta['device_type'])
            
            # Update array size if different
            if (meta['array_rows'] != self.array_rows or
                meta['array_cols'] != self.array_cols):
                
                if messagebox.askyesno("Load Pattern", 
                                    "Pattern was created for a different array size.\n"
                                    "Do you want to adjust the array to match?"):
                    self.rows_var.set(meta['array_rows'])
                    self.cols_var.set(meta['array_cols'])
            
            # Update array with new settings
            self.update_array()
            
            # Load routing segments
            self.routing_segments.clear()
            
            for seg_data in pattern_data['segments']:
                segment = {
                    'id': len(self.routing_segments),
                    'transistor': tuple(seg_data['transistor']),
                    'x1': seg_data['x1'],
                    'y1': seg_data['y1'],
                    'x2': seg_data['x2'],
                    'y2': seg_data['y2'],
                    'type': seg_data['type']
                }
                self.routing_segments.append(segment)
                
                t_key = tuple(seg_data['transistor'])
                if t_key in self.transistors:
                    self.transistors[t_key]['routed'] = True
            
            self.draw_canvas()
            self.update_stats()
            self.show_configuration_info()
            
            messagebox.showinfo("Load Pattern", 
                          f"Pattern loaded from {filename}\n"
                          f"Configuration: W={self.transistor_W}µm, L={self.transistor_L}µm")
    
    def generate_report(self):
        """Genera el reporte del patrón con mapeo de coordenadas"""
        report = "GATE ROUTING PATTERN - WITH COORDINATE MAPPING\n"
        report += "=" * 50 + "\n\n"
        
        report += f"Array: {self.array_rows}x{self.array_cols}"
        if self.has_dummies:
            report += " (with side dummies)"
        report += "\n"
        report += f"Pitch: {self.pitch_x} x {self.pitch_y} µm\n"
        report += f"Technology: SG13G2\n\n"
        
        # Explicación del mapeo
        report += "COORDINATE MAPPING:\n"
        report += "-" * 30 + "\n"
        report += "GUI row numbering: 0=top, 3=bottom\n"
        report += "KLayout row numbering: 0=bottom, 3=top\n"
        report += "Mapping: KL_row = (N-1) - GUI_row\n"
        report += "Direction: preserved from GUI design\n\n"
        
        transistor_routes = {}
        for segment in self.routing_segments:
            t_key = segment['transistor']
            if t_key not in transistor_routes:
                transistor_routes[t_key] = []
            transistor_routes[t_key].append(segment)
        
        report += "PATTERN DATA:\n"
        report += "GUI Pos | KL Pos  | Start(µm)    | H-Len | V-Ext | Direction\n"
        report += "-" * 65 + "\n"
        
        patterns = {}
        
        for t_key in sorted(transistor_routes.keys()):
            row, col = t_key
            segments = transistor_routes[t_key]
            
            if not segments:
                continue
            
            t = self.transistors[t_key]
            if t['is_dummy']:
                continue
            
            gate_x = t['x'] + self.transistor_width / 2
            gate_y = t['y'] + self.transistor_height / 2
            
            start_x = segments[0]['x1']
            start_y = segments[0]['y1']
            
            offset_x = start_x - gate_x
            offset_y = start_y - gate_y
            
            h_length = 0
            v_length = 0
            
            for seg in segments:
                if seg['type'] == 'horizontal':
                    h_length += abs(seg['x2'] - seg['x1'])
                else:
                    v_length += abs(seg['y2'] - seg['y1'])
            
            last_y = segments[-1]['y2']
            goes_up = last_y < gate_y
            
            active_row = t['active_row']
            active_col = t['active_col']
            
            # Mapeo de coordenadas para KLayout
            klayout_row = (self.array_rows - 1) - active_row
            
            patterns[(klayout_row, active_col)] = {
                'offset_y': offset_y,
                'h_length': h_length,
                'v_length': v_length,
                'goes_up': goes_up
            }
            
            direction = "UP" if goes_up else "DOWN"
            
            report += f"[{active_row},{active_col}] | "
            report += f"[{klayout_row},{active_col}] | "
            report += f"({offset_x:4.2f},{offset_y:4.2f}) | "
            report += f"{h_length:5.2f} | {v_length:5.2f} | "
            report += f"{direction}\n"
        
        report += "\n" + "=" * 50 + "\n"
        report += "PYTHON PATTERN (KLayout coordinates):\n\n"
        report += "pattern_data = {\n"
        
        for (row, col), p in sorted(patterns.items()):
            report += f"    ({row}, {col}): {{\n"
            report += f"        'offset_y': {p['offset_y']:.2f},\n"
            report += f"        'h_length': {p['h_length']:.2f},\n"
            report += f"        'v_length': {p['v_length']:.2f},\n"
            report += f"        'goes_up': {p['goes_up']}\n"
            report += f"    }},\n"
        
        report += "}\n"
        
        self.report_text.delete(1.0, tk.END)
        self.report_text.insert(1.0, report)

    def generate_pattern_dict(self):
        """Generate pattern for column-based routing"""
        pattern_dict = {}
        
        # Group segments by column
        columns_data = {}
        for segment in self.routing_segments:
            col = segment.get('column', -1)
            if col >= 0:
                if col not in columns_data:
                    columns_data[col] = []
                columns_data[col].append(segment)
        
        # Store only column 0 pattern (others are clones)
        if 0 in columns_data:
            col0_segments = columns_data[0]
            
            # Get all unique transistors in column 0
            col0_transistors = set()
            for seg in col0_segments:
                t = self.transistors[seg['transistor']]
                if not t['is_dummy']:
                    col0_transistors.add((t['active_row'], t['active_col']))
            
            # Sort by row
            col0_transistors = sorted(list(col0_transistors), key=lambda x: x[0])
            
            # Create column pattern
            pattern_dict['column_pattern'] = {
                'transistors': col0_transistors,
                'segments': []
            }
            
            # Store segments relative to first transistor
            if col0_transistors:
                first_t_key = None
                for t_key, t_info in self.transistors.items():
                    if (t_info['active_row'], t_info['active_col']) == col0_transistors[0]:
                        first_t_key = t_key
                        break
                
                if first_t_key:
                    first_t = self.transistors[first_t_key]
                    ref_x = first_t['x'] + self.transistor_width / 2
                    ref_y = first_t['y'] + self.transistor_height / 2
                    
                    for seg in col0_segments:
                        pattern_dict['column_pattern']['segments'].append({
                            'x1': seg['x1'] - ref_x,
                            'y1': seg['y1'] - ref_y,
                            'x2': seg['x2'] - ref_x,
                            'y2': seg['y2'] - ref_y,
                            'type': seg['type']
                        })
        
        return pattern_dict

    def calculate_total_length(self, segments):
        """Calculate total route length"""
        total = 0
        for seg in segments:
            if seg['type'] == 'horizontal':
                total += abs(seg['x2'] - seg['x1'])
            else:
                total += abs(seg['y2'] - seg['y1'])
        return round(total, 2)
    
    def detect_route_direction(self, segments):
        """Detect exit direction for a specific route"""
        if not segments:
            return 'unknown'
        
        last_seg = segments[-1]
        
        # Check last segment direction
        if last_seg['type'] == 'vertical':
            return 'up' if last_seg['y2'] < last_seg['y1'] else 'down'
        else:
            return 'right' if last_seg['x2'] > last_seg['x1'] else 'left'

    def copy_pattern_dict(self):
        """Copia el diccionario pattern_data al portapapeles"""
        # Generar el patrón
        pattern_dict = self.generate_pattern_dict()
        
        # Formatear como código Python
        code = "# Pattern data for KLayout\n"
        code += "# GUI row 0 (top) → KLayout row 3 (top in KL coordinates)\n"
        code += "# Direction (goes_up) is preserved from GUI design\n\n"
        code += "pattern_data = {\n"
        
        for key in sorted(pattern_dict.keys()):
            p = pattern_dict[key]
            code += f"    {key}: {{\n"
            code += f"        'offset_y': {p['offset_y']:.2f},\n"
            code += f"        'h_length': {p['h_length']:.2f},\n"
            code += f"        'v_length': {p['v_length']:.2f},\n"
            code += f"        'goes_up': {p['goes_up']}\n"
            code += f"    }},\n"
        
        code += "}\n"
        
        # Copiar al portapapeles
        self.root.clipboard_clear()
        self.root.clipboard_append(code)
        
        # Mostrar confirmación
        messagebox.showinfo("Pattern Copied", 
                        "Pattern dictionary copied to clipboard!\n\n"
                        "Coordinate mapping applied:\n"
                        "• GUI Row 0 → KLayout Row 3\n"
                        "• GUI Row 3 → KLayout Row 0\n"
                        "• Directions preserved as designed")
        
        # También mostrar en el área de reporte
        report = "COPIED TO CLIPBOARD:\n\n"
        report += code
        
        self.report_text.delete(1.0, tk.END)
        self.report_text.insert(1.0, report)

    def toggle_auto_clone(self):
        """Toggle auto-cloning feature"""
        self.auto_clone_enabled = self.auto_clone_var.get()
        if self.auto_clone_enabled:
            self.report_text.insert(tk.END, "\n✓ Auto-cloning ENABLED - Patterns in column 0 will be cloned to other columns\n")
        else:
            self.report_text.insert(tk.END, "\n✗ Auto-cloning DISABLED\n")


    def clone_pattern_to_row_no_mirror(self, source_row, source_col):
        """Clone pattern WITHOUT mirror effect - exact copy"""
        if not self.auto_clone_enabled:
            return
        
        source_segments = [s for s in self.routing_segments 
                        if s['transistor'] == (source_row, source_col)]
        
        if not source_segments:
            return
        
        source_t = self.transistors[(source_row, source_col)]
        source_active_row = source_t['active_row']
        
        # Clone to all other columns in same row
        for t_key, t_info in self.transistors.items():
            if (t_info['active_row'] == source_active_row and 
                t_key != (source_row, source_col) and 
                not t_info['is_dummy'] and 
                not t_info.get('routed', False)):
                
                # Calculate X offset only (no mirror)
                source_gate_x = source_t['x'] + self.transistor_width / 2
                target_gate_x = t_info['x'] + self.transistor_width / 2
                x_offset = target_gate_x - source_gate_x
                
                # Copy segments with X offset only
                for seg in source_segments:
                    new_segment = {
                        'id': len(self.routing_segments),
                        'transistor': t_key,
                        'x1': seg['x1'] + x_offset,
                        'y1': seg['y1'],  # Keep same Y
                        'x2': seg['x2'] + x_offset,
                        'y2': seg['y2'],  # Keep same Y
                        'type': seg['type']
                    }
                    self.routing_segments.append(new_segment)
                
                t_info['routed'] = True
        
        self.draw_canvas()
        self.update_stats()

    def analyze_route_pattern(self, segments):
        """
        Analyze a route pattern to extract key characteristics
        FIXED: Correct direction determination for row 0
        """
        if not segments:
            return None
        
        # Find start and end points
        all_points = []
        for seg in segments:
            all_points.append((seg['x1'], seg['y1']))
            all_points.append((seg['x2'], seg['y2']))
        
        # Get transistor gate position
        t = self.transistors[segments[0]['transistor']]
        gate_x = t['x'] + self.transistor_width / 2
        gate_y = t['y'] + self.transistor_height / 2
        
        # Find the start point (closest to gate)
        min_dist = float('inf')
        start_point = None
        for p in all_points:
            dist = math.sqrt((p[0] - gate_x)**2 + (p[1] - gate_y)**2)
            if dist < min_dist:
                min_dist = dist
                start_point = p
        
        # Calculate offset from gate
        offset_y = start_point[1] - gate_y
        
        # Calculate total lengths
        h_length = 0
        v_length = 0
        
        for seg in segments:
            if seg['type'] == 'horizontal':
                h_length += abs(seg['x2'] - seg['x1'])
            else:
                v_length += abs(seg['y2'] - seg['y1'])
        
        # Find the final endpoint of the route
        # This is crucial for determining direction
        final_point = None
        max_dist = 0
        for p in all_points:
            dist = math.sqrt((p[0] - gate_x)**2 + (p[1] - gate_y)**2)
            if dist > max_dist:
                max_dist = dist
                final_point = p
        
        if final_point is None:
            final_point = start_point
        
        # FIXED: Determine direction based on active row position
        # For GUI canvas coordinates: Y increases downward
        active_row = t['active_row']
        
        # Determine if route goes up or down in the PATTERN SPACE
        # This will be interpreted correctly by both GUI and KLayout
        if active_row < self.array_rows / 2:
            # Upper half (rows 0, 1 for 4x4) - routes should exit upward
            # In canvas coordinates, "up" means smaller Y values
            goes_up = final_point[1] < gate_y
        else:
            # Lower half (rows 2, 3 for 4x4) - routes should exit downward  
            # In canvas coordinates, "down" means larger Y values
            goes_up = final_point[1] < gate_y
        
        # Special handling for row boundaries
        # If the route clearly goes in one direction, respect that
        y_diff = final_point[1] - gate_y
        if abs(y_diff) > 0.5:  # Significant vertical movement
            # Trust the actual route direction
            goes_up = y_diff < 0  # Negative diff = going up in canvas
        
        print(f"  Pattern analysis for T[{active_row},{t['active_col']}]:")
        print(f"    Gate Y: {gate_y:.2f}, Final Y: {final_point[1]:.2f}")
        print(f"    Y difference: {y_diff:.2f}")
        print(f"    Direction: {'UP' if goes_up else 'DOWN'}")
        
        return {
            'offset_y': offset_y,
            'h_length': h_length,
            'v_length': v_length,
            'goes_up': goes_up,
            'segments': segments
        }
    
    def create_cloned_route(self, transistor_key, pattern_info, active_col):
        """
        Create a cloned route for a transistor based on pattern info
        FIXED: Correct vertical direction for all rows including row 0
        """
        t = self.transistors[transistor_key]
        gate_x = t['x'] + self.transistor_width / 2
        gate_y = t['y'] + self.transistor_height / 2
        
        # Start point with same offset
        start_x = gate_x
        start_y = gate_y + pattern_info['offset_y']
        
        # Determine horizontal direction based on active column
        if active_col >= self.array_cols // 2:
            # Right half - go right
            h_direction = 1
        else:
            # Left half - go left  
            h_direction = -1
        
        # Create segments
        segments_to_add = []
        current_x = start_x
        current_y = start_y
        
        # Horizontal segment (if any)
        if pattern_info['h_length'] > 0:
            h_end_x = start_x + pattern_info['h_length'] * h_direction
            
            # Store with correct coordinates for the segment
            segment_data = {
                'id': len(self.routing_segments) + len(segments_to_add),
                'transistor': transistor_key,
                'x1': start_x, 
                'y1': start_y,
                'x2': h_end_x, 
                'y2': start_y,
                'type': 'horizontal'
            }
            segments_to_add.append(segment_data)
            current_x = h_end_x
        
        # Vertical segment (if any)
        if pattern_info['v_length'] > 0:
            # FIXED: Correct vertical direction based on pattern
            # In GUI canvas: Y increases downward
            # goes_up=True means the route goes upward visually (decreasing Y)
            if pattern_info['goes_up']:
                v_end_y = current_y - pattern_info['v_length']  # Decrease Y to go up
            else:
                v_end_y = current_y + pattern_info['v_length']  # Increase Y to go down
            
            segment_data = {
                'id': len(self.routing_segments) + len(segments_to_add),
                'transistor': transistor_key,
                'x1': current_x, 
                'y1': current_y,
                'x2': current_x, 
                'y2': v_end_y,
                'type': 'vertical'
            }
            segments_to_add.append(segment_data)
        
        # Add all segments
        for seg in segments_to_add:
            self.routing_segments.append(seg)
            self.draw_segment(seg)
        
        # Mark transistor as routed
        t['routed'] = True
        
        # Debug info
        active_row = t['active_row']
        direction = "UP" if pattern_info['goes_up'] else "DOWN"
        print(f"    Created route for T[{active_row},{active_col}]: dir={direction}, v_len={pattern_info['v_length']:.2f}")

    def align_exit_points(self):
        """
        Align all exit points with uniform pitch
        Call this after all routing is complete
        """
        exit_direction = self.exit_align_var.get()
        
        if exit_direction == 'auto':
            # Determine from majority of routes
            exit_direction = self.detect_exit_direction()
        
        # Group routes by row
        routes_by_row = {}
        for seg in self.routing_segments:
            t_key = seg['transistor']
            if t_key not in routes_by_row:
                routes_by_row[t_key] = []
            routes_by_row[t_key].append(seg)
        
        # Calculate aligned positions
        pitch = self.exit_pitch
        active_routes = []
        
        for t_key, segments in routes_by_row.items():
            t = self.transistors[t_key]
            if not t['is_dummy']:
                # Find exit point (last segment endpoint)
                last_seg = segments[-1]
                exit_x = last_seg['x2']
                exit_y = last_seg['y2']
                
                active_routes.append({
                    'transistor': t_key,
                    'active_row': t['active_row'],
                    'active_col': t['active_col'],
                    'exit_x': exit_x,
                    'exit_y': exit_y,
                    'segments': segments
                })
        
        # Sort by position and assign aligned coordinates
        if exit_direction in ['top', 'bottom']:
            # Sort by column, align in X with pitch
            active_routes.sort(key=lambda r: (r['active_row'], r['active_col']))
            
            # Find common Y coordinate
            if exit_direction == 'top':
                common_y = min(r['exit_y'] for r in active_routes)
            else:
                common_y = max(r['exit_y'] for r in active_routes)
            
            # Assign X positions with pitch
            start_x = min(r['exit_x'] for r in active_routes)
            
            for i, route in enumerate(active_routes):
                new_x = start_x + i * pitch
                self.adjust_route_exit(route['segments'], new_x, common_y)
        
        elif exit_direction in ['left', 'right']:
            # Sort by row, align in Y with pitch
            active_routes.sort(key=lambda r: (r['active_col'], r['active_row']))
            
            # Find common X coordinate
            if exit_direction == 'left':
                common_x = min(r['exit_x'] for r in active_routes)
            else:
                common_x = max(r['exit_x'] for r in active_routes)
            
            # Assign Y positions with pitch
            start_y = min(r['exit_y'] for r in active_routes)
            
            for i, route in enumerate(active_routes):
                new_y = start_y + i * pitch
                self.adjust_route_exit(route['segments'], common_x, new_y)
        
        print(f"✓ Aligned {len(active_routes)} exit points - Direction: {exit_direction}, Pitch: {pitch}µm")
        self.draw_canvas()

    def adjust_route_exit(self, segments, new_x, new_y):
        """Adjust the exit point of a route"""
        if not segments:
            return
        
        # Modify last segment to reach new exit point
        last_seg = segments[-1]
        
        # Determine if we need additional segment
        if last_seg['type'] == 'horizontal' and abs(new_y - last_seg['y2']) > 0.01:
            # Need vertical extension
            extension = {
                'id': len(self.routing_segments),
                'transistor': last_seg['transistor'],
                'x1': last_seg['x2'],
                'y1': last_seg['y2'],
                'x2': last_seg['x2'],
                'y2': new_y,
                'type': 'vertical'
            }
            self.routing_segments.append(extension)
            
            # Also adjust X if needed
            if abs(new_x - last_seg['x2']) > 0.01:
                extension2 = {
                    'id': len(self.routing_segments),
                    'transistor': last_seg['transistor'],
                    'x1': last_seg['x2'],
                    'y1': new_y,
                    'x2': new_x,
                    'y2': new_y,
                    'type': 'horizontal'
                }
                self.routing_segments.append(extension2)
        
        elif last_seg['type'] == 'vertical' and abs(new_x - last_seg['x2']) > 0.01:
            # Need horizontal extension
            extension = {
                'id': len(self.routing_segments),
                'transistor': last_seg['transistor'],
                'x1': last_seg['x2'],
                'y1': last_seg['y2'],
                'x2': new_x,
                'y2': last_seg['y2'],
                'type': 'horizontal'
            }
            self.routing_segments.append(extension)
            
            # Also adjust Y if needed
            if abs(new_y - last_seg['y2']) > 0.01:
                extension2 = {
                    'id': len(self.routing_segments),
                    'transistor': last_seg['transistor'],
                    'x1': new_x,
                    'y1': last_seg['y2'],
                    'x2': new_x,
                    'y2': new_y,
                    'type': 'vertical'
                }
                self.routing_segments.append(extension2)
        else:
            # Just adjust the endpoint
            last_seg['x2'] = new_x
            last_seg['y2'] = new_y

    def detect_exit_direction(self, exit_points):
        """Detecta la dirección predominante de salida"""
        votes = {'up': 0, 'down': 0, 'left': 0, 'right': 0}
        
        for ep in exit_points:
            gate_x, gate_y = ep['gate_pos']
            exit_x, exit_y = ep['exit_pos']
            
            dx = exit_x - gate_x
            dy = exit_y - gate_y
            
            if abs(dx) > abs(dy):
                if dx > 0:
                    votes['right'] += 1
                else:
                    votes['left'] += 1
            else:
                # En canvas: Y+ hacia abajo
                if dy < 0:
                    votes['up'] += 1
                else:
                    votes['down'] += 1
        
        return max(votes, key=votes.get)

    def align_routes_final(self):
        """
        Alinea todas las rutas como paso final antes de exportar.
        Modifica los route_points para que todos los gates salgan alineados.
        """
        if not self.routing_segments:
            messagebox.showwarning("No Routes", "No routes to align!")
            return
        
        # Agrupar segmentos por transistor
        routes_by_transistor = {}
        for segment in self.routing_segments:
            t_key = segment['transistor']
            if t_key not in routes_by_transistor:
                routes_by_transistor[t_key] = []
            routes_by_transistor[t_key].append(segment)
        
        # Analizar cada ruta para encontrar el punto de salida
        exit_points = []
        for t_key, segments in routes_by_transistor.items():
            if not segments:
                continue
            
            t = self.transistors[t_key]
            if t['is_dummy']:
                continue
            
            # Encontrar el último segmento
            last_segment = segments[-1]
            
            # Punto de salida actual
            exit_x = last_segment['x2']
            exit_y = last_segment['y2']
            
            # Gate center
            gate_x = t['x'] + self.transistor_width / 2
            gate_y = t['y'] + self.transistor_height / 2
            
            exit_points.append({
                'transistor': t_key,
                'active_row': t['active_row'],
                'active_col': t['active_col'],
                'gate_pos': (gate_x, gate_y),
                'exit_pos': (exit_x, exit_y),
                'last_segment': last_segment,
                'segments': segments
            })
        
        if not exit_points:
            messagebox.showwarning("No Routes", "No active routes to align!")
            return
        
        # Detectar dirección predominante
        direction = self.detect_exit_direction(exit_points)
        
        # Diálogo para confirmar alineación
        result = self.show_alignment_dialog(direction, len(exit_points))
        if not result:
            return
        
        exit_direction = result['direction']
        exit_pitch = result['pitch']
        
        print(f"\n{'='*50}")
        print(f"ALIGNING ROUTES")
        print(f"Direction: {exit_direction}, Pitch: {exit_pitch}µm")
        print(f"{'='*50}")
        
        # Realizar alineación
        self.perform_alignment(exit_points, exit_direction, exit_pitch)
        
        # Redibujar
        self.draw_canvas()
        self.update_stats()
        
        messagebox.showinfo("Alignment Complete", 
                            f"Aligned {len(exit_points)} routes\n"
                            f"Direction: {exit_direction}\n"
                            f"Pitch: {exit_pitch}µm")

    def perform_alignment(self, exit_points, direction, pitch):
        """Realiza la alineación agregando extensiones a las rutas"""
        
        # Ordenar según la dirección
        if direction in ['up', 'down']:
            exit_points.sort(key=lambda ep: (ep['active_row'], ep['active_col']))
        else:
            exit_points.sort(key=lambda ep: (ep['active_col'], ep['active_row']))
        
        # Calcular línea de alineación con margen
        margin = 3.0  # µm de margen
        
        if direction == 'up':
            align_y = min(ep['exit_pos'][1] for ep in exit_points) - margin
        elif direction == 'down':
            align_y = max(ep['exit_pos'][1] for ep in exit_points) + margin
        elif direction == 'left':
            align_x = min(ep['exit_pos'][0] for ep in exit_points) - margin
        else:  # right
            align_x = max(ep['exit_pos'][0] for ep in exit_points) + margin
        
        # Calcular posición inicial para mantener orden
        if direction in ['up', 'down']:
            # Encontrar el centro X del array
            all_x = [ep['exit_pos'][0] for ep in exit_points]
            center_x = (min(all_x) + max(all_x)) / 2
            start_x = center_x - (len(exit_points) - 1) * pitch / 2
        else:
            # Encontrar el centro Y del array
            all_y = [ep['exit_pos'][1] for ep in exit_points]
            center_y = (min(all_y) + max(all_y)) / 2
            start_y = center_y - (len(exit_points) - 1) * pitch / 2
        
        # Aplicar alineación creando extensiones
        for i, ep in enumerate(exit_points):
            current_exit_x = ep['exit_pos'][0]
            current_exit_y = ep['exit_pos'][1]
            
            if direction in ['up', 'down']:
                new_x = start_x + i * pitch
                new_y = align_y
            else:  # left/right
                new_x = align_x
                new_y = start_y + i * pitch
            
            # Crear extensión si es necesaria
            dx = abs(new_x - current_exit_x)
            dy = abs(new_y - current_exit_y)
            
            if dx > 0.01 or dy > 0.01:
                self.create_alignment_extension(
                    ep['transistor'],
                    current_exit_x, current_exit_y,
                    new_x, new_y
                )
        
        print(f"✓ Aligned {len(exit_points)} routes")
        print(f"  Direction: {direction}")
        print(f"  Pitch: {pitch}µm")

    def create_alignment_extension(self, transistor_key, from_x, from_y, to_x, to_y):
        """
        Crea segmentos de extensión para alcanzar el punto alineado
        """
        # Snap to grid
        from_x = round(from_x / 0.05) * 0.05
        from_y = round(from_y / 0.05) * 0.05
        to_x = round(to_x / 0.05) * 0.05
        to_y = round(to_y / 0.05) * 0.05
        
        dx = abs(to_x - from_x)
        dy = abs(to_y - from_y)
        
        # Crear ruta Manhattan (L-shape si es necesario)
        if dx > 0.01 and dy > 0.01:
            # Necesitamos dos segmentos
            # Opción 1: Vertical primero, luego horizontal
            
            # Segmento vertical
            v_segment = {
                'id': len(self.routing_segments),
                'transistor': transistor_key,
                'x1': from_x,
                'y1': from_y,
                'x2': from_x,
                'y2': to_y,
                'type': 'vertical',
                'is_extension': True  # Marcar como extensión
            }
            self.routing_segments.append(v_segment)
            
            # Segmento horizontal
            h_segment = {
                'id': len(self.routing_segments),
                'transistor': transistor_key,
                'x1': from_x,
                'y1': to_y,
                'x2': to_x,
                'y2': to_y,
                'type': 'horizontal',
                'is_extension': True
            }
            self.routing_segments.append(h_segment)
            
        elif dx > 0.01:
            # Solo horizontal
            h_segment = {
                'id': len(self.routing_segments),
                'transistor': transistor_key,
                'x1': from_x,
                'y1': from_y,
                'x2': to_x,
                'y2': from_y,
                'type': 'horizontal',
                'is_extension': True
            }
            self.routing_segments.append(h_segment)
            
        elif dy > 0.01:
            # Solo vertical
            v_segment = {
                'id': len(self.routing_segments),
                'transistor': transistor_key,
                'x1': from_x,
                'y1': from_y,
                'x2': from_x,
                'y2': to_y,
                'type': 'vertical',
                'is_extension': True
            }
            self.routing_segments.append(v_segment)

    def show_alignment_dialog(self, detected_direction, num_routes):
        """Muestra diálogo para confirmar parámetros de alineación"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Route Alignment Settings")
        dialog.geometry("400x300")
        
        # Variables
        direction_var = tk.StringVar(value=detected_direction)
        pitch_var = tk.DoubleVar(value=1.0)
        
        # UI
        ttk.Label(dialog, text=f"Aligning {num_routes} routes", 
                font=('Arial', 12, 'bold')).grid(row=0, column=0, columnspan=2, pady=10)
        
        ttk.Label(dialog, text="Exit Direction:").grid(row=1, column=0, padx=10, pady=5, sticky='e')
        
        dir_frame = ttk.Frame(dialog)
        dir_frame.grid(row=1, column=1, padx=10, pady=5)
        
        for dir_name in ['up', 'down', 'left', 'right']:
            ttk.Radiobutton(dir_frame, text=dir_name.capitalize(), 
                            variable=direction_var, 
                            value=dir_name).pack(side=tk.LEFT)
        
        ttk.Label(dialog, text="Exit Pitch (µm):").grid(row=2, column=0, padx=10, pady=5, sticky='e')
        ttk.Spinbox(dialog, from_=0.5, to=5.0, increment=0.1, 
                    textvariable=pitch_var, width=10).grid(row=2, column=1, padx=10, pady=5, sticky='w')
        
        # Preview
        ttk.Label(dialog, text="Preview:", font=('Arial', 10, 'bold')).grid(row=3, column=0, columnspan=2, pady=10)
        
        preview_text = tk.Text(dialog, height=6, width=50)
        preview_text.grid(row=4, column=0, columnspan=2, padx=10, pady=5)
        
        def update_preview(*args):
            preview_text.delete(1.0, tk.END)
            dir_val = direction_var.get()
            pitch_val = pitch_var.get()
            
            if dir_val in ['up', 'down']:
                preview_text.insert(1.0, f"All routes will exit {dir_val.upper()}\n")
                preview_text.insert(tk.END, f"Horizontal spacing: {pitch_val}µm\n")
                preview_text.insert(tk.END, f"All exits at same Y coordinate\n")
            else:
                preview_text.insert(1.0, f"All routes will exit {dir_val.upper()}\n")
                preview_text.insert(tk.END, f"Vertical spacing: {pitch_val}µm\n")
                preview_text.insert(tk.END, f"All exits at same X coordinate\n")
        
        direction_var.trace('w', update_preview)
        pitch_var.trace('w', update_preview)
        update_preview()
        
        # Result
        result = {'confirmed': False}
        
        def apply():
            result['confirmed'] = True
            result['direction'] = direction_var.get()
            result['pitch'] = pitch_var.get()
            dialog.destroy()
        
        def cancel():
            dialog.destroy()
        
        ttk.Button(dialog, text="Apply Alignment", command=apply).grid(row=5, column=0, padx=10, pady=10)
        ttk.Button(dialog, text="Cancel", command=cancel).grid(row=5, column=1, padx=10, pady=10)
        
        dialog.wait_window()
        return result if result.get('confirmed') else None

    def debug_routing_info(self):
        """Print debug information about current routing state"""
        print("\n" + "="*50)
        print("DEBUG: Current Routing State")
        print("="*50)
        
        # Group segments by transistor
        routes_by_transistor = {}
        for seg in self.routing_segments:
            t_key = seg['transistor']
            if t_key not in routes_by_transistor:
                routes_by_transistor[t_key] = []
            routes_by_transistor[t_key].append(seg)
        
        print(f"Total routed transistors: {len(routes_by_transistor)}")
        
        # Organize by active row
        by_active_row = {}
        for t_key in routes_by_transistor:
            if t_key in self.transistors:
                t_info = self.transistors[t_key]
                active_row = t_info['active_row']
                if active_row not in by_active_row:
                    by_active_row[active_row] = []
                by_active_row[active_row].append({
                    'key': t_key,
                    'active_col': t_info['active_col'],
                    'segments': len(routes_by_transistor[t_key])
                })
        
        # Print organized info
        for row in sorted(by_active_row.keys()):
            transistors = sorted(by_active_row[row], key=lambda x: x['active_col'])
            cols_routed = [t['active_col'] for t in transistors]
            print(f"  Row {row}: Columns {cols_routed} routed")
            for t in transistors:
                print(f"    T{t['key']}: {t['segments']} segments")
        
        print("="*50)

def main():
    root = tk.Tk()
    app = AdvancedRoutingGUI(root)
    
    # Limpiar el estado al cerrar
    def on_closing():
        if hasattr(app, 'manhattan_router') and app.manhattan_router:
            app.manhattan_router = None
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()