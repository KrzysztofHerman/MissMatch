#!/usr/bin/env python3
"""
Transistor array 4x4 for mismatch evaluation with shared guardrings
IHP SG13G2 PDK - KLayout
MODIFIED VERSION - Accepts pattern from GUI

Features:
- 4x4 array with side dummies only
- Shared guardring borders between adjacent transistors
- S, D, B shared across all transistors
- Independent gates routed without overlap
- Pattern can be loaded from external source (GUI)
"""

import pya
import klayout.db as db
import sys
import json

# ========== CONFIGURATION ==========
ARRAY_SIZE = 4          # 4x4 array (change this to scale: 6, 8, 10, etc.)
MULTIPLICATION_FACTOR = 1
TRANSISTOR_W = 1.03*MULTIPLICATION_FACTOR    # µm - MATCHED to GUI value
TRANSISTOR_L = 0.35*MULTIPLICATION_FACTOR    # µm
TRANSISTOR_NG = 1       # fingers

# Spacings (µm)
GUARDRING_WIDTH = 0.5*MULTIPLICATION_FACTOR       # Guardring width
GUARDRING_SPACING = 0.8*MULTIPLICATION_FACTOR     # Space between transistor and guardring
GUARDRING_SHARE = True      # Share guardring borders

# Design rules IHP SG13G2
METAL1_WIDTH = 0.28
METAL2_WIDTH = 0.36
METAL3_WIDTH = 0.20      # MATCHED to GUI value (0.2 µm)
POLY_WIDTH = 0.13
VIA1_SIZE = 0.26
VIA2_SIZE = 0.26
CONT_SIZE = 0.22
CONT_SPACING = 0.28
PAD_SIZE = 50.0

# PDK
LIB_NAME = 'SG13_dev'

# Layers
LAYER_MAP = {
    'Activ':    (1, 0),
    'GatPoly':  (5, 0),
    'Cont':     (6, 0),
    'nSD':      (7, 0),
    'Metal1':   (8, 0),
    'Metal2':   (10, 0),
    'Metal3':   (30, 0),
    'pSD':      (14, 0),
    'Via1':     (19, 0),
    'Via2':     (29, 0),
    'NWell':    (31, 0),
    'Ptap':     (32, 0),
    'Ntap':     (33, 0),  
    'TEXT':     (63, 0),
}

def load_pattern_data():
    """Load routing pattern from external source or use default"""
    
    # Option 1: Pattern passed as global variable
    if 'custom_pattern' in globals():
        print("✓ Using custom pattern from global variable")
        return custom_pattern
    
    # Option 2: Pattern file specified
    if 'pattern_file' in globals():
        print(f"✓ Loading pattern from file: {pattern_file}")
        try:
            with open(pattern_file, 'r') as f:
                data = json.load(f)
                json_pattern = data.get('pattern_data', {})
                
                # Convert string keys back to tuples
                pattern = {}
                for str_key, value in json_pattern.items():
                    row, col = map(int, str_key.split(','))
                    pattern[(row, col)] = value
                
                return pattern
        except Exception as e:
            print(f"⚠ Error loading pattern file: {e}")
    
    # Option 3: Check for temp_pattern.json (from GUI)
    try:
        with open('temp_pattern.json', 'r') as f:
            data = json.load(f)
            json_pattern = data.get('pattern_data', {})
            
            # Convert string keys back to tuples
            pattern = {}
            for str_key, value in json_pattern.items():
                row, col = map(int, str_key.split(','))
                pattern[(row, col)] = value
            
            print("✓ Found temp_pattern.json from GUI")
            return pattern
    except:
        pass
    
    # Option 4: Default pattern
    print("✓ Using default pattern")
    return {
        (0, 0): {'offset_y': -0.20, 'h_length': 0.60, 'v_length': 5.20, 'goes_up': True},
        (0, 1): {'offset_y': -0.15, 'h_length': 1.20, 'v_length': 5.15, 'goes_up': True},
        (0, 2): {'offset_y': -0.10, 'h_length': 1.80, 'v_length': 5.10, 'goes_up': True},
        (0, 3): {'offset_y': -0.05, 'h_length': 2.40, 'v_length': 5.05, 'goes_up': True},
        
        (1, 0): {'offset_y': -0.10, 'h_length': 0.50, 'v_length': 4.60, 'goes_up': True},
        (1, 1): {'offset_y': -0.05, 'h_length': 1.10, 'v_length': 4.55, 'goes_up': True},
        (1, 2): {'offset_y':  0.00, 'h_length': 1.70, 'v_length': 4.50, 'goes_up': True},
        (1, 3): {'offset_y':  0.05, 'h_length': 2.30, 'v_length': 4.45, 'goes_up': True},
        
        (2, 0): {'offset_y':  0.05, 'h_length': 0.60, 'v_length': 4.45, 'goes_up': False},
        (2, 1): {'offset_y':  0.00, 'h_length': 1.20, 'v_length': 4.50, 'goes_up': False},
        (2, 2): {'offset_y': -0.05, 'h_length': 1.80, 'v_length': 4.55, 'goes_up': False},
        (2, 3): {'offset_y': -0.10, 'h_length': 2.40, 'v_length': 4.60, 'goes_up': False},
        
        (3, 0): {'offset_y':  0.15, 'h_length': 0.50, 'v_length': 5.05, 'goes_up': False},
        (3, 1): {'offset_y':  0.10, 'h_length': 1.10, 'v_length': 5.10, 'goes_up': False},
        (3, 2): {'offset_y':  0.05, 'h_length': 1.70, 'v_length': 5.15, 'goes_up': False},
        (3, 3): {'offset_y':  0.00, 'h_length': 2.30, 'v_length': 5.20, 'goes_up': False},
    }

class MismatchArray4x4:
    """Generator for 4x4 array with shared guardrings"""
    
    def __init__(self):
        print("\n" + "="*60)
        print("MISMATCH ARRAY GENERATOR - INITIALIZATION")
        print("="*60)
        
        # Load library
        self.lib = pya.Library.library_by_name(LIB_NAME)
        if not self.lib:
            raise Exception(f"Library {LIB_NAME} not found")
        
        # Create layout
        self.layout = db.Layout(True)
        self.layout.dbu = 0.001  # 1nm
        self.top_cell = self.layout.create_cell('MismatchArray4x4_SharedGR')
        
        # Create layer indices
        self.layers = {}
        for name, (layer, datatype) in LAYER_MAP.items():
            self.layers[name] = self.layout.layer(layer, datatype)
        
        print(f"✓ Layout initialized")
        print(f"✓ Library: {LIB_NAME}")
        print(f"✓ Database unit: {self.layout.dbu} µm")
        
        # Debug tracking
        self.debug_info = {
            'transistor_count': 0,
            'dummy_count': 0,
            'gate_routes': [],
            'pattern_verification': []
        }
    
    def dbu(self, value_um):
        """Convert µm to database units"""
        return int(value_um / self.layout.dbu)
    
    def create_transistor_pcell(self, transistor_type='nmos'):
        """Create transistor PCell"""
        pcell_name = transistor_type  # 'nmos' o 'pmos'
        
        # Buscar la declaración de la PCell
        pcell_decl = self.lib.layout().pcell_declaration(pcell_name)
        if not pcell_decl:
            # Listar PCells disponibles para debug
            print(f"\n⚠ PCell '{pcell_name}' not found")
            print("Available PCells in library:")
            for i in range(self.lib.layout().pcells()):
                pd = self.lib.layout().pcell_declaration(i)
                if pd:
                    print(f"  - {pd.name()}")
            raise Exception(f"PCell {pcell_name} not found in library {LIB_NAME}")
        
        # Parámetros para la PCell como strings
        params = {
            'w': f'{TRANSISTOR_W}u',
            'l': f'{TRANSISTOR_L}u',
            'ng': str(TRANSISTOR_NG)
        }
        
        # Crear instancia de la PCell usando add_pcell_variant
        return self.layout.add_pcell_variant(self.lib, pcell_decl.id(), params)
    
    def calculate_shared_guardring_array(self, transistor_bbox, rows, cols):
        """Calculate dimensions for array with shared guardrings"""
        
        # Calculate actual pitches - MUST match GUI values
        pitch_x = self.dbu(3.13)  # Exact value from GUI
        pitch_y = self.dbu(3.46)  # Exact value from GUI
        
        # Verify calculation
        calculated_pitch_x = transistor_bbox.width() + 2 * self.dbu(GUARDRING_SPACING) + self.dbu(GUARDRING_WIDTH)
        calculated_pitch_y = transistor_bbox.height() + 2 * self.dbu(GUARDRING_SPACING) + self.dbu(GUARDRING_WIDTH)
        
        print(f"\nPitch verification:")
        print(f"  GUI pitch X: 3.13 µm, calculated: {calculated_pitch_x * self.layout.dbu:.2f} µm")
        print(f"  GUI pitch Y: 3.46 µm, calculated: {calculated_pitch_y * self.layout.dbu:.2f} µm")
        
        # Use GUI values
        if abs(calculated_pitch_x - pitch_x) > self.dbu(0.01):
            print(f"  ⚠ Using GUI pitch_x value instead of calculated")
        if abs(calculated_pitch_y - pitch_y) > self.dbu(0.01):
            print(f"  ⚠ Using GUI pitch_y value instead of calculated")
        
        gr_width = self.dbu(GUARDRING_WIDTH)
        gr_spacing = self.dbu(GUARDRING_SPACING)
        
        total_width = cols * pitch_x + gr_width
        total_height = rows * pitch_y + gr_width
        
        cell_inner_width = pitch_x - gr_width
        cell_inner_height = pitch_y - gr_width
        
        return {
            'pitch_x': pitch_x,
            'pitch_y': pitch_y,
            'gr_width': gr_width,
            'gr_spacing': gr_spacing,
            'total_width': total_width,
            'total_height': total_height,
            'cell_inner_width': cell_inner_width,
            'cell_inner_height': cell_inner_height
        }
    
    def create_shared_guardring_structure(self, array_cell, geom, rows, cols, transistor_type):
        """Create shared guardring structure for entire array"""
        print("\nCreating shared guardring structure...")
        
        gr_width = geom['gr_width']
        
        # Create vertical guardring stripes
        for col in range(cols + 1):
            x = col * geom['pitch_x']
            stripe = db.Box(
                x, 0,
                x + gr_width, geom['total_height']
            )
            array_cell.shapes(self.layers['Activ']).insert(stripe)
            
            if transistor_type == 'nmos':
                array_cell.shapes(self.layers['pSD']).insert(stripe)
                array_cell.shapes(self.layers['Ptap']).insert(stripe)
            else:
                array_cell.shapes(self.layers['nSD']).insert(stripe)
                array_cell.shapes(self.layers['Ntap']).insert(stripe)
        
        # Create horizontal guardring stripes
        for row in range(rows + 1):
            y = row * geom['pitch_y']
            stripe = db.Box(
                0, y,
                geom['total_width'], y + gr_width
            )
            array_cell.shapes(self.layers['Activ']).insert(stripe)
            
            if transistor_type == 'nmos':
                array_cell.shapes(self.layers['pSD']).insert(stripe)
                array_cell.shapes(self.layers['Ptap']).insert(stripe)
            else:
                array_cell.shapes(self.layers['nSD']).insert(stripe)
                array_cell.shapes(self.layers['Ntap']).insert(stripe)
        
        # Add NWell for PMOS
        if transistor_type == 'pmos':
            nwell_box = db.Box(
                -self.dbu(0.5), -self.dbu(0.5),
                geom['total_width'] + self.dbu(0.5),
                geom['total_height'] + self.dbu(0.5)
            )
            array_cell.shapes(self.layers['NWell']).insert(nwell_box)
        
        # Add contacts to guardring intersections
        cont_size = self.dbu(CONT_SIZE)
        for row in range(rows + 1):
            for col in range(cols + 1):
                x = col * geom['pitch_x'] + gr_width // 2
                y = row * geom['pitch_y'] + gr_width // 2
                
                cont_box = db.Box(
                    x - cont_size//2, y - cont_size//2,
                    x + cont_size//2, y + cont_size//2
                )
                array_cell.shapes(self.layers['Cont']).insert(cont_box)
                
                m1_box = cont_box.enlarged(self.dbu(0.05))
                array_cell.shapes(self.layers['Metal1']).insert(m1_box)
        
        print(f"✓ Created shared guardring grid: {cols+1} x {rows+1} stripes")
    
    def create_array_with_shared_guardrings(self, transistor_type='nmos'):
        """Create complete array with shared guardrings"""
        print(f"\n{'='*60}")
        print(f"Creating {transistor_type.upper()} array {ARRAY_SIZE}x{ARRAY_SIZE}")
        print(f"{'='*60}")
        
        array_cell = self.layout.create_cell(f'{transistor_type}_array_{ARRAY_SIZE}x{ARRAY_SIZE}')
        
        transistor_pcell = self.create_transistor_pcell(transistor_type)
        transistor_cell = self.layout.cell(transistor_pcell)
        t_bbox = transistor_cell.bbox()
        
        total_cols = ARRAY_SIZE + 2  # Add dummy columns
        total_rows = ARRAY_SIZE
        geom = self.calculate_shared_guardring_array(t_bbox, total_rows, total_cols)
        
        self.create_shared_guardring_structure(array_cell, geom, total_rows, total_cols, transistor_type)
        
        transistor_info = []
        active_count = 0
        dummy_count = 0
        
        for row in range(total_rows):
            row_info = []
            for col in range(total_cols):
                cell_center_x = col * geom['pitch_x'] + geom['gr_width'] + geom['cell_inner_width'] // 2
                cell_center_y = row * geom['pitch_y'] + geom['gr_width'] + geom['cell_inner_height'] // 2
                
                trans = db.Trans(db.Point(cell_center_x - t_bbox.width()//2, 
                                        cell_center_y - t_bbox.height()//2))
                array_cell.insert(db.CellInstArray(transistor_pcell, trans))
                
                is_dummy = (col == 0 or col == total_cols - 1)
                
                info = {
                    'row': row,
                    'col': col,
                    'active_row': row,
                    'active_col': col - 1 if not is_dummy else -1,
                    'x': cell_center_x,
                    'y': cell_center_y,
                    'is_dummy': is_dummy,
                    'gate_x': cell_center_x * self.layout.dbu,  # Convert to µm
                    'gate_y': cell_center_y * self.layout.dbu   # Convert to µm
                }
                
                row_info.append(info)
                transistor_info.append(info)
                
                if is_dummy:
                    self.debug_info['dummy_count'] += 1
                    dummy_count += 1
                else:
                    self.debug_info['transistor_count'] += 1
                    active_count += 1
            
            transistor_info.extend(row_info)
        
        print(f"✓ Placed {active_count} active + {dummy_count} dummy transistors")
        
        return array_cell, transistor_info, geom
    
    def route_gate_connections(self, array_cell, transistor_info, transistor_type):
        """Route gate connections with pattern from GUI - FIXED VERSION"""
        print(f"\nRouting gate connections for {transistor_type}...")
        
        # Load pattern data
        pattern_data = load_pattern_data()
        
        # Verify pattern
        print(f"✓ Loaded pattern with {len(pattern_data)} entries")
        
        m3_width = self.dbu(METAL3_WIDTH)
        
        active_transistors = [t for t in transistor_info if not t['is_dummy']]
        print(f"✓ Found {len(active_transistors)} active transistors to route")
        
        routed_count = 0
        
        for t in active_transistors:
            row = t['active_row']
            col = t['active_col']
            
            pattern_key = (row, col)
            if pattern_key not in pattern_data:
                print(f"⚠ No pattern found for transistor [{row},{col}]")
                continue
            
            pattern = pattern_data[pattern_key]
            
            # Gate position (center of transistor)
            gate_x = t['x']
            gate_y = t['y']
            
            # Create via stack at gate
            self.create_gate_via_stack(array_cell, gate_x, gate_y)
            
            # Start position (offset from gate center)
            offset_y_dbu = self.dbu(pattern['offset_y'])
            start_x = gate_x
            start_y = gate_y + offset_y_dbu
            
            # Connect point (where horizontal meets vertical)
            connect_y = start_y
            
            # Horizontal segment length
            h_length_dbu = self.dbu(pattern['h_length'])
            
            # Determine horizontal direction based on column position
            if col >= ARRAY_SIZE//2:
                # Right half goes right
                b_end_x = start_x + h_length_dbu
            else:
                # Left half goes left
                b_end_x = start_x - h_length_dbu
            
            # Draw horizontal segment if it has length
            if h_length_dbu > 0:
                h_box = db.Box(
                    min(start_x, b_end_x) - m3_width//2, start_y - m3_width//2,
                    max(start_x, b_end_x) + m3_width//2, start_y + m3_width//2
                )
                array_cell.shapes(self.layers['Metal3']).insert(h_box)
            
            # FIXED: Use v_length from pattern instead of calculating exit based on array bounds
            v_length_dbu = self.dbu(pattern['v_length'])
            
            if pattern['goes_up']:
                exit_y = connect_y + v_length_dbu  # Go up from connection point
                direction = 'UP'
            else:
                exit_y = connect_y - v_length_dbu  # Go down from connection point
                direction = 'DOWN'
            
            # Draw vertical segment
            v_box = db.Box(
                b_end_x - m3_width // 2, min(connect_y, exit_y),
                b_end_x + m3_width // 2, max(connect_y, exit_y)
            )
            array_cell.shapes(self.layers['Metal3']).insert(v_box)
            
            # Add label at exit point
            label = f"G{row}_{col}"
            label_y_offset = self.dbu(0.5)
            label_y = exit_y + label_y_offset if pattern['goes_up'] else exit_y - label_y_offset
            
            self.add_text(array_cell, b_end_x, label_y, label)
            self.debug_info['gate_routes'].append(label)
            
            # Debug info
            print(f"  T[{row},{col}]: offset_y={pattern['offset_y']:.2f}, "
                f"h_len={pattern['h_length']:.2f}, v_len={pattern['v_length']:.2f}, "
                f"exit_y={exit_y * self.layout.dbu:.2f}µm, dir={direction}")
            
            # Verification info
            self.debug_info['pattern_verification'].append({
                'transistor': f"[{row},{col}]",
                'pattern': pattern,
                'gate_pos': (gate_x * self.layout.dbu, gate_y * self.layout.dbu),
                'route_start': (start_x * self.layout.dbu, start_y * self.layout.dbu),
                'exit_point': (b_end_x * self.layout.dbu, exit_y * self.layout.dbu)
            })
            
            routed_count += 1
        
        print(f"✓ Routed {routed_count} gates successfully")
        
        # Print verification summary
        if len(self.debug_info['pattern_verification']) <= 10:
            print("\nPattern verification:")
            for v in self.debug_info['pattern_verification'][:5]:
                print(f"  {v['transistor']}: offset_y={v['pattern']['offset_y']:.2f}, "
                    f"h_len={v['pattern']['h_length']:.2f}, "
                    f"v_len={v['pattern']['v_length']:.2f}, "
                    f"exit_y={v['exit_point'][1]:.2f}µm")
    
    def create_gate_via_stack(self, cell, x, y):
        """Create via stack from Poly to Metal3 at gate position"""
        cont_size = self.dbu(CONT_SIZE)
        via1_size = self.dbu(VIA1_SIZE)
        via2_size = self.dbu(VIA2_SIZE)
        
        # Contact (Poly to M1)
        cont_box = db.Box(
            x - cont_size//2, y - cont_size//2,
            x + cont_size//2, y + cont_size//2
        )
        cell.shapes(self.layers['Cont']).insert(cont_box)
        
        # M1 pad
        m1_pad = cont_box.enlarged(self.dbu(0.05))
        cell.shapes(self.layers['Metal1']).insert(m1_pad)
        
        # Via1 (M1 to M2)
        via1_box = db.Box(
            x - via1_size//2, y - via1_size//2,
            x + via1_size//2, y + via1_size//2
        )
        cell.shapes(self.layers['Via1']).insert(via1_box)
        
        # M2 pad
        m2_pad = via1_box.enlarged(self.dbu(0.05))
        cell.shapes(self.layers['Metal2']).insert(m2_pad)
        
        # Via2 (M2 to M3)
        via2_box = db.Box(
            x - via2_size//2, y - via2_size//2,
            x + via2_size//2, y + via2_size//2
        )
        cell.shapes(self.layers['Via2']).insert(via2_box)
    
    def route_shared_connections(self, array_cell, transistor_info, transistor_type, geom):
        """Route shared S, D, B connections using M1 and M2"""
        print(f"\nRouting shared connections for {transistor_type}...")
        
        bus_width = self.dbu(METAL1_WIDTH * 4)
        bus_width_m2 = self.dbu(METAL2_WIDTH * 4)
        
        array_bbox = array_cell.bbox()
        
        # Source bus (left side vertical) - Metal1
        source_x = array_bbox.left - self.dbu(5)
        source_bus = db.Box(
            source_x - bus_width//2, array_bbox.bottom,
            source_x + bus_width//2, array_bbox.top
        )
        array_cell.shapes(self.layers['Metal1']).insert(source_bus)
        self.add_text(array_cell, source_x - self.dbu(3), array_bbox.center().y, 
                      f"{transistor_type.upper()}_SOURCE")
        
        # Drain bus (right side vertical) - Metal2 
        drain_x = array_bbox.right + self.dbu(5)
        drain_bus = db.Box(
            drain_x - bus_width_m2//2, array_bbox.bottom,
            drain_x + bus_width_m2//2, array_bbox.top
        )
        array_cell.shapes(self.layers['Metal2']).insert(drain_bus)
        self.add_text(array_cell, drain_x + self.dbu(3), array_bbox.center().y,
                      f"{transistor_type.upper()}_DRAIN")
        
        # Bulk bus (bottom horizontal) - Metal1
        bulk_y = array_bbox.bottom - self.dbu(10)
        bulk_bus = db.Box(
            array_bbox.left, bulk_y - bus_width//2,
            array_bbox.right, bulk_y + bus_width//2
        )
        array_cell.shapes(self.layers['Metal1']).insert(bulk_bus)
        
        bulk_label = f"{transistor_type.upper()}_BULK"
        if transistor_type == 'nmos':
            bulk_label += " (substrate/VSS)"
        else:
            bulk_label += " (N-well/VDD)"
        self.add_text(array_cell, array_bbox.center().x, bulk_y - self.dbu(3), bulk_label)
        
        print("✓ Added shared connection buses (S=M1, D=M2, B=M1)")
    
    def add_text(self, cell, x, y, text):
        """Add text label"""
        text_obj = db.Text(text, db.Trans(db.Point(x, y)))
        cell.shapes(self.layers['TEXT']).insert(text_obj)
    
    def add_measurement_pads(self):
        """Add measurement pads"""
        print("\nAdding measurement pads...")
        
        pad_size = self.dbu(PAD_SIZE)
        pad_spacing = self.dbu(60)
        
        bbox = self.top_cell.bbox()
        pad_y = bbox.top + self.dbu(50)
        
        pads = [
            ('VDD', 'Power supply'),
            ('VSS', 'Ground'),
            ('NMOS_S_D_B', 'NMOS shared'),
            ('PMOS_S_D_B', 'PMOS shared'),
            ('GATE_BUS', 'Gate test bus')
        ]
        
        start_x = bbox.center().x - (len(pads) * pad_spacing) // 2
        
        for i, (label, desc) in enumerate(pads):
            x = start_x + i * pad_spacing
            
            pad_box = db.Box(
                x - pad_size//2, pad_y - pad_size//2,
                x + pad_size//2, pad_y + pad_size//2
            )
            self.top_cell.shapes(self.layers['Metal2']).insert(pad_box)
            
            self.add_text(self.top_cell, x, pad_y, label)
            self.add_text(self.top_cell, x, pad_y - pad_size//2 - self.dbu(2), desc)
        
        print(f"✓ Added {len(pads)} measurement pads")
    
    def generate_complete_structure(self, output_file):
        """Generate complete mismatch test structure"""
        print("\n" + "="*60)
        print("GENERATING COMPLETE MISMATCH TEST STRUCTURE")
        print("="*60)
        
        # Print pattern info
        pattern = load_pattern_data()
        print(f"\nUsing pattern with {len(pattern)} transistor entries")
        
        # Create NMOS array
        nmos_array, nmos_info, nmos_geom = self.create_array_with_shared_guardrings('nmos')
        self.route_gate_connections(nmos_array, nmos_info, 'nmos')
        self.route_shared_connections(nmos_array, nmos_info, 'nmos', nmos_geom)
        
        # Create PMOS array
        pmos_array, pmos_info, pmos_geom = self.create_array_with_shared_guardrings('pmos')
        self.route_gate_connections(pmos_array, pmos_info, 'pmos')
        self.route_shared_connections(pmos_array, pmos_info, 'pmos', pmos_geom)
        
        # Place arrays in top cell
        nmos_bbox = nmos_array.bbox()
        pmos_bbox = pmos_array.bbox()
        
        # NMOS on left
        nmos_trans = db.Trans(db.Point(0, 0))
        self.top_cell.insert(db.CellInstArray(nmos_array.cell_index(), nmos_trans))
        
        # PMOS on right
        separation = self.dbu(30)
        pmos_x = nmos_bbox.width() + separation
        pmos_trans = db.Trans(db.Point(pmos_x, 0))
        self.top_cell.insert(db.CellInstArray(pmos_array.cell_index(), pmos_trans))
        
        # Add measurement pads
        self.add_measurement_pads()
        
        # Add title and info
        self.add_design_info()
        
        # Save
        print(f"\nSaving to: {output_file}")
        self.layout.write(output_file)
        
        # Final report
        self.print_final_report()
    
    def add_design_info(self):
        """Add design information text"""
        bbox = self.top_cell.bbox()
        
        title_y = bbox.top + self.dbu(70)
        title = f"Mismatch Test Array {ARRAY_SIZE}x{ARRAY_SIZE} - W={TRANSISTOR_W}µm L={TRANSISTOR_L}µm"
        self.add_text(self.top_cell, bbox.center().x, title_y, title)
        
        info_y = title_y - self.dbu(3)
        info = "Shared guardrings | S/D/B shared | Gates independent | Pattern from GUI"
        self.add_text(self.top_cell, bbox.center().x, info_y, info)
    
    def print_final_report(self):
        """Print final summary report"""
        bbox = self.top_cell.bbox()
        total_area = bbox.width() * bbox.height() / 1e6
        
        print("\n" + "="*60)
        print("FINAL REPORT - STRUCTURE GENERATED SUCCESSFULLY")
        print("="*60)
        print(f"\nDimensions:")
        print(f"  Total area: {total_area:.0f} µm²")
        print(f"  Chip size: {bbox.width()/1000:.1f} x {bbox.height()/1000:.1f} µm")
        
        print(f"\nTransistor count:")
        print(f"  Active: {self.debug_info['transistor_count']}")
        print(f"  Dummy: {self.debug_info['dummy_count']}")
        print(f"  Total: {self.debug_info['transistor_count'] + self.debug_info['dummy_count']}")
        
        print(f"\nGate connections routed: {len(self.debug_info['gate_routes'])}")
        if len(self.debug_info['gate_routes']) <= 20:
            print(f"  Gates: {', '.join(self.debug_info['gate_routes'])}")
        
        print(f"\nKey features:")
        print(f"  ✓ Shared guardring borders")
        print(f"  ✓ Non-overlapping gate routing (Metal3)")
        print(f"  ✓ Pattern loaded from external source")
        print(f"  ✓ Manhattan routing (H→V segments)")
        print(f"  ✓ Dimensions matched to GUI")
        print(f"  ✓ Upper half gates exit top")
        print(f"  ✓ Lower half gates exit bottom")
        print(f"  ✓ Dummies on sides only")
        print(f"  ✓ M1/M2 for S/D/B, M3 for gates")
        print("="*60)

def main():
    """Main function"""
    
    # Output file
    try:
        output
    except NameError:
        output = "mismatch_array_4x4_from_gui.gds"
    
    print(f"Output file: {output}")
    
    # Generate structure
    generator = MismatchArray4x4()
    generator.generate_complete_structure(output)
    
    print(f"\nTo view the result:")
    print(f"  klayout {output}")
    print("\nNext steps:")
    print("  1. Verify gate routing matches GUI pattern")
    print("  2. Check dimensions match GUI (pitch, spacing)")
    print("  3. Run DRC checks")
    print("  4. Test with different patterns from GUI")

if __name__ == "__main__":
    main()