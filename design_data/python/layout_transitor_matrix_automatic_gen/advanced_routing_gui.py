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

class StrictManhattanRouter:
    """Manejador de ruteo estrictamente Manhattan (solo H/V)"""
    
    def __init__(self, grid_snap=0.05):
        self.grid_snap = grid_snap  # Snap to 50nm grid
        self.segments = []
        self.current_point = None
        self.routing_mode = 'H'  # Empezar con horizontal
        
    def start_route(self, x, y):
        """Inicia una nueva ruta"""
        self.segments = []
        self.current_point = self.snap_to_grid(x, y)
        self.routing_mode = 'H'
        return self.current_point
    
    def snap_to_grid(self, x, y):
        """Ajusta coordenadas a la grilla"""
        x_snap = round(x / self.grid_snap) * self.grid_snap
        y_snap = round(y / self.grid_snap) * self.grid_snap
        return (x_snap, y_snap)
    
    def add_point(self, x, y):
        """Agrega un punto creando segmento H o V"""
        if not self.current_point:
            return []
        
        target = self.snap_to_grid(x, y)
        curr_x, curr_y = self.current_point
        tgt_x, tgt_y = target
        
        segments_added = []
        
        # Determinar si necesitamos movimiento H, V o ambos
        dx = abs(tgt_x - curr_x)
        dy = abs(tgt_y - curr_y)
        
        if dx > 0.01 and dy > 0.01:
            # Necesitamos ambos - crear ángulo recto
            if self.routing_mode == 'H':
                # Horizontal primero
                mid_point = (tgt_x, curr_y)
                segments_added.append({
                    'type': 'horizontal',
                    'start': self.current_point,
                    'end': mid_point
                })
                segments_added.append({
                    'type': 'vertical',
                    'start': mid_point,
                    'end': target
                })
                self.routing_mode = 'V'  # Alternar para próximo
            else:
                # Vertical primero
                mid_point = (curr_x, tgt_y)
                segments_added.append({
                    'type': 'vertical',
                    'start': self.current_point,
                    'end': mid_point
                })
                segments_added.append({
                    'type': 'horizontal',
                    'start': mid_point,
                    'end': target
                })
                self.routing_mode = 'H'  # Alternar para próximo
        elif dx > 0.01:
            # Solo horizontal
            segments_added.append({
                'type': 'horizontal',
                'start': self.current_point,
                'end': target
            })
        elif dy > 0.01:
            # Solo vertical
            segments_added.append({
                'type': 'vertical',
                'start': self.current_point,
                'end': target
            })
        
        if segments_added:
            self.segments.extend(segments_added)
            self.current_point = target
        
        return segments_added
    
    def get_preview_segments(self, x, y):
        """Obtiene segmentos de preview sin confirmar"""
        if not self.current_point:
            return []
        
        target = self.snap_to_grid(x, y)
        curr_x, curr_y = self.current_point
        tgt_x, tgt_y = target
        
        preview_segments = []
        
        dx = abs(tgt_x - curr_x)
        dy = abs(tgt_y - curr_y)
        
        if dx > 0.01 and dy > 0.01:
            if self.routing_mode == 'H':
                mid_point = (tgt_x, curr_y)
                preview_segments.append({
                    'type': 'horizontal',
                    'start': self.current_point,
                    'end': mid_point
                })
                preview_segments.append({
                    'type': 'vertical',
                    'start': mid_point,
                    'end': target
                })
            else:
                mid_point = (curr_x, tgt_y)
                preview_segments.append({
                    'type': 'vertical',
                    'start': self.current_point,
                    'end': mid_point
                })
                preview_segments.append({
                    'type': 'horizontal',
                    'start': mid_point,
                    'end': target
                })
        elif dx > 0.01:
            preview_segments.append({
                'type': 'horizontal',
                'start': self.current_point,
                'end': target
            })
        elif dy > 0.01:
            preview_segments.append({
                'type': 'vertical',
                'start': self.current_point,
                'end': target
            })
        
        return preview_segments
    
    def finish_route(self):
        """Finaliza la ruta y retorna todos los segmentos"""
        result = self.segments.copy()
        self.segments = []
        self.current_point = None
        self.routing_mode = 'H'
        return result

class AdvancedRoutingGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Gate Routing Designer - Manhattan Routing")
        
        # Parámetros del array (en micrómetros)
        self.array_rows = 4
        self.array_cols = 4
        self.has_dummies = True
        
        # Dimensiones físicas reales (µm) - según PDK IHP SG13G2
        self.transistor_factor_multiplier = 1 
        self.transistor_width = 1.03 * self.transistor_factor_multiplier  # µm (en dirección X)
        self.transistor_height = 1.36 * self.transistor_factor_multiplier   # µm (en dirección Y)
        self.pitch_x = 3.13 * self.transistor_factor_multiplier           # µm (incluye guardring)
        self.pitch_y = 3.46  * self.transistor_factor_multiplier          # µm (incluye guardring)
        self.metal3_width = 0.2        # µm
        
        # Parámetros de visualización
        self.zoom_level = 50.0         # pixels/µm
        self.grid_spacing = 0.5        # µm
        self.canvas_width = 800
        self.canvas_height = 600
        
        # Offset del canvas (para pan)
        self.canvas_offset_x = 50
        self.canvas_offset_y = 50
        
        # Estado
        self.transistors = {}  # Dict[tuple(row,col), transistor_info]
        self.routing_segments = []  # Lista de todos los segmentos
        self.drawing = False
        self.selected_transistor = None
        self.selected_segment = None
        self.mouse_start = None
        self.manhattan_router = None  # Para ruteo Manhattan estricto
        
        # Modo de edición
        self.edit_mode = 'draw'  # 'draw', 'delete', 'move'
        
        # Colores
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
        
        # Mostrar instrucciones iniciales
        instructions = """MANHATTAN ROUTING ENABLED - WITH COORDINATE MAPPING
        
Instructions:
1. Click on a transistor gate (red line) to start routing
2. Drag to create route - alternates H/V automatically
3. Release to confirm the route
4. Right-click to cancel current route or delete last route
5. Use "Copy Pattern Dict" to export for KLayout

IMPORTANT - Coordinate System:
- GUI Display: Row 0 = TOP, Row N = BOTTOM
- KLayout: Row 0 = BOTTOM, Row N = TOP
- The pattern export automatically handles this mapping!
- Each transistor shows both coordinates:
  * GUI[row,col] = coordinates in this interface
  * KL[row,col] = coordinates in KLayout

Routing Rules:
- Routes are strictly horizontal/vertical (Manhattan)
- First segment alternates H→V→H→V for each new route
- Routes snap to 50nm grid
- Direction is automatically inverted for KLayout

Tips:
- Plan your route path before clicking
- Avoid crossing other routes
- Keep routes as short as possible
- The pattern is automatically converted for KLayout"""
        
        self.report_text.insert(1.0, instructions)
        
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="5")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Toolbar
        toolbar = ttk.Frame(main_frame)
        toolbar.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Manhattan routing indicator
        manhattan_label = ttk.Label(toolbar, text="MANHATTAN ROUTING", 
                                  font=('Arial', 10, 'bold'), foreground='green')
        manhattan_label.pack(side=tk.LEFT, padx=10)
        
        ttk.Separator(toolbar, orient='vertical').pack(side=tk.LEFT, fill='y', padx=5)
        
        # Controles de array
        ttk.Label(toolbar, text="Array:").pack(side=tk.LEFT, padx=5)
        
        self.rows_var = tk.IntVar(value=self.array_rows)
        ttk.Spinbox(toolbar, from_=2, to=20, width=5, textvariable=self.rows_var,
                   command=self.update_array).pack(side=tk.LEFT)
        
        ttk.Label(toolbar, text="x").pack(side=tk.LEFT, padx=2)
        
        self.cols_var = tk.IntVar(value=self.array_cols)
        ttk.Spinbox(toolbar, from_=2, to=20, width=5, textvariable=self.cols_var,
                   command=self.update_array).pack(side=tk.LEFT)
        
        self.dummies_var = tk.BooleanVar(value=self.has_dummies)
        ttk.Checkbutton(toolbar, text="Side Dummies", variable=self.dummies_var,
                       command=self.update_array).pack(side=tk.LEFT, padx=10)
        
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
        """Crea el array de transistores con dummies solo en columnas laterales"""
        self.transistors.clear()
        rows = self.rows_var.get()
        cols = self.cols_var.get()
        
        total_rows = rows
        total_cols = cols
        
        if self.has_dummies:
            total_cols += 2  # Solo agregar columnas dummy, no filas
        
        for row in range(total_rows):
            for col in range(total_cols):
                # Determinar si es dummy (solo columnas laterales)
                is_dummy = False
                if self.has_dummies:
                    is_dummy = (col == 0 or col == total_cols-1)
                
                # Posición del transistor
                x = col * self.pitch_x
                y = row * self.pitch_y
                
                # Calcular índices activos
                if self.has_dummies and not is_dummy:
                    active_row = row
                    active_col = col - 1  # Restar 1 por la columna dummy izquierda
                else:
                    active_row = row if not is_dummy else -1
                    active_col = col if not is_dummy else -1
                
                # Crear info del transistor
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
        """Dibuja transistor con orientación correcta: |DRAIN|GATE|SOURCE|"""
        x, y = t['x'], t['y']
        
        # Convertir a canvas
        x1, y1 = self.um_to_canvas(x, y)
        x2, y2 = self.um_to_canvas(x + self.transistor_width, 
                                y + self.transistor_height)
        
        # Color según tipo
        fill_color = self.colors['dummy'] if t['is_dummy'] else self.colors['transistor']
        
        # Dibujar rectángulo del transistor
        rect = self.canvas.create_rectangle(x1, y1, x2, y2,
                                        fill=fill_color,
                                        outline='black',
                                        width=2,
                                        tags=f"transistor_{t['row']}_{t['col']}")
        
        # Dibujar DRAIN (izquierda)
        drain_x = x + self.transistor_width * 0.2
        drain_y = y + self.transistor_height / 2
        dx1, dy1 = self.um_to_canvas(drain_x - 0.05, drain_y - 0.05)
        dx2, dy2 = self.um_to_canvas(drain_x + 0.05, drain_y + 0.05)
        self.canvas.create_oval(dx1, dy1, dx2, dy2,
                            fill='#44ff44', outline='darkgreen',
                            tags=f"drain_{t['row']}_{t['col']}")
        
        # Dibujar GATE (centro - línea vertical)
        gate_x = x + self.transistor_width / 2
        gx1, gy1 = self.um_to_canvas(gate_x - 0.02, y + 0.1)
        gx2, gy2 = self.um_to_canvas(gate_x + 0.02, y + self.transistor_height - 0.1)
        self.canvas.create_rectangle(gx1, gy1, gx2, gy2,
                                fill=self.colors['gate'],
                                outline='darkred',
                                width=1,
                                tags=f"gate_{t['row']}_{t['col']}")
        
        # Dibujar SOURCE (derecha)
        source_x = x + self.transistor_width * 0.8
        source_y = y + self.transistor_height / 2
        sx1, sy1 = self.um_to_canvas(source_x - 0.05, source_y - 0.05)
        sx2, sy2 = self.um_to_canvas(source_x + 0.05, source_y + 0.05)
        self.canvas.create_oval(sx1, sy1, sx2, sy2,
                            fill='#4444ff', outline='darkblue',
                            tags=f"source_{t['row']}_{t['col']}")
        
        # Etiquetas D, G, S
        if not t['is_dummy']:
            # Solo para transistores activos
            font_size = max(6, int(8 * self.zoom_level / 50))
            dx, dy = self.um_to_canvas(drain_x, y - 0.2)
            self.canvas.create_text(dx, dy, text="D", font=('Arial', font_size))
            gx, gy = self.um_to_canvas(gate_x, y - 0.2)
            self.canvas.create_text(gx, gy, text="G", font=('Arial', font_size))
            sx, sy = self.um_to_canvas(source_x, y - 0.2)
            self.canvas.create_text(sx, sy, text="S", font=('Arial', font_size))
        
        # Etiqueta del transistor mostrando ambas coordenadas para claridad
        if t['is_dummy']:
            label = f"D[{t['row']},{t['col']}]"
        else:
            active_row = t['row']
            active_col = t['col'] - (1 if self.has_dummies else 0)
            
            # Calcular coordenada KLayout
            klayout_row = (self.array_rows - 1) - active_row
            
            # Mostrar ambas para debugging
            label = f"G[{active_row},{active_col}]\nK[{klayout_row},{active_col}]"
        
        lx, ly = self.um_to_canvas(x - 0.5, y + self.transistor_height / 2)
        self.canvas.create_text(lx, ly, text=label, font=('Arial', 7),
                            anchor='e', tags=f"label_{t['row']}_{t['col']}")

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
        """Dibuja un segmento de ruta"""
        x1, y1 = self.um_to_canvas(segment['x1'], segment['y1'])
        x2, y2 = self.um_to_canvas(segment['x2'], segment['y2'])
        
        color = self.colors['routing']
        if segment.get('selected', False):
            color = self.colors['routing_selected']
        
        width = max(2, int(self.metal3_width * self.zoom_level))
        
        line = self.canvas.create_line(x1, y1, x2, y2,
                                     fill=color,
                                     width=width,
                                     capstyle='projecting',
                                     tags=f"segment_{segment['id']}")
        segment['canvas_id'] = line
    
    def find_transistor_at(self, x_um, y_um):
        """Encuentra el transistor en las coordenadas dadas (gate)"""
        for t in self.transistors.values():
            gate_x = t['x'] + self.transistor_width / 2
            gate_y = t['y'] + self.transistor_height / 2
            
            if (abs(x_um - gate_x) < 0.2 and 
                abs(y_um - gate_y) < 0.2):
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
        """Manejo del click del mouse"""
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        x_um, y_um = self.canvas_to_um(x, y)
        
        mode = self.mode_var.get()
        
        if mode == 'draw':
            t = self.find_transistor_at(x_um, y_um)
            if t and not t['is_dummy']:
                self.selected_transistor = t
                self.drawing = True
                
                # Iniciar router Manhattan
                self.manhattan_router = StrictManhattanRouter()
                # Comenzar en el centro del gate
                gate_x = t['x'] + self.transistor_width / 2
                gate_y = t['y'] + self.transistor_height / 2
                self.manhattan_router.start_route(gate_x, gate_y)
                
                gate_tag = f"gate_{t['row']}_{t['col']}"
                self.canvas.itemconfig(gate_tag, fill=self.colors['gate_selected'])
        
        elif mode == 'delete':
            segment = self.find_segment_at(x_um, y_um)
            if segment:
                self.delete_segment(segment)
        
        self.mouse_start = (x, y)
    
    def on_mouse_drag(self, event):
        """Manejo del arrastre con ruteo Manhattan estricto"""
        if not self.drawing or not self.selected_transistor:
            return
        
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        x_um, y_um = self.canvas_to_um(x, y)
        
        # Obtener segmentos de preview
        preview_segments = self.manhattan_router.get_preview_segments(x_um, y_um)
        
        # Dibujar preview
        self.canvas.delete("preview")
        
        for seg in preview_segments:
            x1, y1 = self.um_to_canvas(*seg['start'])
            x2, y2 = self.um_to_canvas(*seg['end'])
            
            self.canvas.create_line(x1, y1, x2, y2,
                                   fill=self.colors['routing_preview'],
                                   width=max(2, int(self.metal3_width * self.zoom_level)),
                                   capstyle='projecting',
                                   tags="preview")
        
        # Mostrar modo actual
        mode_text = "Mode: " + ("Horizontal" if self.manhattan_router.routing_mode == 'H' else "Vertical")
        self.coord_label.config(text=f"X: {x_um:.2f} µm\nY: {y_um:.2f} µm\n{mode_text}")
    
    def on_mouse_up(self, event):
        """Confirma el ruteo Manhattan"""
        if not self.drawing or not self.selected_transistor:
            return
        
        self.drawing = False
        self.canvas.delete("preview")
        
        if self.manhattan_router:
            # Agregar punto final
            x = self.canvas.canvasx(event.x)
            y = self.canvas.canvasy(event.y)
            x_um, y_um = self.canvas_to_um(x, y)
            
            self.manhattan_router.add_point(x_um, y_um)
            
            # Obtener todos los segmentos
            segments = self.manhattan_router.finish_route()
            
            if segments:
                # Convertir a formato de la GUI
                t_key = (self.selected_transistor['row'], self.selected_transistor['col'])
                
                for seg in segments:
                    x1, y1 = seg['start']
                    x2, y2 = seg['end']
                    
                    segment_data = {
                        'id': len(self.routing_segments),
                        'transistor': t_key,
                        'x1': x1, 'y1': y1,
                        'x2': x2, 'y2': y2,
                        'type': seg['type']
                    }
                    
                    self.routing_segments.append(segment_data)
                    self.draw_segment(segment_data)
                
                self.selected_transistor['routed'] = True
            
            # Limpiar
            self.manhattan_router = None
        
        # Restaurar color del gate
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
    
    def on_mouse_move(self, event):
        """Actualiza las coordenadas del mouse"""
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        x_um, y_um = self.canvas_to_um(x, y)
        
        # Si no estamos dibujando, mostrar solo coordenadas
        if not self.drawing or not self.manhattan_router:
            self.coord_label.config(text=f"X: {x_um:.2f} µm\nY: {y_um:.2f} µm")
    
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
    
    def update_array(self):
        """Actualiza el array cuando cambian los parámetros"""
        self.array_rows = self.rows_var.get()
        self.array_cols = self.cols_var.get()
        self.has_dummies = self.dummies_var.get()
        
        self.routing_segments.clear()
        
        self.create_array()
        self.draw_canvas()
        self.update_stats()
    
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
        """Guarda el patrón actual en un archivo"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialfile=f"routing_pattern_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        
        if filename:
            # Generar pattern_data directamente
            pattern_dict = self.generate_pattern_dict()
            
            # Convertir tuplas a strings para JSON
            json_pattern = {}
            for (row, col), data in pattern_dict.items():
                key = f"{row},{col}"
                json_pattern[key] = data
            
            pattern_data = {
                'metadata': {
                    'array_rows': self.array_rows,
                    'array_cols': self.array_cols,
                    'has_dummies': self.has_dummies,
                    'pitch_x': self.pitch_x,
                    'pitch_y': self.pitch_y,
                    'timestamp': datetime.now().isoformat()
                },
                'pattern_data': json_pattern
            }
            
            with open(filename, 'w') as f:
                json.dump(pattern_data, f, indent=2)
            
            messagebox.showinfo("Save Pattern", f"Pattern saved to {filename}")

    def load_pattern(self):
        """Carga un patrón desde archivo"""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            with open(filename, 'r') as f:
                pattern_data = json.load(f)
            
            meta = pattern_data['metadata']
            if (meta['array_rows'] != self.array_rows or
                meta['array_cols'] != self.array_cols or
                meta['has_dummies'] != self.has_dummies):
                
                if messagebox.askyesno("Load Pattern", 
                                     "Pattern was created for a different array size.\n"
                                     "Do you want to adjust the array to match?"):
                    self.rows_var.set(meta['array_rows'])
                    self.cols_var.set(meta['array_cols'])
                    self.dummies_var.set(meta['has_dummies'])
                    self.update_array()
            
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
            
            messagebox.showinfo("Load Pattern", f"Pattern loaded from {filename}")
    
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
        """Genera el diccionario de patrones a partir de segmentos Manhattan"""
        pattern_dict = {}
        
        # Agrupar segmentos por transistor
        transistor_routes = {}
        for segment in self.routing_segments:
            t_key = segment['transistor']
            if t_key not in transistor_routes:
                transistor_routes[t_key] = []
            transistor_routes[t_key].append(segment)
        
        # Analizar cada transistor
        for t_key in sorted(transistor_routes.keys()):
            row, col = t_key
            segments = transistor_routes[t_key]
            
            if not segments or self.transistors[t_key].get('is_dummy', False):
                continue
            
            t = self.transistors[t_key]
            
            # Centro del GATE (línea vertical en el medio)
            gate_x = t['x'] + self.transistor_width / 2
            gate_y = t['y'] + self.transistor_height / 2
            
            # Encontrar el segmento más cercano al gate (debería ser el primero)
            min_dist = float('inf')
            start_point = None
            
            for seg in segments:
                # Verificar distancia del inicio del segmento al gate
                dist = math.sqrt((seg['x1'] - gate_x)**2 + (seg['y1'] - gate_y)**2)
                if dist < min_dist:
                    min_dist = dist
                    start_point = (seg['x1'], seg['y1'])
            
            if not start_point:
                continue
            
            # Offset desde el centro del gate
            offset_y = start_point[1] - gate_y
            
            # Calcular longitudes H y V
            h_length = 0
            v_length = 0
            
            # Encontrar el punto más alejado para determinar dirección
            max_y = min_y = gate_y
            
            for seg in segments:
                if seg['type'] == 'horizontal':
                    h_length += abs(seg['x2'] - seg['x1'])
                else:
                    v_length += abs(seg['y2'] - seg['y1'])
                
                # Actualizar extremos Y
                max_y = max(max_y, seg['y1'], seg['y2'])
                min_y = min(min_y, seg['y1'], seg['y2'])
            
            # Determinar dirección basada en el punto final
            # Si el extremo está por encima del centro del array, va arriba
            array_center_y = sum(t['y'] for t in self.transistors.values() if not t['is_dummy']) / sum(1 for t in self.transistors.values() if not t['is_dummy'])
            
            # El punto más alejado del gate determina la dirección
            if abs(max_y - gate_y) > abs(min_y - gate_y):
                final_y = max_y
            else:
                final_y = min_y
            
            goes_up = final_y < array_center_y
            
            # Coordenadas activas
            active_row = row
            active_col = col - 1 if self.has_dummies else col
            
            # INVERTIR SOLO LAS COORDENADAS DE FILA para KLayout
            # En GUI: row 0 = arriba, en KLayout: row 0 = abajo
            klayout_row = (self.array_rows - 1) - active_row
            
            # NO INVERTIR la dirección goes_up - mantenerla igual
            pattern_dict[(klayout_row, active_col)] = {
                'offset_y': round(offset_y, 2),
                'h_length': round(h_length, 2),
                'v_length': round(v_length, 2),
                'goes_up': goes_up  # Mantener la dirección sin invertir
            }
        
        return pattern_dict
    
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