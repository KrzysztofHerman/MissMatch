#!/usr/bin/env python3
"""
SCALABLE MISMATCH ARRAY GENERATOR - NMOS AND PMOS SUPPORT
Configurable dimensions.

author: Mauricio Montanares
"""

import pya
import klayout.db as db
import sys
import json

# ========== SCALABLE CONFIGURATION ==========
# These values should match what's configured in the GUI

# Default transistor dimensions (will be overridden if pattern file contains them)
TRANSISTOR_W = 1.03      # µm - Width (configurable)
TRANSISTOR_L = 0.35      # µm - Length (configurable)
TRANSISTOR_NG = 1        # Number of fingers

# Spacing parameters (µm)
GUARDRING_WIDTH = 0.5       # Guardring width
GUARDRING_SPACING = 2.0     # Distance from transistor to guardring (configurable, default 2µm)

# Array size (will be read from pattern file)
ARRAY_SIZE = 4              # Default 4x4 array

# Design rules IHP SG13G2
METAL1_WIDTH = 0.28
METAL2_WIDTH = 0.36
METAL3_WIDTH = 0.20
POLY_WIDTH = 0.13
VIA1_SIZE = 0.19
VIA2_SIZE = 0.19
CONT_SIZE = 0.22
CONT_SPACING = 0.40
PAD_SIZE = 50.0

TOPMETAL1_WIDTH = 2    
TOPMETAL2_WIDTH = 2.00    
TOPVIA1_SIZE = 0.42       
TOPVIA2_SIZE = 0.90       

TOPMETAL1_MIN_SPACING = 1.64  # Minimum spacing between TM1 lines

# PDK
LIB_NAME = 'SG13_dev'

# Layers
LAYER_MAP = {
    'Activ':    (1, 0),   # Active area
    'GatPoly':  (5, 0),   # Gate poly
    'Cont':     (6, 0),   # Contact (not "locint" as in IHP script)
    'nSD':      (7, 0),   # N+ implant
    'Metal1':   (8, 0),   # Metal 1
    'Metal2':   (10, 0),  # Metal 2
    'Metal3':   (30, 0),  # Metal 3
    'pSD':      (14, 0),  # P+ implant
    'Via1':     (19, 0),  # Via 1
    'Via2':     (29, 0),  # Via 2
    'NWell':    (31, 0),  # N-well
    'Via3':     (49, 0),  # Via 3 (M3-M4) - CORRECTED
    'Metal4':   (50, 0),  # Metal 4 - CORRECTED
    'Via4':     (66, 0),  # Via 4 (M4-M5) - CORRECTED
    'Metal5':   (67, 0),  # Metal 5 - CORRECTED
    # Ptap and Ntap are NOT used by IHP for guard rings!
    # 'Ptap':     (32, 0),  # Not used
    # 'Ntap':     (33, 0),  # Not used
    'TEXT':     (63, 0),  # Text layer
    'TopVia1':  (125, 0),
    'TopMetal1':(126, 0),
    'TopVia2':  (133, 0),
    'TopMetal2':(134, 0),
}

def get_default_pattern():
    """Return default pattern if no pattern file is found"""
    return {}

def load_pattern_and_config():
    """Load pattern and extract configuration if available - Phase 2 & 3 version"""
    global TRANSISTOR_W, TRANSISTOR_L, GUARDRING_SPACING, ARRAY_SIZE
    
    # Initialize return data
    full_data = {
        'pattern_data': {},
        'metadata': {}
    }
    
    # Determine which pattern file to load
    pattern_file = 'temp_pattern_nmos.json'  # Default file
    
    # Check for KLayout -rd arguments (they come as global variables without $)
    try:
        if 'pattern_file' in globals():
            pattern_file = globals()['pattern_file']
            print(f"Pattern file specified via -rd: {pattern_file}")
    except:
        pass
    
    # Alternative: check environment or sys.argv
    import sys
    import os
    
    # Check if running in KLayout with environment variable
    if 'KLAYOUT_PATTERN_FILE' in os.environ:
        pattern_file = os.environ['KLAYOUT_PATTERN_FILE']
    
    # Try to load pattern file
    try:
        with open(pattern_file, 'r') as f:
            data = json.load(f)
            full_data = data
            print(f"✓ Loaded pattern file: {pattern_file}")
    except FileNotFoundError:
        print(f"⚠ Pattern file '{pattern_file}' not found, using defaults")
    except json.JSONDecodeError as e:
        print(f"⚠ Error parsing JSON in '{pattern_file}': {e}")
    except Exception as e:
        print(f"⚠ Could not load '{pattern_file}': {e}")
    
    # Extract config from metadata
    config = full_data.get('metadata', {})
    
    # Apply configuration if available
    if config:
        if 'transistor_W' in config:
            TRANSISTOR_W = config['transistor_W']
            print(f"✓ Loaded W={TRANSISTOR_W}µm from pattern file")
        
        if 'transistor_L' in config:
            TRANSISTOR_L = config['transistor_L']
            print(f"✓ Loaded L={TRANSISTOR_L}µm from pattern file")
        
        if 'guardring_spacing' in config:
            GUARDRING_SPACING = config['guardring_spacing']
            print(f"✓ Loaded guardring_spacing={GUARDRING_SPACING}µm from pattern file")
        
        if 'array_rows' in config:
            ARRAY_SIZE = config['array_rows']
            print(f"✓ Loaded array_size={ARRAY_SIZE}x{ARRAY_SIZE} from pattern file")
        
        # Phase 2: Handle dummy mode
        if 'dummy_mode' in config:
            print(f"✓ Dummy mode: {config['dummy_mode']}")
        elif 'has_dummies' in config:
            # Backward compatibility
            dummy_mode = 'sides' if config['has_dummies'] else 'none'
            config['dummy_mode'] = dummy_mode
            print(f"✓ Converted has_dummies to dummy_mode: {dummy_mode}")
        
        if 'device_type' in config:
            print(f"✓ Device type: {config['device_type']}")
    
    # Convert pattern keys from strings to tuples
    pattern_data = full_data.get('pattern_data', {})
    if pattern_data:
        pattern = {}
        for str_key, value in pattern_data.items():
            if isinstance(str_key, str) and ',' in str_key:
                row, col = map(int, str_key.split(','))
                pattern[(row, col)] = value
            else:
                pattern[str_key] = value
        full_data['pattern_data'] = pattern
    
    return full_data

class ScalableMismatchArray:
    """Scalable mismatch array generator - NMOS and PMOS support"""
    
    def __init__(self):
        print("\n" + "="*60)
        print("SCALABLE MISMATCH ARRAY GENERATOR")
        print("="*60)
        
        # Load configuration and pattern
        self.full_data = load_pattern_and_config()
        self.pattern_data = self.full_data.get('pattern_data', {})
        self.metadata = self.full_data.get('metadata', {})
        self.device_type = self.metadata.get('device_type', 'nmos')
        self.dummy_mode = self.metadata.get('dummy_mode', 'sides')
        
        # Display current configuration
        print(f"\nConfiguration:")
        print(f"  Device Type: {self.device_type}")
        print(f"  Dummy Mode: {self.dummy_mode}")
        print(f"  Transistor W: {TRANSISTOR_W} µm")
        print(f"  Transistor L: {TRANSISTOR_L} µm")
        print(f"  Array size: {ARRAY_SIZE}x{ARRAY_SIZE}")
        
        # Calculate pitches
        self.calculate_pitches()
        
        # Load library
        self.lib = pya.Library.library_by_name(LIB_NAME)
        if not self.lib:
            raise Exception(f"Library {LIB_NAME} not found")
        
        # Create layout
        self.layout = db.Layout(True)
        self.layout.dbu = 0.001  # 1nm
        
        # Create top cell with appropriate name
        if self.device_type == 'both':
            cell_name = f'MismatchArray_{ARRAY_SIZE}x{ARRAY_SIZE}_BOTH'
        elif self.device_type == 'pmos':
            cell_name = f'MismatchArray_{ARRAY_SIZE}x{ARRAY_SIZE}_PMOS'
        else:
            cell_name = f'MismatchArray_{ARRAY_SIZE}x{ARRAY_SIZE}_NMOS'
        
        self.top_cell = self.layout.create_cell(cell_name)
        
        # Create layer indices
        self.layers = {}
        for name, (layer, datatype) in LAYER_MAP.items():
            self.layers[name] = self.layout.layer(layer, datatype)
        
        print(f"✓ Layout initialized")
        
        # Debug tracking
        self.debug_info = {
            'transistor_count': 0,
            'dummy_count': 0,
            'gate_routes': [],
            'pattern_verification': []
        }
    
    def analyze_transistor_terminals(self, transistor_cell):
        """
        Analyze transistor PCell to find actual terminal positions and transistor boundaries
        """
        print("\n  Analyzing transistor terminals...")
        
        # Get transistor bbox
        t_bbox = transistor_cell.bbox()
        
        terminals = {
            # Transistor boundaries (in database units)
            'bbox_left': t_bbox.left,
            'bbox_right': t_bbox.right,
            'bbox_top': t_bbox.top,
            'bbox_bottom': t_bbox.bottom,
            'bbox_width': t_bbox.width(),
            'bbox_height': t_bbox.height(),
            
            # Terminal positions (will be filled)
            'drain_left_edge': None,
            'drain_right_edge': None,
            'drain_center': None,
            'source_left_edge': None,
            'source_right_edge': None,
            'source_center': None,
            'gate_center': t_bbox.center().x,
            'transistor_center': t_bbox.center().x,
            
            # CRITICAL: Find actual GatPoly edges
            'poly_top_edge': None,      # Top edge of actual poly
            'poly_bottom_edge': None,    # Bottom edge of actual poly
            'poly_center_x': None        # Center X of poly
        }
        
        # Find actual GatPoly boundaries
        poly_top = -float('inf')
        poly_bottom = float('inf')
        poly_center_x = t_bbox.center().x
        
        # Scan all GatPoly shapes to find the actual edges
        for shape in transistor_cell.shapes(self.layers['GatPoly']).each():
            if shape.is_box():
                box = shape.box
                # Find the topmost edge of any poly shape
                if box.top > poly_top:
                    poly_top = box.top
                # Find the bottommost edge
                if box.bottom < poly_bottom:
                    poly_bottom = box.bottom
                poly_center_x = box.center().x
        
        # Store the actual poly edges
        if poly_top != -float('inf'):
            terminals['poly_top_edge'] = poly_top
            terminals['poly_bottom_edge'] = poly_bottom
            terminals['poly_center_x'] = poly_center_x
            
            print(f"    Actual GatPoly edges found:")
            print(f"      Top edge: {poly_top*self.layout.dbu:.3f}μm from origin")
            print(f"      Bottom edge: {poly_bottom*self.layout.dbu:.3f}μm from origin")
            print(f"      Bbox vs Poly top gap: {(t_bbox.top - poly_top)*self.layout.dbu:.3f}μm")
        else:
            print(f"    WARNING: Could not find GatPoly shapes!")
            # Fallback: estimate based on typical gap
            terminals['poly_top_edge'] = t_bbox.top - self.dbu(0.14)
            terminals['poly_bottom_edge'] = t_bbox.bottom + self.dbu(0.14)
        
        # Find Metal1 shapes for drain/source (existing code)
        metal1_shapes = []
        for shape in transistor_cell.shapes(self.layers['Metal1']).each():
            if shape.is_box():
                box = shape.box
                metal1_shapes.append({
                    'left': box.left,
                    'right': box.right,
                    'top': box.top,
                    'bottom': box.bottom,
                    'center_x': box.center().x,
                    'center_y': box.center().y,
                    'width': box.width(),
                    'height': box.height()
                })
        
        # Identify drain (leftmost M1) and source (rightmost M1)
        if metal1_shapes:
            # Sort by center X position
            metal1_shapes.sort(key=lambda s: s['center_x'])
            
            # Leftmost M1 is drain
            drain_shape = metal1_shapes[0]
            terminals['drain_left_edge'] = drain_shape['left']
            terminals['drain_right_edge'] = drain_shape['right']
            terminals['drain_center'] = drain_shape['center_x']
            terminals['drain_top'] = drain_shape['top']
            terminals['drain_bottom'] = drain_shape['bottom']
            
            # Rightmost M1 is source
            source_shape = metal1_shapes[-1]
            terminals['source_left_edge'] = source_shape['left']
            terminals['source_right_edge'] = source_shape['right']
            terminals['source_center'] = source_shape['center_x']
            terminals['source_top'] = source_shape['top']
            terminals['source_bottom'] = source_shape['bottom']
            
            print(f"    Transistor bbox: width={t_bbox.width()*self.layout.dbu:.3f}µm, height={t_bbox.height()*self.layout.dbu:.3f}µm")
            print(f"    Drain M1: x={drain_shape['center_x']*self.layout.dbu:.3f}µm")
            print(f"    Source M1: x={source_shape['center_x']*self.layout.dbu:.3f}µm")
        
        # Fallback if detection failed
        if terminals['drain_left_edge'] is None:
            # Estimate positions
            terminals['drain_center'] = t_bbox.center().x - t_bbox.width() * 0.3
            terminals['drain_left_edge'] = terminals['drain_center'] - self.dbu(0.14)
            terminals['drain_right_edge'] = terminals['drain_center'] + self.dbu(0.14)
            print(f"    Using fallback positions")
        
        return terminals

    def calculate_pitches(self):
        """Calculate pitches based on transistor dimensions and spacing"""
        # Get actual transistor bbox size (this is approximate)
        # The actual size will be determined when we create the PCell
        estimated_t_width = TRANSISTOR_W
        estimated_t_height = TRANSISTOR_L * 4  # Approximate height
        
        # Calculate pitches
        # Pitch = transistor_dimension + 2*spacing + guardring_width
        self.pitch_x = estimated_t_width + 2 * GUARDRING_SPACING + GUARDRING_WIDTH
        self.pitch_y = estimated_t_height + 2 * GUARDRING_SPACING + GUARDRING_WIDTH
        
        print(f"  Calculated pitch X: {self.pitch_x:.3f} µm")
        print(f"  Calculated pitch Y: {self.pitch_y:.3f} µm")
    
    def dbu(self, value_um):
        """Convert µm to database units"""
        return int(value_um / self.layout.dbu)
    
    def create_transistor_pcell(self, transistor_type='nmos'):
        """Create transistor PCell - FIXED to accept type parameter"""
        pcell_name = transistor_type
        
        # Find PCell declaration
        pcell_decl = self.lib.layout().pcell_declaration(pcell_name)
        if not pcell_decl:
            print(f"\n⚠ PCell '{pcell_name}' not found")
            print("Available PCells in library:")
            for i in range(self.lib.layout().pcells()):
                pd = self.lib.layout().pcell_declaration(i)
                if pd:
                    print(f"  - {pd.name()}")
            raise Exception(f"PCell {pcell_name} not found in library {LIB_NAME}")
        
        # Parameters for PCell
        params = {
            'w': f'{TRANSISTOR_W}u',
            'l': f'{TRANSISTOR_L}u',
            'ng': str(TRANSISTOR_NG)
        }
        
        # Create PCell instance
        return self.layout.add_pcell_variant(self.lib, pcell_decl.id(), params)

    def enhance_guardring_with_bulk_connection(self, array_cell, geom, rows, cols):
        """
        Add contacts to guardring with IMPROVED SPACING and NO INTERSECTIONS
        - 50% more spacing (0.60µm instead of 0.40µm)
        - No contacts at cross points, T-junctions, or any multi-line intersections
        """
        gr_width = geom['gr_width']
        
        # Contact parameters - INCREASED SPACING
        cont_size = self.dbu(0.22)
        cont_spacing = self.dbu(0.60)  # INCREASED 50% from 0.40 to 0.60µm
        cont_pitch = cont_size + cont_spacing  # Now 0.82µm pitch
        m1_enc = self.dbu(0.06)  # Metal1 enclosure
        
        # Define exclusion zone around intersections
        exclusion_radius = self.dbu(0.5)  # 0.5µm exclusion radius around intersections
        
        print("\n  Adding improved contacts to guardring...")
        print(f"    Contact pitch: {cont_pitch*self.layout.dbu:.3f}µm (50% increased)")
        print(f"    Avoiding all intersections (cross, T-junctions)")
        
        contacts_added = 0
        
        # Calculate intersection points to avoid
        intersection_points = []
        
        # All cross points (4-way intersections)
        for row in range(rows + 1):
            for col in range(cols + 1):
                x_int = col * geom['pitch_x'] + gr_width // 2
                y_int = row * geom['pitch_y'] + gr_width // 2
                intersection_points.append((x_int, y_int))
        
        # Helper function to check if a point is too close to any intersection
        def is_near_intersection(x, y):
            for int_x, int_y in intersection_points:
                dist_x = abs(x - int_x)
                dist_y = abs(y - int_y)
                if dist_x < exclusion_radius and dist_y < exclusion_radius:
                    return True
            return False
        
        # VERTICAL STRIPES - contacts along vertical lines, avoiding intersections
        for col in range(cols + 1):
            x_center = col * geom['pitch_x'] + gr_width // 2
            
            # For each vertical segment between intersections
            for row_segment in range(rows + 1):
                if row_segment == 0:
                    # Bottom segment
                    y_start = 0
                    y_end = geom['pitch_y'] - exclusion_radius
                elif row_segment == rows:
                    # Top segment
                    y_start = row_segment * geom['pitch_y'] + gr_width + exclusion_radius
                    y_end = geom['total_height']
                else:
                    # Middle segments
                    y_start = row_segment * geom['pitch_y'] + gr_width + exclusion_radius
                    y_end = (row_segment + 1) * geom['pitch_y'] - exclusion_radius
                
                # Place contacts in this segment
                segment_length = y_end - y_start
                if segment_length > cont_size:
                    num_contacts = int((segment_length - cont_size) / cont_pitch) + 1
                    
                    # Adjust spacing to distribute evenly in segment
                    if num_contacts > 1:
                        actual_pitch = (segment_length - cont_size) / (num_contacts - 1)
                    else:
                        actual_pitch = 0
                    
                    for i in range(num_contacts):
                        if num_contacts == 1:
                            y = y_start + segment_length / 2
                        else:
                            y = y_start + cont_size/2 + i * actual_pitch
                        
                        # Double-check we're not near an intersection
                        if not is_near_intersection(x_center, y):
                            # Contact
                            cont_box = db.Box(
                                x_center - cont_size//2, y - cont_size//2,
                                x_center + cont_size//2, y + cont_size//2
                            )
                            array_cell.shapes(self.layers['Cont']).insert(cont_box)
                            
                            # M1 with enclosure
                            m1_box = cont_box.enlarged(m1_enc)
                            array_cell.shapes(self.layers['Metal1']).insert(m1_box)
                            contacts_added += 1
        
        # HORIZONTAL STRIPES - contacts along horizontal lines, avoiding intersections
        for row in range(rows + 1):
            y_center = row * geom['pitch_y'] + gr_width // 2
            
            # For each horizontal segment between intersections
            for col_segment in range(cols + 1):
                if col_segment == 0:
                    # Left segment
                    x_start = 0
                    x_end = geom['pitch_x'] - exclusion_radius
                elif col_segment == cols:
                    # Right segment
                    x_start = col_segment * geom['pitch_x'] + gr_width + exclusion_radius
                    x_end = geom['total_width']
                else:
                    # Middle segments
                    x_start = col_segment * geom['pitch_x'] + gr_width + exclusion_radius
                    x_end = (col_segment + 1) * geom['pitch_x'] - exclusion_radius
                
                # Place contacts in this segment
                segment_length = x_end - x_start
                if segment_length > cont_size:
                    num_contacts = int((segment_length - cont_size) / cont_pitch) + 1
                    
                    # Adjust spacing to distribute evenly in segment
                    if num_contacts > 1:
                        actual_pitch = (segment_length - cont_size) / (num_contacts - 1)
                    else:
                        actual_pitch = 0
                    
                    for i in range(num_contacts):
                        if num_contacts == 1:
                            x = x_start + segment_length / 2
                        else:
                            x = x_start + cont_size/2 + i * actual_pitch
                        
                        # Double-check we're not near an intersection
                        if not is_near_intersection(x, y_center):
                            # Contact
                            cont_box = db.Box(
                                x - cont_size//2, y_center - cont_size//2,
                                x + cont_size//2, y_center + cont_size//2
                            )
                            array_cell.shapes(self.layers['Cont']).insert(cont_box)
                            
                            # M1 with enclosure
                            m1_box = cont_box.enlarged(m1_enc)
                            array_cell.shapes(self.layers['Metal1']).insert(m1_box)
                            contacts_added += 1
        
        print(f"    ✓ Added {contacts_added} contacts (no intersections)")
        print(f"    ✓ Excluded {(rows+1)*(cols+1)} intersection points")
        
        # Add bulk connection at top-right corner
        self.add_bulk_connection_corner(array_cell, geom, rows, cols)

    def calculate_shared_guardring_array(self, transistor_bbox, rows, cols):
        """Calculate dimensions for array with shared guardrings"""
        
        # Get actual transistor dimensions
        actual_t_width = transistor_bbox.width() * self.layout.dbu
        actual_t_height = transistor_bbox.height() * self.layout.dbu
        
        print(f"\nActual transistor dimensions:")
        print(f"  Width: {actual_t_width:.3f} µm")
        print(f"  Height: {actual_t_height:.3f} µm")
        
        # Recalculate pitches with actual dimensions
        pitch_x = self.dbu(actual_t_width + 2 * GUARDRING_SPACING + GUARDRING_WIDTH)
        pitch_y = self.dbu(actual_t_height + 2 * GUARDRING_SPACING + GUARDRING_WIDTH)
        
        print(f"  Final pitch X: {pitch_x * self.layout.dbu:.3f} µm")
        print(f"  Final pitch Y: {pitch_y * self.layout.dbu:.3f} µm")
        
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
            'cell_inner_height': cell_inner_height,
            't_width': transistor_bbox.width(),
            't_height': transistor_bbox.height()
        }
    
    def create_shared_guardring_structure(self, array_cell, geom, rows, cols):
        """
        Create shared guardring structure for NMOS array
        NO contacts at intersections - only Activ/pSD/Metal1 layers
        """
        print("\nCreating shared guardring structure for NMOS (IHP-compliant)...")
        
        gr_width = geom['gr_width']
        
        # For NMOS array: p-type substrate contact
        # Based on IHP script: uses pSD + Activ (NO Ptap!)
        
        # Create vertical guardring stripes
        for col in range(cols + 1):
            x = col * geom['pitch_x']
            stripe_box = db.Box(
                x, 0,
                x + gr_width, geom['total_height']
            )
            
            # Active area (required for guard ring)
            array_cell.shapes(self.layers['Activ']).insert(stripe_box)
            
            # P+ implant for substrate contact (pSD layer)
            array_cell.shapes(self.layers['pSD']).insert(stripe_box)
        
        # Create horizontal guardring stripes
        for row in range(rows + 1):
            y = row * geom['pitch_y']
            stripe_box = db.Box(
                0, y,
                geom['total_width'], y + gr_width
            )
            
            # Active area
            array_cell.shapes(self.layers['Activ']).insert(stripe_box)
            
            # P+ implant for substrate contact
            array_cell.shapes(self.layers['pSD']).insert(stripe_box)
        
        # Add Metal1 at intersections for connectivity (but NO contacts)
        m1_size = self.dbu(0.4)  # Larger M1 pad at intersections
        
        for row in range(rows + 1):
            for col in range(cols + 1):
                # Center of guardring intersection
                x_center = col * geom['pitch_x'] + gr_width // 2
                y_center = row * geom['pitch_y'] + gr_width // 2
                
                # Metal1 pad at intersection (NO Contact underneath)
                m1_box = db.Box(
                    x_center - m1_size//2,
                    y_center - m1_size//2,
                    x_center + m1_size//2,
                    y_center + m1_size//2
                )
                array_cell.shapes(self.layers['Metal1']).insert(m1_box)
        
        print(f"✓ Created substrate contact guardring: {cols+1} x {rows+1} stripes")
        print(f"  Layers used: Activ, pSD, Metal1")
        print(f"  M1 pads at intersections for connectivity (no contacts)")
        
        # Now add contacts with improved spacing, avoiding intersections
        self.enhance_guardring_with_bulk_connection(array_cell, geom, rows, cols)

    def create_shared_guardring_structure_pmos(self, array_cell, geom, rows, cols):
        """
        Create N-well guardring for PMOS - CORRECT IHP IMPLEMENTATION
        NO contacts at intersections - only Activ/nSD/NWell/Metal1 layers
        """
        print("\nCreating N-well guardring structure for PMOS (IHP-compliant)...")
        
        gr_width = geom['gr_width']
        
        # First create N-well for entire PMOS array
        nwell_margin = self.dbu(0.5)
        nwell_box = db.Box(
            -nwell_margin, 
            -nwell_margin,
            geom['total_width'] + nwell_margin,
            geom['total_height'] + nwell_margin
        )
        array_cell.shapes(self.layers['NWell']).insert(nwell_box)
        
        # Create guardring stripes (N-well contact)
        for col in range(cols + 1):
            x = col * geom['pitch_x']
            stripe_box = db.Box(
                x, 0,
                x + gr_width, geom['total_height']
            )
            
            # Active area
            array_cell.shapes(self.layers['Activ']).insert(stripe_box)
            
            # N+ implant for N-well contact (nSD layer)
            array_cell.shapes(self.layers['nSD']).insert(stripe_box)
        
        # Horizontal stripes
        for row in range(rows + 1):
            y = row * geom['pitch_y']
            stripe_box = db.Box(
                0, y,
                geom['total_width'], y + gr_width
            )
            
            array_cell.shapes(self.layers['Activ']).insert(stripe_box)
            array_cell.shapes(self.layers['nSD']).insert(stripe_box)
        
        # Add Metal1 at intersections for connectivity (but NO contacts)
        m1_size = self.dbu(0.4)  # Larger M1 pad at intersections
        
        for row in range(rows + 1):
            for col in range(cols + 1):
                x_center = col * geom['pitch_x'] + gr_width // 2
                y_center = row * geom['pitch_y'] + gr_width // 2
                
                # Metal1 pad at intersection (NO Contact underneath)
                m1_box = db.Box(
                    x_center - m1_size//2,
                    y_center - m1_size//2,
                    x_center + m1_size//2,
                    y_center + m1_size//2
                )
                array_cell.shapes(self.layers['Metal1']).insert(m1_box)
        
        print(f"✓ Created N-well contact guardring: {cols+1} x {rows+1} stripes")
        print(f"  Layers used: NWell, Activ, nSD, Metal1")
        print(f"  M1 pads at intersections for connectivity (no contacts)")
        
        # Now add contacts with improved spacing, avoiding intersections
        self.enhance_guardring_with_bulk_connection(array_cell, geom, rows, cols)

    def add_bulk_connection_corner(self, array_cell, geom, rows, cols):
        """
        Add bulk connection ONLY at top-right corner of guardring
        For NMOS: connects P-substrate to VSS (VBULK_NMOS)
        For PMOS: connects N-well to VDD (VBULK_PMOS)
        """
        print("  Adding bulk connection at top-right corner...")
        
        # Top-right corner position
        corner_x = cols * geom['pitch_x'] + geom['gr_width'] // 2
        corner_y = rows * geom['pitch_y'] + geom['gr_width'] // 2
        
        # Via1 (M1 to M2)
        via1_size = self.dbu(VIA1_SIZE)
        via1_box = db.Box(
            corner_x - via1_size//2, corner_y - via1_size//2,
            corner_x + via1_size//2, corner_y + via1_size//2
        )
        array_cell.shapes(self.layers['Via1']).insert(via1_box)
        
        # M2 pad
        m2_size = self.dbu(METAL2_WIDTH)
        m2_pad = db.Box(
            corner_x - m2_size//2, corner_y - m2_size//2,
            corner_x + m2_size//2, corner_y + m2_size//2
        )
        array_cell.shapes(self.layers['Metal2']).insert(m2_pad)
        
        # Via2 (M2 to M3)
        via2_size = self.dbu(VIA2_SIZE)
        via2_box = db.Box(
            corner_x - via2_size//2, corner_y - via2_size//2,
            corner_x + via2_size//2, corner_y + via2_size//2
        )
        array_cell.shapes(self.layers['Via2']).insert(via2_box)
        
        # M3 pad
        m3_size = self.dbu(METAL3_WIDTH)
        m3_pad = db.Box(
            corner_x - m3_size//2, corner_y - m3_size//2,
            corner_x + m3_size//2, corner_y + m3_size//2
        )
        array_cell.shapes(self.layers['Metal3']).insert(m3_pad)
        
        # Via3 (M3 to M4)
        via3_size = self.dbu(0.19)
        via3_box = db.Box(
            corner_x - via3_size//2, corner_y - via3_size//2,
            corner_x + via3_size//2, corner_y + via3_size//2
        )
        array_cell.shapes(self.layers['Via3']).insert(via3_box)
        
        # M4 routing - extend 1.5μm beyond guardring
        m4_width = self.dbu(0.4)
        extension = self.dbu(1.5)
        
        # M4 horizontal extension to the right
        m4_h_box = db.Box(
            corner_x - m4_width//2,
            corner_y - m4_width//2,
            corner_x + extension,
            corner_y + m4_width//2
        )
        array_cell.shapes(self.layers['Metal4']).insert(m4_h_box)
        
        # M4 vertical extension upward
        m4_v_box = db.Box(
            corner_x - m4_width//2,
            corner_y - m4_width//2,
            corner_x + m4_width//2,
            corner_y + extension
        )
        array_cell.shapes(self.layers['Metal4']).insert(m4_v_box)
        
        # Add label
        if self.device_type == 'pmos':
            label = "VBULK_PMOS"
        else:
            label = "VBULK_NMOS"
        
        self.add_text(array_cell, corner_x + extension, corner_y, label)
        self.add_text(array_cell, corner_x, corner_y + extension, label)
        
        print(f"    ✓ Added bulk connection: {label} at top-right corner")

    def create_nmos_array(self):
        """Create NMOS array with configurable dummy arrangement - Phase 2"""
        print(f"\n{'='*60}")
        print(f"Creating NMOS array {ARRAY_SIZE}x{ARRAY_SIZE}")
        print(f"{'='*60}")
        
        array_cell = self.layout.create_cell(f'nmos_array_{ARRAY_SIZE}x{ARRAY_SIZE}')
        
        # Get dummy mode from metadata
        dummy_mode = self.metadata.get('dummy_mode', 'sides')
        print(f"  Dummy mode: {dummy_mode}")
        
        # Calculate total dimensions based on dummy mode
        if dummy_mode == 'none':
            total_rows = ARRAY_SIZE
            total_cols = ARRAY_SIZE
        elif dummy_mode == 'sides':
            total_rows = ARRAY_SIZE
            total_cols = ARRAY_SIZE + 2
        else:  # full ring
            total_rows = ARRAY_SIZE + 2
            total_cols = ARRAY_SIZE + 2
        
        print(f"  Total array dimensions: {total_rows}x{total_cols}")
        print(f"  Active array: {ARRAY_SIZE}x{ARRAY_SIZE}")
        
        # Create transistor PCell
        transistor_pcell = self.create_transistor_pcell('nmos')
        transistor_cell = self.layout.cell(transistor_pcell)
        t_bbox = transistor_cell.bbox()
        
        geom = self.calculate_shared_guardring_array(t_bbox, total_rows, total_cols)
        
        # Create guardring structure
        self.create_shared_guardring_structure(array_cell, geom, total_rows, total_cols)
        
        # Place transistors
        transistor_info = []
        active_count = 0
        dummy_count = 0
        
        for row in range(total_rows):
            for col in range(total_cols):
                # Determine if dummy based on mode
                is_dummy = False
                
                if dummy_mode == 'sides':
                    is_dummy = (col == 0 or col == total_cols-1)
                elif dummy_mode == 'full':
                    is_dummy = (row == 0 or row == total_rows-1 or 
                            col == 0 or col == total_cols-1)
                
                # Calculate center position
                cell_center_x = col * geom['pitch_x'] + geom['gr_width'] + geom['cell_inner_width'] // 2
                cell_center_y = row * geom['pitch_y'] + geom['gr_width'] + geom['cell_inner_height'] // 2
                
                # Position transistor
                bbox_center_x = t_bbox.center().x
                bbox_center_y = t_bbox.center().y
                
                trans_x = cell_center_x - bbox_center_x
                trans_y = cell_center_y - bbox_center_y
                
                trans = db.Trans(db.Point(trans_x, trans_y))
                array_cell.insert(db.CellInstArray(transistor_pcell, trans))
                
                # Calculate active indices
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
                
                info = {
                    'row': row,
                    'col': col,
                    'active_row': active_row,
                    'active_col': active_col,
                    'x': cell_center_x,
                    'y': cell_center_y,
                    'is_dummy': is_dummy,
                    'gate_x': cell_center_x * self.layout.dbu,
                    'gate_y': cell_center_y * self.layout.dbu
                }
                
                transistor_info.append(info)
                
                if is_dummy:
                    dummy_count += 1
                    self.debug_info['dummy_count'] += 1
                else:
                    active_count += 1
                    self.debug_info['transistor_count'] += 1
        
        print(f"✓ Placed {active_count} active + {dummy_count} dummy transistors")

        if dummy_count > 0:
            self.connect_dummies_to_vss(array_cell, transistor_info, geom)
        
        if dummy_mode == 'full':
            print(f"Full dummy ring: top/bottom/left/right borders")
        elif dummy_mode == 'sides':
            print(f"Side dummies only: left/right columns")
        else:
            print(f"No dummy transistors")
        
        return array_cell, transistor_info, geom

    def create_pmos_array(self):
        """Create PMOS array with configurable dummy arrangement - Phase 2"""
        print(f"\n{'='*60}")
        print(f"Creating PMOS array {ARRAY_SIZE}x{ARRAY_SIZE}")
        print(f"{'='*60}")
        
        array_cell = self.layout.create_cell(f'pmos_array_{ARRAY_SIZE}x{ARRAY_SIZE}')
        
        # Get dummy mode from metadata
        dummy_mode = self.metadata.get('dummy_mode', 'sides')
        print(f"  Dummy mode: {dummy_mode}")
        
        # Calculate total dimensions based on dummy mode
        if dummy_mode == 'none':
            total_rows = ARRAY_SIZE
            total_cols = ARRAY_SIZE
        elif dummy_mode == 'sides':
            total_rows = ARRAY_SIZE
            total_cols = ARRAY_SIZE + 2
        else:  # full ring
            total_rows = ARRAY_SIZE + 2
            total_cols = ARRAY_SIZE + 2
        
        # Create PMOS transistor PCell
        transistor_pcell = self.create_transistor_pcell('pmos')
        transistor_cell = self.layout.cell(transistor_pcell)
        t_bbox = transistor_cell.bbox()
        
        geom = self.calculate_shared_guardring_array(t_bbox, total_rows, total_cols)
        
        # Create N-well guardring structure for PMOS
        self.create_shared_guardring_structure_pmos(array_cell, geom, total_rows, total_cols)
        
        # Place transistors (same logic as NMOS)
        transistor_info = []
        active_count = 0
        dummy_count = 0
        
        for row in range(total_rows):
            for col in range(total_cols):
                # Determine if dummy based on mode
                is_dummy = False
                
                if dummy_mode == 'sides':
                    is_dummy = (col == 0 or col == total_cols-1)
                elif dummy_mode == 'full':
                    is_dummy = (row == 0 or row == total_rows-1 or 
                            col == 0 or col == total_cols-1)
                
                # Calculate center position
                cell_center_x = col * geom['pitch_x'] + geom['gr_width'] + geom['cell_inner_width'] // 2
                cell_center_y = row * geom['pitch_y'] + geom['gr_width'] + geom['cell_inner_height'] // 2
                
                # Position transistor
                bbox_center_x = t_bbox.center().x
                bbox_center_y = t_bbox.center().y
                
                trans_x = cell_center_x - bbox_center_x
                trans_y = cell_center_y - bbox_center_y
                
                trans = db.Trans(db.Point(trans_x, trans_y))
                array_cell.insert(db.CellInstArray(transistor_pcell, trans))
                
                # Calculate active indices
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
                
                info = {
                    'row': row,
                    'col': col,
                    'active_row': active_row,
                    'active_col': active_col,
                    'x': cell_center_x,
                    'y': cell_center_y,
                    'is_dummy': is_dummy,
                    'gate_x': cell_center_x * self.layout.dbu,
                    'gate_y': cell_center_y * self.layout.dbu
                }
                
                transistor_info.append(info)
                
                if is_dummy:
                    dummy_count += 1
                else:
                    active_count += 1
        
        print(f"✓ Placed {active_count} active + {dummy_count} dummy PMOS transistors")

        if dummy_count > 0:
            self.connect_dummies_to_vss(array_cell, transistor_info, geom)
        
        if dummy_mode == 'full':
            print(f"Full dummy ring: top/bottom/left/right borders")
        elif dummy_mode == 'sides':
            print(f"Side dummies only: left/right columns")
        else:
            print(f"No dummy transistors")
        
        return array_cell, transistor_info, geom

    def create_route_from_points(self, array_cell, gate_x, gate_y, route_points, m3_width):
        """
        Create route from points - Y-INVERSION ONLY
        """
        segments = []
        
        if len(route_points) < 2:
            return segments
        
        for i in range(len(route_points) - 1):
            current_point = route_points[i]
            next_point = route_points[i + 1]
            
            # Only invert Y coordinate
            curr_x = gate_x + self.dbu(current_point['x'])  # Keep X as is
            curr_y = gate_y - self.dbu(current_point['y'])  # Invert Y
            next_x = gate_x + self.dbu(next_point['x'])     # Keep X as is
            next_y = gate_y - self.dbu(next_point['y'])     # Invert Y
            
            # Rest of the code remains the same...
            dx = abs(next_x - curr_x)
            dy = abs(next_y - curr_y)
            
            if dx > 1 and dy < 1:  # Horizontal
                box = db.Box(
                    min(curr_x, next_x) - m3_width//2,
                    curr_y - m3_width//2,
                    max(curr_x, next_x) + m3_width//2,
                    curr_y + m3_width//2
                )
                array_cell.shapes(self.layers['Metal3']).insert(box)
                
            elif dy > 1 and dx < 1:  # Vertical
                box = db.Box(
                    curr_x - m3_width//2,
                    min(curr_y, next_y) - m3_width//2,
                    curr_x + m3_width//2,
                    max(curr_y, next_y) + m3_width//2
                )
                array_cell.shapes(self.layers['Metal3']).insert(box)
            
            elif dx > 1 and dy > 1:
                # L-shape
                h_box = db.Box(
                    min(curr_x, next_x) - m3_width//2,
                    curr_y - m3_width//2,
                    max(curr_x, next_x) + m3_width//2,
                    curr_y + m3_width//2
                )
                array_cell.shapes(self.layers['Metal3']).insert(h_box)
                
                v_box = db.Box(
                    next_x - m3_width//2,
                    min(curr_y, next_y) - m3_width//2,
                    next_x + m3_width//2,
                    max(curr_y, next_y) + m3_width//2
                )
                array_cell.shapes(self.layers['Metal3']).insert(v_box)
        
        return segments
    
    def create_legacy_route(self, array_cell, gate_x, gate_y, pattern, active_col, m3_width):
        """Create route from legacy pattern format (backward compatibility)"""
        segments = []
        
        # Apply pattern WITHOUT direction logic
        offset_y_dbu = self.dbu(pattern.get('offset_y', 0))
        h_length_dbu = self.dbu(pattern.get('h_length', 0))
        v_length_dbu = self.dbu(pattern.get('v_length', 0))
        
        start_x = gate_x
        start_y = gate_y + offset_y_dbu
        
        # NO AUTOMATIC DIRECTION - respect pattern exactly
        # NO MIRROR EFFECT - all columns use same pattern
        end_x = start_x + h_length_dbu
        
        # Horizontal segment
        if h_length_dbu > 0:
            h_box = db.Box(
                min(start_x, end_x) - m3_width//2, start_y - m3_width//2,
                max(start_x, end_x) + m3_width//2, start_y + m3_width//2
            )
            array_cell.shapes(self.layers['Metal3']).insert(h_box)
            segments.append({'type': 'H', 'start': (start_x, start_y), 'end': (end_x, start_y)})
        
        # Vertical segment - respect pattern direction
        if pattern.get('goes_up', False):
            exit_y = start_y + v_length_dbu
        else:
            exit_y = start_y - v_length_dbu
        
        v_box = db.Box(
            end_x - m3_width//2, min(start_y, exit_y),
            end_x + m3_width//2, max(start_y, exit_y)
        )
        array_cell.shapes(self.layers['Metal3']).insert(v_box)
        segments.append({'type': 'V', 'start': (end_x, start_y), 'end': (end_x, exit_y)})
        
        return segments

    def route_gate_connections_horizontal(self, array_cell, transistor_info, geom=None):
        """
        Route gates HORIZONTALLY by rows with poly extension
        Poly extends 1.5μm ABOVE transistor -> Via Contact -> M3 horizontal bus
        FIXED: For PMOS, find actual poly edge to avoid gap
        """
        print(f"\nRouting gate connections HORIZONTALLY by rows...")
        
        m3_width = self.dbu(METAL3_WIDTH)
        poly_extension = self.dbu(1.5)  # 1.5μm extension above transistor
        
        # Get transistor PCell for terminal analysis
        transistor_pcell = self.create_transistor_pcell('nmos' if self.device_type != 'pmos' else 'pmos')
        transistor_cell = self.layout.cell(transistor_pcell)
        terminal_info = self.analyze_transistor_terminals(transistor_cell)
        
        # PMOS FIX: Find actual poly edge for PMOS only
        poly_top_offset = 0
        if self.device_type == 'pmos':
            print("  PMOS detected: Finding actual GatPoly edge...")
            poly_top = -float('inf')
            
            # Scan all GatPoly shapes to find the actual top edge
            for shape in transistor_cell.shapes(self.layers['GatPoly']).each():
                if shape.is_box():
                    box = shape.box
                    if box.top > poly_top:
                        poly_top = box.top
            
            if poly_top != -float('inf'):
                # Calculate offset from bbox top to actual poly top
                poly_top_offset = terminal_info['bbox_top'] - poly_top
                print(f"    Found poly top offset: {poly_top_offset*self.layout.dbu:.3f}μm below bbox top")
            else:
                # Fallback based on your observation
                poly_top_offset = self.dbu(0.14)
                print(f"    Using fallback offset: {poly_top_offset*self.layout.dbu:.3f}μm")
        
        # Group transistors by ROW (not column)
        rows = {}
        for t in transistor_info:
            if not t['is_dummy']:
                row = t['active_row']
                if row not in rows:
                    rows[row] = []
                rows[row].append(t)
        
        # Sort each row by column
        for row in rows:
            rows[row].sort(key=lambda t: t['active_col'])
        
        # Find guard ring edges for horizontal extension
        all_transistors = transistor_info
        if all_transistors:
            min_x_transistor = min(t['x'] for t in all_transistors)
            max_x_transistor = max(t['x'] for t in all_transistors)
            
            # Guard ring edges in X direction
            left_guard_edge = min_x_transistor - terminal_info['bbox_width']/2 - self.dbu(GUARDRING_SPACING) - self.dbu(GUARDRING_WIDTH)
            right_guard_edge = max_x_transistor + terminal_info['bbox_width']/2 + self.dbu(GUARDRING_SPACING) + self.dbu(GUARDRING_WIDTH)
        
        # Extension beyond guard ring
        extension_beyond = self.dbu(1.5)  # 1.5μm beyond guard ring edge
        
        routes_created = 0
        
        for row in sorted(rows.keys()):
            row_transistors = rows[row]
            
            if len(row_transistors) < 1:
                continue
            
            actual_row_number = (ARRAY_SIZE - 1) - row
            print(f"  Row {row}: Connecting {len(row_transistors)} gates horizontally")
            
            # Y position for horizontal bus (above transistors)
            # FIXED: Adjust for PMOS poly offset
            if self.device_type == 'pmos':
                # For PMOS, start from actual poly top
                bus_y = row_transistors[0]['y'] + terminal_info['bbox_height']/2 - poly_top_offset + poly_extension
            else:
                # For NMOS, keep original calculation
                bus_y = row_transistors[0]['y'] + terminal_info['bbox_height']/2 + poly_extension
            
            # Create poly extensions and via stacks for each transistor
            for t in row_transistors:
                gate_x = t['x']  # Gate center
                gate_y = t['y']  # Gate center
                
                # Extend poly upward from transistor top edge
                # FIXED: Adjust starting point for PMOS
                if self.device_type == 'pmos':
                    # For PMOS, start from actual poly top
                    poly_top = t['y'] + terminal_info['bbox_height']/2 - poly_top_offset
                else:
                    # For NMOS, use bbox top (original)
                    poly_top = t['y'] + terminal_info['bbox_height']/2
                
                poly_extension_y = poly_top + poly_extension
                
                # Create poly extension (vertical stripe)
                poly_width = self.dbu(POLY_WIDTH)
                poly_ext_box = db.Box(
                    gate_x - poly_width//2,
                    poly_top,
                    gate_x + poly_width//2,
                    poly_extension_y
                )
                array_cell.shapes(self.layers['GatPoly']).insert(poly_ext_box)
                
                # Create via stack at extended poly position
                self.create_gate_via_stack_at_position(array_cell, gate_x, poly_extension_y)
                
                # Short vertical M3 segment to connect to horizontal bus
                if abs(poly_extension_y - bus_y) > 1:
                    v_box = db.Box(
                        gate_x - m3_width//2,
                        min(poly_extension_y, bus_y) - m3_width//2,
                        gate_x + m3_width//2,
                        max(poly_extension_y, bus_y) + m3_width//2
                    )
                    array_cell.shapes(self.layers['Metal3']).insert(v_box)
            
            # Create horizontal M3 bus extending to both guard ring edges + 1.5μm
            left_extension_x = left_guard_edge - extension_beyond
            right_extension_x = right_guard_edge + extension_beyond
            
            h_bus_box = db.Box(
                left_extension_x - m3_width//2,
                bus_y - m3_width//2,
                right_extension_x + m3_width//2,
                bus_y + m3_width//2
            )
            array_cell.shapes(self.layers['Metal3']).insert(h_bus_box)
            
            # Add labels at both ends
            label_text = f"G_ROW{actual_row_number}"
            self.add_text(array_cell, left_extension_x, bus_y, label_text)
            self.add_text(array_cell, right_extension_x, bus_y, label_text)
            
            routes_created += 1
            
            if self.device_type == 'pmos':
                print(f"    Row {row}: Poly extends from actual edge (offset {poly_top_offset*self.layout.dbu:.3f}μm)")
        
        print(f"  Created {routes_created} horizontal gate routes")
        return routes_created 
    
    def create_gate_via_stack_at_position(self, cell, x, y):
        """Create via stack from Poly to M3 at specific position"""
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
        
        # M3 pad (part of the routing)
        m3_size = self.dbu(METAL3_WIDTH)
        m3_pad = db.Box(
            x - m3_size//2, y - m3_size//2,
            x + m3_size//2, y + m3_size//2
        )
        cell.shapes(self.layers['Metal3']).insert(m3_pad)    

    def route_column_drains_tm1(self, array_cell, col_transistors, col):
        """
        Route drains VERTICALLY with TopMetal1 - MOVED 1.5μm to the LEFT
        Creates L-shaped M1 extension: vertical up, then horizontal LEFT
        FIXED: Reduced vertical extension by 0.15μm to avoid M3 conflicts
        """
        
        m1_width = self.dbu(METAL1_WIDTH)
        tm1_width = self.dbu(TOPMETAL1_WIDTH)  # 2.0μm wide (increased from 1.64μm)
        
        # Get terminal positions
        transistor_pcell = self.create_transistor_pcell('nmos' if self.device_type != 'pmos' else 'pmos')
        transistor_cell = self.layout.cell(transistor_pcell)
        terminal_info = self.analyze_transistor_terminals(transistor_cell)
        
        # Drain X offset (left edge of drain M1)
        drain_x_offset = terminal_info['drain_left_edge'] - terminal_info['transistor_center']
        
        # Extension parameters
        bbox_half_height = terminal_info['bbox_height'] / 2
        # FIXED: Reduced vertical extension to avoid M3 conflicts
        vertical_extension = self.dbu(0.85)    # WAS 1.0μm, NOW 0.85μm (0.15μm lower)
        horizontal_offset = self.dbu(1.5)     # 1.5μm horizontal offset to the LEFT
        
        print(f"    Column {col}: routing drains with TopMetal1 (1.5μm LEFT, 0.85μm UP)")
        
        drain_tm1_points = []
        
        # Create L-shaped M1 extensions and via stacks for each transistor
        for t in col_transistors:
            # Starting position at drain
            drain_x = t['x'] + drain_x_offset
            
            # STEP 1: M1 vertical extension from center to above transistor
            ext_start_y = t['y']
            # FIXED: Reduced extension to avoid M3 conflicts
            ext_end_y = t['y'] + bbox_half_height + vertical_extension  # Now 0.85μm instead of 1.0μm
            
            # Vertical part of L-shape
            m1_vertical = db.Box(
                drain_x - m1_width//2,
                ext_start_y - m1_width//2,
                drain_x + m1_width//2,
                ext_end_y + m1_width//2
            )
            array_cell.shapes(self.layers['Metal1']).insert(m1_vertical)
            
            # STEP 2: M1 horizontal extension to the LEFT (1.5μm)
            final_x = drain_x - horizontal_offset  # NEGATIVE offset for LEFT direction
            
            # Horizontal part of L-shape (from drain_x to final_x on the left)
            m1_horizontal = db.Box(
                final_x - m1_width//2,      # Left edge at final position
                ext_end_y - m1_width//2,
                drain_x + m1_width//2,       # Right edge at drain position
                ext_end_y + m1_width//2
            )
            array_cell.shapes(self.layers['Metal1']).insert(m1_horizontal)
            
            # STEP 3: Via stack at the END of horizontal extension (LEFT side)
            # FIXED: Via position also moved down by 0.15μm
            via_x = final_x  # Via at the left end of horizontal extension
            via_y = ext_end_y  # Now 0.85μm above transistor instead of 1.0μm
            
            # Create full via stack M1->TopMetal1
            self.create_via_stack_m1_to_tm1(array_cell, via_x, via_y)
            
            drain_tm1_points.append((via_x, via_y))
        
        # Find vertical extent (guard ring edges)
        all_transistors = [t for t in array_cell.parent_transistor_info] if hasattr(array_cell, 'parent_transistor_info') else col_transistors
        
        min_y_transistor = min(t['y'] for t in all_transistors)
        max_y_transistor = max(t['y'] for t in all_transistors)
        
        # Guard ring edges in Y direction
        bottom_guard_edge = min_y_transistor - terminal_info['bbox_height']/2 - self.dbu(GUARDRING_SPACING) - self.dbu(GUARDRING_WIDTH)
        top_guard_edge = max_y_transistor + terminal_info['bbox_height']/2 + self.dbu(GUARDRING_SPACING) + self.dbu(GUARDRING_WIDTH)
        
        # Extension beyond guard rings
        ext_length = self.dbu(1.5)
        bottom_extension_y = bottom_guard_edge - ext_length
        top_extension_y = top_guard_edge + ext_length
        
        # Create vertical TopMetal1 bus at LEFT OFFSET position
        if drain_tm1_points:
            tm1_x = drain_tm1_points[0][0]  # All drains aligned at LEFT offset X position
            
            # Full vertical TopMetal1 bus (2.0μm wide)
            tm1_vertical = db.Box(
                tm1_x - tm1_width//2,
                bottom_extension_y,
                tm1_x + tm1_width//2,
                top_extension_y
            )
            array_cell.shapes(self.layers['TopMetal1']).insert(tm1_vertical)
            
            # Add labels at top and bottom
            label_text = f"D_COL{col}"
            self.add_text(array_cell, tm1_x, bottom_extension_y, label_text)
            self.add_text(array_cell, tm1_x, top_extension_y, label_text)
            
            print(f"      TopMetal1 bus at X={tm1_x*self.layout.dbu:.3f}μm (1.5μm LEFT of drain)")
            print(f"      Via height: Y={via_y*self.layout.dbu:.3f}μm (0.85μm above transistor center)")
            print(f"      Extends from Y={bottom_extension_y*self.layout.dbu:.3f}μm to Y={top_extension_y*self.layout.dbu:.3f}μm")
    
    def create_via_stack_m1_to_tm1(self, cell, x, y):
        """Create complete via stack from M1 to TopMetal1 with CORRECTED M5"""
        
        # M1 to M4 with corrected sizes
        self.create_via_stack_m1_to_m4(cell, x, y)
        
        # Via4 (M4 to M5) - CORRECTED SIZE
        via4_size = self.dbu(0.19)  # Correct size for Via4
        via4_box = db.Box(
            x - via4_size//2, y - via4_size//2,
            x + via4_size//2, y + via4_size//2
        )
        cell.shapes(self.layers['Via4']).insert(via4_box)
        
        # M5 pad - CORRECCIÓN CRÍTICA!!!
        # ANTES (INCORRECTO):
        # m5_size = self.dbu(0.06)  # ❌ Solo 60nm!
        
        # DESPUÉS (CORRECTO):
        m5_enc = self.dbu(0.06)  # Enclosure de 60nm
        m5_pad = via4_box.enlarged(m5_enc)  # ✅ M5 con enclosure apropiado
        # Esto crea un M5 de 0.19 + 2*0.06 = 0.31µm
        
        cell.shapes(self.layers['Metal5']).insert(m5_pad)
        
        # TopVia1 (M5 to TopMetal1) - CORRECTED SIZE
        topvia1_size = self.dbu(TOPVIA1_SIZE)  # 0.42µm
        topvia1_box = db.Box(
            x - topvia1_size//2, y - topvia1_size//2,
            x + topvia1_size//2, y + topvia1_size//2
        )
        cell.shapes(self.layers['TopVia1']).insert(topvia1_box)
        
        # TopMetal1 pad - must be at least 1.64µm wide
        tm1_size = self.dbu(TOPMETAL1_WIDTH)  # 1.64µm
        tm1_pad = db.Box(
            x - tm1_size//2, y - tm1_size//2,
            x + tm1_size//2, y + tm1_size//2
        )
        cell.shapes(self.layers['TopMetal1']).insert(tm1_pad)

    def route_drain_source_connections_new_orientation(self, array_cell, transistor_info):
        """
        Route drains (VERTICAL by columns) and sources (HORIZONTAL by rows)
        Drains: TopMetal1 vertical buses
        Sources: TopMetal2 horizontal buses
        """
        print(f"\nRouting drain and source connections with new orientation...")
        print(f"  Drains: VERTICAL by columns (TopMetal1)")
        print(f"  Sources: HORIZONTAL by rows (TopMetal2)")
        
        # Store transistor info for access by routing functions
        array_cell.parent_transistor_info = transistor_info
        
        # GROUP BY COLUMNS for drains
        columns = {}
        for t in transistor_info:
            if not t['is_dummy']:
                col = t['active_col']
                if col not in columns:
                    columns[col] = []
                columns[col].append(t)
        
        # Sort each column by row
        for col in columns:
            columns[col].sort(key=lambda t: t['active_row'])
        
        # Route drains vertically by column
        for col in sorted(columns.keys()):
            col_transistors = columns[col]
            if len(col_transistors) >= 1:
                print(f"  Column {col}: Processing {len(col_transistors)} drains")
                self.route_column_drains_tm1(array_cell, col_transistors, col)
        
        # GROUP BY ROWS for sources
        rows = {}
        for t in transistor_info:
            if not t['is_dummy']:
                row = t['active_row']
                if row not in rows:
                    rows[row] = []
                rows[row].append(t)
        
        # Sort each row by column
        for row in rows:
            rows[row].sort(key=lambda t: t['active_col'])
        
        # Route sources horizontally by row
        for row in sorted(rows.keys()):
            row_transistors = rows[row]
            if len(row_transistors) >= 1:
                print(f"  Row {row}: Processing {len(row_transistors)} sources")
                self.route_row_sources_tm2(array_cell, row_transistors, row)
        
        print(f"  ✓ Completed drain/source routing")
        print(f"    - {len(columns)} drain columns (TopMetal1)")
        print(f"    - {len(rows)} source rows (TopMetal2)")

    def route_row_drains_m4(self, array_cell, row_transistors, row):
        """
        Route drains: M1 extension from CENTER upward to 1µm OUTSIDE transistor
        Extended horizontally to BOTH left and right guard ring edges + 1.5µm
        FIXED: Corrected row numbering (KLayout row 0 = bottom = GUI row N-1)
        """
        
        m1_width = self.dbu(METAL1_WIDTH)
        m4_width = self.dbu(0.4)
        
        # Get terminal positions and bbox
        transistor_pcell = self.create_transistor_pcell('nmos' if self.device_type != 'pmos' else 'pmos')
        transistor_cell = self.layout.cell(transistor_pcell)
        terminal_info = self.analyze_transistor_terminals(transistor_cell)
        
        # Drain X position (left edge of drain M1)
        drain_x_offset = terminal_info['drain_left_edge'] - terminal_info['transistor_center']
        
        # Extension parameters: from CENTER to 1µm OUTSIDE top edge
        bbox_half_height = terminal_info['bbox_height'] / 2
        extension_beyond = self.dbu(1)  # 1µm beyond transistor boundary
        
        # FIXED: Correct row number for labeling
        actual_row_number = (ARRAY_SIZE - 1) - row
        
        print(f"    KLayout row {row} (GUI row {actual_row_number}): routing drains")
        
        drain_m4_points = []
        
        # Create M1 extensions and via stacks for each transistor
        for i, t in enumerate(row_transistors):
            # Drain X position
            drain_x = t['x'] + drain_x_offset
            
            # Extension Y positions
            ext_start_y = t['y']  # Start from transistor CENTER
            ext_end_y = t['y'] + bbox_half_height + extension_beyond  # End 1µm above top edge
            
            # M1 vertical extension
            m1_extension = db.Box(
                drain_x - m1_width//2,
                ext_start_y - m1_width//2,
                drain_x + m1_width//2,
                ext_end_y + m1_width//2
            )
            array_cell.shapes(self.layers['Metal1']).insert(m1_extension)
            
            # Via stack at end of extension
            via_x = drain_x
            via_y = ext_end_y
            
            # Create full via stack M1->M4
            self.create_via_stack_m1_to_m4(array_cell, via_x, via_y)
            
            drain_m4_points.append((via_x, via_y))
        
        # Find actual array boundaries from all transistors in this row
        # Get all transistors (including dummies) to find edges
        all_row_transistors = [t for t in array_cell.parent_transistor_info 
                            if t['row'] == row] if hasattr(array_cell, 'parent_transistor_info') else row_transistors
        
        # If we don't have parent info, estimate from current transistors
        if not hasattr(array_cell, 'parent_transistor_info'):
            # Find min and max X from transistors
            min_x_transistor = min(t['x'] for t in row_transistors)
            max_x_transistor = max(t['x'] for t in row_transistors)
            
            # Estimate guard ring positions
            left_guard_edge = min_x_transistor - terminal_info['bbox_width']/2 - self.dbu(GUARDRING_SPACING) - self.dbu(GUARDRING_WIDTH)
            right_guard_edge = max_x_transistor + terminal_info['bbox_width']/2 + self.dbu(GUARDRING_SPACING) + self.dbu(GUARDRING_WIDTH)
        else:
            # Use actual positions
            all_x = [t['x'] for t in all_row_transistors]
            left_guard_edge = min(all_x) - terminal_info['bbox_width']/2 - self.dbu(GUARDRING_SPACING) - self.dbu(GUARDRING_WIDTH)
            right_guard_edge = max(all_x) + terminal_info['bbox_width']/2 + self.dbu(GUARDRING_SPACING) + self.dbu(GUARDRING_WIDTH)
        
        # Extension beyond guard rings
        ext_length = self.dbu(1.5)  # 1.5µm beyond guard ring
        left_extension_x = left_guard_edge - ext_length
        right_extension_x = right_guard_edge + ext_length
        
        # Create full horizontal M4 bus from LEFT to RIGHT guard ring edges
        if drain_m4_points:
            m4_y = drain_m4_points[0][1]  # All at same Y
            
            # Full horizontal M4 bus extending BOTH directions
            m4_horizontal = db.Box(
                left_extension_x - m4_width//2,
                m4_y - m4_width//2,
                right_extension_x + m4_width//2,
                m4_y + m4_width//2
            )
            array_cell.shapes(self.layers['Metal4']).insert(m4_horizontal)
            
            # Add label at left extension
            self.add_text(array_cell, left_extension_x, m4_y, f"D_R{actual_row_number}")
            
            print(f"    Extended M4 drain bus from X={left_extension_x*self.layout.dbu:.3f}µm to X={right_extension_x*self.layout.dbu:.3f}µm")

    def route_row_sources_tm2(self, array_cell, row_transistors, row):
        """
        Route sources HORIZONTALLY with TopMetal2 - WITH L-SHAPED EXTENSION
        M1 extension: vertical DOWN (2µm) then horizontal RIGHT (1.5µm)
        This moves the TM1 pad (part of M1->TM2 stack) away from drain TM1 lines
        """
        
        m1_width = self.dbu(METAL1_WIDTH)
        tm2_width = self.dbu(TOPMETAL2_WIDTH)  # 2.00µm wide
        
        # Get terminal positions
        transistor_pcell = self.create_transistor_pcell('nmos' if self.device_type != 'pmos' else 'pmos')
        transistor_cell = self.layout.cell(transistor_pcell)
        terminal_info = self.analyze_transistor_terminals(transistor_cell)
        
        # Source X offset (right edge of source M1)
        source_x_offset = terminal_info['source_right_edge'] - terminal_info['transistor_center']
        
        # Extension parameters
        bbox_half_height = terminal_info['bbox_height'] / 2
        vertical_extension = self.dbu(2.0)    # 2µm vertical extension downward
        horizontal_offset = self.dbu(1.5)     # 1.5µm horizontal offset to the RIGHT
        
        # Correct row number for labeling
        actual_row_number = (ARRAY_SIZE - 1) - row
        
        print(f"    Row {row} (GUI row {actual_row_number}): routing sources with L-extension (2µm down, 1.5µm right)")
        
        source_tm2_points = []
        
        # Create L-shaped M1 extensions and via stacks
        for t in row_transistors:
            # Starting position at source
            source_x = t['x'] + source_x_offset
            
            # STEP 1: M1 vertical extension downward from center
            ext_start_y = t['y']
            ext_end_y = t['y'] - bbox_half_height - vertical_extension  # 2µm below transistor
            
            # Vertical part of L-shape (going DOWN)
            m1_vertical = db.Box(
                source_x - m1_width//2,
                ext_end_y - m1_width//2,
                source_x + m1_width//2,
                ext_start_y + m1_width//2
            )
            array_cell.shapes(self.layers['Metal1']).insert(m1_vertical)
            
            # STEP 2: M1 horizontal extension to the RIGHT (1.5µm)
            final_x = source_x + horizontal_offset  # Move RIGHT from source
            
            # Horizontal part of L-shape (going RIGHT)
            m1_horizontal = db.Box(
                source_x - m1_width//2,
                ext_end_y - m1_width//2,
                final_x + m1_width//2,
                ext_end_y + m1_width//2
            )
            array_cell.shapes(self.layers['Metal1']).insert(m1_horizontal)
            
            # STEP 3: Via stack at the END of horizontal extension (RIGHT side)
            via_x = final_x  # Via at the right end of horizontal extension
            via_y = ext_end_y  # At the bottom of vertical extension
            
            # Create full via stack M1->TopMetal2
            # IMPORTANT: This stack includes a TM1 pad that is now 1.5µm to the RIGHT
            # away from the vertical TM1 lines of the drains
            self.create_via_stack_m1_to_tm2(array_cell, via_x, via_y)
            
            source_tm2_points.append((via_x, via_y))
        
        # Calculate horizontal extent for the TM2 bus
        all_transistors = array_cell.parent_transistor_info if hasattr(array_cell, 'parent_transistor_info') else row_transistors
        
        if all_transistors:
            min_x_transistor = min(t['x'] for t in all_transistors)
            max_x_transistor = max(t['x'] for t in all_transistors)
            
            # Guard ring edges in X direction
            left_guard_edge = min_x_transistor - terminal_info['bbox_width']/2 - self.dbu(GUARDRING_SPACING) - self.dbu(GUARDRING_WIDTH)
            right_guard_edge = max_x_transistor + terminal_info['bbox_width']/2 + self.dbu(GUARDRING_SPACING) + self.dbu(GUARDRING_WIDTH)
        else:
            # Fallback calculation
            left_guard_edge = 0
            dummy_mode = self.metadata.get('dummy_mode', 'sides')
            total_cols = ARRAY_SIZE + 2 if dummy_mode in ['sides', 'full'] else ARRAY_SIZE
            
            if len(row_transistors) >= 2:
                pitch_x = abs(row_transistors[1]['x'] - row_transistors[0]['x'])
            else:
                pitch_x = self.dbu(self.pitch_x)
            
            right_guard_edge = total_cols * pitch_x
        
        # Extension beyond guard rings (may need to increase due to RIGHT offset)
        ext_length = self.dbu(2.0)  # Increased to account for the horizontal offset
        left_extension_x = left_guard_edge - ext_length
        right_extension_x = right_guard_edge + ext_length
        
        # Create horizontal TopMetal2 bus at the offset position
        if source_tm2_points:
            tm2_y = source_tm2_points[0][1]  # All sources at same Y (2µm below transistor)
            
            # Full horizontal TopMetal2 bus (2.00µm wide)
            tm2_horizontal = db.Box(
                left_extension_x,
                tm2_y - tm2_width//2,
                right_extension_x,
                tm2_y + tm2_width//2
            )
            array_cell.shapes(self.layers['TopMetal2']).insert(tm2_horizontal)
            
            # Add labels at both ends
            label_text = f"S_R{actual_row_number}"
            self.add_text(array_cell, left_extension_x, tm2_y, label_text)
            self.add_text(array_cell, right_extension_x, tm2_y, label_text)
            
            print(f"      TopMetal2 bus at Y={tm2_y*self.layout.dbu:.3f}µm")
            print(f"      Via stacks offset 1.5µm RIGHT from sources")
            print(f"      TM1 pads in via stack now separated from drain TM1 lines")

    def create_via_stack_m1_to_m4(self, cell, x, y):
        """Create via stack from M1 to M4 with CORRECT via sizes"""
        
        # Via1 (M1 to M2) - CORRECTED SIZE
        via1_size = self.dbu(0.19)  # Was 0.26
        via1_box = db.Box(
            x - via1_size//2, y - via1_size//2,
            x + via1_size//2, y + via1_size//2
        )
        cell.shapes(self.layers['Via1']).insert(via1_box)
        
        # M2 pad with proper enclosure
        m2_enc = self.dbu(0.06)
        m2_pad = via1_box.enlarged(m2_enc)
        cell.shapes(self.layers['Metal2']).insert(m2_pad)
        
        # Via2 (M2 to M3) - CORRECTED SIZE
        via2_size = self.dbu(0.19)  # Was 0.26
        via2_box = db.Box(
            x - via2_size//2, y - via2_size//2,
            x + via2_size//2, y + via2_size//2
        )
        cell.shapes(self.layers['Via2']).insert(via2_box)
        
        # M3 pad
        m3_enc = self.dbu(0.06)
        m3_pad = via2_box.enlarged(m3_enc)
        cell.shapes(self.layers['Metal3']).insert(m3_pad)
        
        # Via3 (M3 to M4) - CORRECTED SIZE
        via3_size = self.dbu(0.19)  # Was 0.26
        via3_box = db.Box(
            x - via3_size//2, y - via3_size//2,
            x + via3_size//2, y + via3_size//2
        )
        cell.shapes(self.layers['Via3']).insert(via3_box)
        
        # M4 pad
        m4_enc = self.dbu(0.06)
        m4_pad = via3_box.enlarged(m4_enc)
        cell.shapes(self.layers['Metal4']).insert(m4_pad)

        def create_via_stack_m1_to_m5(self, cell, x, y):
            """Create complete via stack from M1 to M5"""
            
            # First create stack to M4
            self.create_via_stack_m1_to_m4(cell, x, y)
            
            # Via4 (M4 to M5)
            via4_size = self.dbu(0.19)
            via4_box = db.Box(
                x - via4_size//2, y - via4_size//2,
                x + via4_size//2, y + via4_size//2
            )
            cell.shapes(self.layers['Via4']).insert(via4_box)
            
            # M5 pad
            m5_size = self.dbu(0.4)
            m5_pad = db.Box(
                x - m5_size//2, y - m5_size//2,
                x + m5_size//2, y + m5_size//2
            )
            cell.shapes(self.layers['Metal5']).insert(m5_pad)

    def create_via_stack_m1_to_tm2(self, cell, x, y):
        """Create complete via stack from M1 to TopMetal2"""
        
        # First create stack to TopMetal1
        self.create_via_stack_m1_to_tm1(cell, x, y)
        
        # TopVia2 (TopMetal1 to TopMetal2)
        topvia2_size = self.dbu(TOPVIA2_SIZE)  
        topvia2_box = db.Box(
            x - topvia2_size//2, y - topvia2_size//2,
            x + topvia2_size//2, y + topvia2_size//2
        )
        cell.shapes(self.layers['TopVia2']).insert(topvia2_box)
        
        # TopMetal2 pad
        tm2_size = self.dbu(TOPMETAL2_WIDTH)
        tm2_pad = db.Box(
            x - tm2_size//2, y - tm2_size//2,
            x + tm2_size//2, y + tm2_size//2
        )
        cell.shapes(self.layers['TopMetal2']).insert(tm2_pad)

    def create_via_stack_to_m4(self, cell, x, y):
        """Create via stack from M1 to M4"""
        via_size = self.dbu(0.19)
        
        # Via1 (M1 to M2)
        via1_box = db.Box(x - via_size//2, y - via_size//2,
                        x + via_size//2, y + via_size//2)
        cell.shapes(self.layers['Via1']).insert(via1_box)
        
        # M2 pad
        m2_pad = via1_box.enlarged(self.dbu(0.05))
        cell.shapes(self.layers['Metal2']).insert(m2_pad)
        
        # Via2 (M2 to M3)
        via2_box = db.Box(x - via_size//2, y - via_size//2,
                        x + via_size//2, y + via_size//2)
        cell.shapes(self.layers['Via2']).insert(via2_box)
        
        # M3 pad
        m3_pad = via2_box.enlarged(self.dbu(0.05))
        cell.shapes(self.layers['Metal3']).insert(m3_pad)
        
        # Via3 (M3 to M4)
        via3_box = db.Box(x - via_size//2, y - via_size//2,
                        x + via_size//2, y + via_size//2)
        cell.shapes(self.layers['Via3']).insert(via3_box)

    def create_via_stack_to_m5(self, cell, x, y):
        """Create via stack from M1 to M5"""
        # First create stack to M4
        self.create_via_stack_to_m4(cell, x, y)
        
        via_size = self.dbu(0.19)
        
        # M4 pad
        m4_pad = db.Box(x - via_size//2 - self.dbu(0.05),
                        y - via_size//2 - self.dbu(0.05),
                        x + via_size//2 + self.dbu(0.05),
                        y + via_size//2 + self.dbu(0.05))
        cell.shapes(self.layers['Metal4']).insert(m4_pad)
        
        # Via4 (M4 to M5)
        via4_box = db.Box(x - via_size//2, y - via_size//2,
                        x + via_size//2, y + via_size//2)
        cell.shapes(self.layers['Via4']).insert(via4_box)

    def create_gate_via_stack(self, cell, x, y):
        """Create via stack from Poly to Metal3"""
        cont_size = self.dbu(CONT_SIZE)
        via1_size = self.dbu(VIA1_SIZE)
        via2_size = self.dbu(VIA2_SIZE)
        
        # Contact
        cont_box = db.Box(
            x - cont_size//2, y - cont_size//2,
            x + cont_size//2, y + cont_size//2
        )
        cell.shapes(self.layers['Cont']).insert(cont_box)
        
        # M1
        m1_pad = cont_box.enlarged(self.dbu(0.05))
        cell.shapes(self.layers['Metal1']).insert(m1_pad)
        
        # Via1
        via1_box = db.Box(
            x - via1_size//2, y - via1_size//2,
            x + via1_size//2, y + via1_size//2
        )
        cell.shapes(self.layers['Via1']).insert(via1_box)
        
        # M2
        m2_pad = via1_box.enlarged(self.dbu(0.05))
        cell.shapes(self.layers['Metal2']).insert(m2_pad)
        
        # Via2
        via2_box = db.Box(
            x - via2_size//2, y - via2_size//2,
            x + via2_size//2, y + via2_size//2
        )
        cell.shapes(self.layers['Via2']).insert(via2_box)
    
    def add_text(self, cell, x, y, text):
        """Add text label"""
        text_obj = db.Text(text, db.Trans(db.Point(x, y)))
        cell.shapes(self.layers['TEXT']).insert(text_obj)
    
    def generate_structure(self, output_file):
        """Generate complete structure with NMOS and/or PMOS - FIXED VERSION"""
        print("\n" + "="*60)
        print("GENERATING MISMATCH TEST STRUCTURE")
        print("="*60)
        
        print(f"Device type requested: {self.device_type}")
        
        if self.device_type == 'both':
            # Create both NMOS and PMOS arrays
            nmos_array, nmos_info, nmos_geom = self.create_nmos_array()
            self.route_gate_connections_horizontal(nmos_array, nmos_info, nmos_geom)
            self.route_drain_source_connections_new_orientation(nmos_array, nmos_info)
            
            pmos_array, pmos_info, pmos_geom = self.create_pmos_array()
            self.route_gate_connections_horizontal(pmos_array, pmos_info, pmos_geom)
            self.route_drain_source_connections_new_orientation(pmos_array, pmos_info)
                    
            # Place side by side
            nmos_trans = db.Trans(db.Point(0, 0))
            self.top_cell.insert(db.CellInstArray(nmos_array.cell_index(), nmos_trans))
            
            separation = self.dbu(30)
            pmos_x = nmos_array.bbox().width() + separation
            pmos_trans = db.Trans(db.Point(pmos_x, 0))
            self.top_cell.insert(db.CellInstArray(pmos_array.cell_index(), pmos_trans))
            
            print("✓ Generated both NMOS and PMOS arrays")
        
        elif self.device_type == 'pmos':
            # PMOS only
            pmos_array, pmos_info, pmos_geom = self.create_pmos_array()
            self.route_gate_connections_horizontal(pmos_array, pmos_info, pmos_geom)
            self.route_drain_source_connections_new_orientation(pmos_array, pmos_info)
            pmos_trans = db.Trans(db.Point(0, 0))
            self.top_cell.insert(db.CellInstArray(pmos_array.cell_index(), pmos_trans))
            
            print("✓ Generated PMOS array only")
        
        else:
            # NMOS only (default)
            nmos_array, nmos_info, nmos_geom = self.create_nmos_array()
            self.route_gate_connections_horizontal(nmos_array, nmos_info, nmos_geom)
            self.route_drain_source_connections_new_orientation(nmos_array, nmos_info)
            nmos_trans = db.Trans(db.Point(0, 0))
            self.top_cell.insert(db.CellInstArray(nmos_array.cell_index(), nmos_trans))
            
            print("✓ Generated NMOS array only")
        
        # Add title
        bbox = self.top_cell.bbox()
        title_y = bbox.top + self.dbu(10)
        title = f"{self.device_type.upper()} Mismatch Array {ARRAY_SIZE}x{ARRAY_SIZE} - W={TRANSISTOR_W}µm L={TRANSISTOR_L}µm"
        self.add_text(self.top_cell, bbox.center().x, title_y, title)
        
        # Save
        print(f"\nSaving to: {output_file}")
        self.layout.write(output_file)
        
        # Final report
        self.print_final_report()
    
    def connect_dummies_to_vss(self, array_cell, transistor_info, geom):
        """
        Short S/D/G terminals of each dummy transistor INTERNALLY only
        NO connection between different dummies
        """
        print("\n  Shorting dummy transistor terminals (internal only)...")
        
        # Get transistor terminal positions
        transistor_pcell = self.create_transistor_pcell('nmos' if self.device_type != 'pmos' else 'pmos')
        transistor_cell = self.layout.cell(transistor_pcell)
        terminal_info = self.analyze_transistor_terminals(transistor_cell)
        
        m1_width = self.dbu(METAL1_WIDTH)
        m2_width = self.dbu(METAL2_WIDTH)
        
        dummy_count = 0
        
        # Process each dummy independently - NO INTERCONNECTION
        for t in transistor_info:
            if t['is_dummy']:
                dummy_count += 1
                
                trans_center_x = t['x']
                trans_center_y = t['y']
                
                # Get terminal positions
                drain_x = trans_center_x + (terminal_info['drain_center'] - terminal_info['transistor_center'])
                source_x = trans_center_x + (terminal_info['source_center'] - terminal_info['transistor_center'])
                gate_x = trans_center_x
                
                # M2 bar to short THIS dummy's terminals only
                left_x = min(drain_x, source_x) - self.dbu(0.2)
                right_x = max(drain_x, source_x) + self.dbu(0.2)
                
                m2_bar = db.Box(
                    left_x, trans_center_y - m2_width//2,
                    right_x, trans_center_y + m2_width//2
                )
                array_cell.shapes(self.layers['Metal2']).insert(m2_bar)
                
                # Via1 at drain
                via1_box = db.Box(
                    drain_x - self.dbu(VIA1_SIZE)//2,
                    trans_center_y - self.dbu(VIA1_SIZE)//2,
                    drain_x + self.dbu(VIA1_SIZE)//2,
                    trans_center_y + self.dbu(VIA1_SIZE)//2
                )
                array_cell.shapes(self.layers['Via1']).insert(via1_box)
                
                # Via1 at source
                via1_box = db.Box(
                    source_x - self.dbu(VIA1_SIZE)//2,
                    trans_center_y - self.dbu(VIA1_SIZE)//2,
                    source_x + self.dbu(VIA1_SIZE)//2,
                    trans_center_y + self.dbu(VIA1_SIZE)//2
                )
                array_cell.shapes(self.layers['Via1']).insert(via1_box)
                
                # Gate connection: small poly extension for contact
                poly_ext_y = trans_center_y + self.dbu(0.3)
                
                poly_ext_box = db.Box(
                    gate_x - self.dbu(POLY_WIDTH)//2,
                    trans_center_y,
                    gate_x + self.dbu(POLY_WIDTH)//2,
                    poly_ext_y
                )
                array_cell.shapes(self.layers['GatPoly']).insert(poly_ext_box)
                
                # Contact at poly extension
                cont_box = db.Box(
                    gate_x - self.dbu(CONT_SIZE)//2,
                    poly_ext_y - self.dbu(CONT_SIZE),
                    gate_x + self.dbu(CONT_SIZE)//2,
                    poly_ext_y
                )
                array_cell.shapes(self.layers['Cont']).insert(cont_box)
                
                # M1 connection
                m1_box = db.Box(
                    gate_x - m1_width//2,
                    trans_center_y - m2_width//2,
                    gate_x + m1_width//2,
                    poly_ext_y
                )
                array_cell.shapes(self.layers['Metal1']).insert(m1_box)
                
                # Via1 at gate
                via1_box = db.Box(
                    gate_x - self.dbu(VIA1_SIZE)//2,
                    trans_center_y - self.dbu(VIA1_SIZE)//2,
                    gate_x + self.dbu(VIA1_SIZE)//2,
                    trans_center_y + self.dbu(VIA1_SIZE)//2
                )
                array_cell.shapes(self.layers['Via1']).insert(via1_box)
        
        print(f"    ✓ Shorted {dummy_count} dummy transistors (internal only, no interconnection)")


    def print_final_report(self):
        """Print final summary"""
        bbox = self.top_cell.bbox()
        total_area = bbox.width() * bbox.height() / 1e6
        
        print("\n" + "="*60)
        print(f"FINAL REPORT - {self.device_type.upper()} STRUCTURE GENERATED")
        print("="*60)
        print(f"\nConfiguration:")
        print(f"  Device Type: {self.device_type}")
        print(f"  Transistor W: {TRANSISTOR_W} µm")
        print(f"  Transistor L: {TRANSISTOR_L} µm")
        print(f"  Guardring spacing: {GUARDRING_SPACING} µm")
        print(f"  Array: {ARRAY_SIZE}x{ARRAY_SIZE}")
        
        print(f"\nDimensions:")
        print(f"  Total area: {total_area:.0f} µm²")
        print(f"  Chip size: {bbox.width()/1000:.1f} x {bbox.height()/1000:.1f} µm")
        
        print(f"\nTransistor count:")
        print(f"  Active: {self.debug_info['transistor_count']}")
        print(f"  Dummy: {self.debug_info['dummy_count']}")
        print(f"  Total: {self.debug_info['transistor_count'] + self.debug_info['dummy_count']}")
        
        print(f"\nFeatures:")
        print(f"  ✓ Scalable dimensions (W, L configurable)")
        print(f"  ✓ Configurable guardring spacing ({GUARDRING_SPACING}µm)")
        print(f"  ✓ Shared guardring borders")
        print(f"  ✓ {self.device_type.upper()} support enabled")
        print(f"  ✓ Pattern-based routing")
        print("="*60)

def main():
    """Main function"""
    
    # Load data to get device type
    full_data = load_pattern_and_config()
    device_type = full_data.get('metadata', {}).get('device_type', 'nmos')
    
    # Get pattern file name for output naming
    pattern_file = 'default'
    if '$pattern_file' in globals():
        import os
        pattern_file = os.path.splitext(os.path.basename(globals()['$pattern_file']))[0]
    
    # Output file with appropriate name
    try:
        output
    except NameError:
        if device_type == 'both':
            output = f"mismatch_array_{ARRAY_SIZE}x{ARRAY_SIZE}_both_{pattern_file}.gds"
        elif device_type == 'pmos':
            output = f"mismatch_array_{ARRAY_SIZE}x{ARRAY_SIZE}_pmos_{pattern_file}.gds"
        else:
            output = f"mismatch_array_{ARRAY_SIZE}x{ARRAY_SIZE}_nmos_{pattern_file}.gds"
    
    print(f"Output file: {output}")
    
    # Generate structure
    generator = ScalableMismatchArray()
    generator.generate_structure(output)
    
    print(f"\nTo view the result:")
    print(f"  klayout {output}")

if __name__ == "__main__":
    main()