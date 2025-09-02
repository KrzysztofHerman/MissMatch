#!/usr/bin/env python3
"""
INTEGRATED MATRIX OF MISMATCH ARRAYS GENERATOR
Works with KLayout environment to generate matrix of arrays with merged guardrings
Usage:
  klayout -zz -r integrated_matrix_generator.py -rd config_file=matrix_config.json -rd output=matrix_output.gds
"""

import pya
import klayout.db as db
import json
import sys
import os

# Constants
GUARDRING_WIDTH = 0.5  # μm
METAL1_WIDTH = 0.28
METAL3_WIDTH = 0.20
CONT_SIZE = 0.22
VIA1_SIZE = 0.19
VIA2_SIZE = 0.19

# PDK library
LIB_NAME = 'SG13_dev'

# Layer definitions
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
    'Via3':     (49, 0),
    'Metal4':   (50, 0),
    'Via4':     (66, 0),
    'Metal5':   (67, 0),
    'TEXT':     (63, 0),
    'TopVia1':  (125, 0),
    'TopMetal1':(126, 0),
    'TopVia2':  (133, 0),
    'TopMetal2':(134, 0),
}


class IntegratedMatrixGenerator:
    """
    Integrated matrix generator for KLayout environment
    """
    
    def __init__(self, config_file):
        """Initialize with configuration"""
        self.config_file = config_file
        self.load_configuration()
        
        # Create main layout
        self.layout = db.Layout(True)
        self.layout.dbu = 0.001  # 1nm
        
        # Load PDK library if available (in KLayout)
        try:
            self.lib = pya.Library.library_by_name(LIB_NAME)
            self.has_pdk = True
            print(f"✓ PDK library '{LIB_NAME}' loaded")
        except:
            self.lib = None
            self.has_pdk = False
            print(f"⚠ PDK library '{LIB_NAME}' not found - using simplified transistors")
        
        # Create top cell
        cell_name = f"Matrix_{self.matrix_rows}x{self.matrix_cols}_Array{self.subarray_size}x{self.subarray_size}_{self.device_type}"
        self.top_cell = self.layout.create_cell(cell_name)
        
        # Create layer indices
        self.layers = {}
        for name, (layer, datatype) in LAYER_MAP.items():
            self.layers[name] = self.layout.layer(layer, datatype)
        
        print("\n" + "="*70)
        print("INTEGRATED MATRIX GENERATOR")
        print("="*70)
        
    def load_configuration(self):
        """Load and validate configuration"""
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            
            self.matrix_rows = config.get('matrix_rows', 3)
            self.matrix_cols = config.get('matrix_cols', 3)
            self.subarray_size = config.get('subarray_size', 16)
            self.device_type = config.get('device_type', 'nmos')
            self.dummy_mode = config.get('dummy_mode', 'sides')
            self.guardring_spacing = config.get('guardring_spacing', 2.0)
            self.w_values = config.get('w_values', [0.5, 1.0, 2.0])
            self.l_values = config.get('l_values', [0.35, 0.5, 1.0])
            
            # Adjust array lengths to match matrix dimensions
            if len(self.w_values) != self.matrix_rows:
                print(f"  Adjusting W values to match {self.matrix_rows} rows")
                if len(self.w_values) < self.matrix_rows:
                    self.w_values += [self.w_values[-1]] * (self.matrix_rows - len(self.w_values))
                else:
                    self.w_values = self.w_values[:self.matrix_rows]
            
            if len(self.l_values) != self.matrix_cols:
                print(f"  Adjusting L values to match {self.matrix_cols} columns")
                if len(self.l_values) < self.matrix_cols:
                    self.l_values += [self.l_values[-1]] * (self.matrix_cols - len(self.l_values))
                else:
                    self.l_values = self.l_values[:self.matrix_cols]
            
            print(f"Configuration loaded from: {self.config_file}")
            print(f"  Matrix: {self.matrix_rows}x{self.matrix_cols}")
            print(f"  Subarray: {self.subarray_size}x{self.subarray_size}")
            print(f"  Device: {self.device_type}")
            print(f"  W values: {self.w_values}")
            print(f"  L values: {self.l_values}")
            
        except FileNotFoundError:
            print(f"ERROR: Configuration file '{self.config_file}' not found")
            sys.exit(1)
        except Exception as e:
            print(f"Configuration error: {e}")
            sys.exit(1)
    
    def dbu(self, value_um):
        """Convert μm to database units"""
        return int(value_um / self.layout.dbu)
    
    def create_transistor_or_placeholder(self, w, l, device_type='nmos'):
        """
        Create transistor PCell if PDK available, otherwise create placeholder
        Returns cell index and bbox
        """
        if self.has_pdk and self.lib:
            # Use real PDK transistor
            pcell_decl = self.lib.layout().pcell_declaration(device_type)
            if pcell_decl:
                params = {
                    'w': f'{w}u',
                    'l': f'{l}u',
                    'ng': '1'
                }
                pcell_idx = self.layout.add_pcell_variant(self.lib, pcell_decl.id(), params)
                pcell = self.layout.cell(pcell_idx)
                return pcell_idx, pcell.bbox()
        
        # Create placeholder transistor
        placeholder_name = f"Transistor_{device_type}_W{w}_L{l}".replace(".", "_")
        
        # Check if already exists
        for cell_idx in self.layout.each_cell():
            cell = self.layout.cell(cell_idx)
            if cell.name == placeholder_name:
                return cell_idx, cell.bbox()
        
        # Create new placeholder
        cell = self.layout.create_cell(placeholder_name)
        
        # Simple rectangular representations
        w_dbu = self.dbu(w)
        l_dbu = self.dbu(l)
        
        # Active area (slightly larger than gate)
        active_box = db.Box(-w_dbu//2 - self.dbu(0.2), -l_dbu*2,
                            w_dbu//2 + self.dbu(0.2), l_dbu*2)
        cell.shapes(self.layers['Activ']).insert(active_box)
        
        # Gate poly
        gate_box = db.Box(-w_dbu//2, -l_dbu//2, w_dbu//2, l_dbu//2)
        cell.shapes(self.layers['GatPoly']).insert(gate_box)
        
        # Source/Drain metal (M1)
        # Drain (left)
        drain_box = db.Box(-w_dbu//2 - self.dbu(0.4), -l_dbu,
                           -w_dbu//2 - self.dbu(0.1), l_dbu)
        cell.shapes(self.layers['Metal1']).insert(drain_box)
        
        # Source (right)
        source_box = db.Box(w_dbu//2 + self.dbu(0.1), -l_dbu,
                           w_dbu//2 + self.dbu(0.4), l_dbu)
        cell.shapes(self.layers['Metal1']).insert(source_box)
        
        # Add implant
        if device_type == 'nmos':
            cell.shapes(self.layers['nSD']).insert(active_box)
        else:
            cell.shapes(self.layers['pSD']).insert(active_box)
            # Add N-well for PMOS
            nwell_box = active_box.enlarged(self.dbu(1.0))
            cell.shapes(self.layers['NWell']).insert(nwell_box)
        
        return cell.cell_index(), cell.bbox()
    
    def create_merged_guardring_structure(self):
        """
        Create the complete merged guardring structure for the entire matrix
        """
        print("\nCreating unified guardring structure...")
        
        gr_width = self.dbu(GUARDRING_WIDTH)
        
        # Get typical transistor dimensions for pitch calculation
        test_idx, test_bbox = self.create_transistor_or_placeholder(
            self.w_values[0], self.l_values[0], self.device_type)
        
        # Calculate pitch for single cell
        cell_pitch_x = test_bbox.width() + self.dbu(2 * self.guardring_spacing) + gr_width
        cell_pitch_y = test_bbox.height() + self.dbu(2 * self.guardring_spacing) + gr_width
        
        # Account for dummy columns if enabled
        if self.dummy_mode == 'sides':
            actual_cols = self.subarray_size + 2  # Add left and right dummy columns
            actual_rows = self.subarray_size
        elif self.dummy_mode == 'full':
            actual_cols = self.subarray_size + 2
            actual_rows = self.subarray_size + 2
        else:
            actual_cols = self.subarray_size
            actual_rows = self.subarray_size
        
        # Total stripes needed
        total_v_stripes = self.matrix_cols * actual_cols + 1
        total_h_stripes = self.matrix_rows * actual_rows + 1
        
        # Total dimensions
        total_width = self.matrix_cols * actual_cols * cell_pitch_x + gr_width
        total_height = self.matrix_rows * actual_rows * cell_pitch_y + gr_width
        
        # Create vertical guardring stripes
        for stripe_idx in range(total_v_stripes):
            x = stripe_idx * cell_pitch_x
            
            stripe_box = db.Box(x, 0, x + gr_width, total_height)
            
            # Active area
            self.top_cell.shapes(self.layers['Activ']).insert(stripe_box)
            
            # Implant based on device type
            if self.device_type == 'pmos':
                self.top_cell.shapes(self.layers['nSD']).insert(stripe_box)
            else:
                self.top_cell.shapes(self.layers['pSD']).insert(stripe_box)
        
        # Create horizontal guardring stripes
        for stripe_idx in range(total_h_stripes):
            y = stripe_idx * cell_pitch_y
            
            stripe_box = db.Box(0, y, total_width, y + gr_width)
            
            # Active area
            self.top_cell.shapes(self.layers['Activ']).insert(stripe_box)
            
            # Implant
            if self.device_type == 'pmos':
                self.top_cell.shapes(self.layers['nSD']).insert(stripe_box)
            else:
                self.top_cell.shapes(self.layers['pSD']).insert(stripe_box)
        
        # Add N-well for PMOS
        if self.device_type == 'pmos':
            nwell_margin = self.dbu(2.0)
            nwell_box = db.Box(
                -nwell_margin,
                -nwell_margin,
                total_width + nwell_margin,
                total_height + nwell_margin
            )
            self.top_cell.shapes(self.layers['NWell']).insert(nwell_box)
        
        # Store dimensions for transistor placement
        self.cell_pitch_x = cell_pitch_x
        self.cell_pitch_y = cell_pitch_y
        self.gr_width = gr_width
        self.actual_cols = actual_cols
        self.actual_rows = actual_rows
        
        print(f"  Created guardring grid: {total_v_stripes} x {total_h_stripes} stripes")
        print(f"  Cell pitch: {cell_pitch_x * self.layout.dbu:.3f} x {cell_pitch_y * self.layout.dbu:.3f} μm")
        print(f"  Total size: {total_width * self.layout.dbu:.1f} x {total_height * self.layout.dbu:.1f} μm")
        
        return cell_pitch_x, cell_pitch_y, gr_width
    
    def place_transistors_in_matrix(self):
        """
        Place all transistors in the complete matrix including dummies
        """
        print("\nPlacing transistors in matrix...")
        
        transistor_count = 0
        dummy_count = 0
        
        # Iterate through matrix positions
        for matrix_row in range(self.matrix_rows):
            for matrix_col in range(self.matrix_cols):
                
                w = self.w_values[matrix_row]
                l = self.l_values[matrix_col]
                
                print(f"  Subarray [{matrix_row},{matrix_col}]: W={w}μm, L={l}μm")
                
                # Create transistor for this W/L
                transistor_idx, t_bbox = self.create_transistor_or_placeholder(w, l, self.device_type)
                
                # Place transistors in this subarray (including dummies)
                for sub_row in range(self.actual_rows):
                    for sub_col in range(self.actual_cols):
                        
                        # Determine if this is a dummy
                        is_dummy = False
                        if self.dummy_mode == 'sides':
                            is_dummy = (sub_col == 0 or sub_col == self.actual_cols - 1)
                        elif self.dummy_mode == 'full':
                            is_dummy = (sub_row == 0 or sub_row == self.actual_rows - 1 or
                                      sub_col == 0 or sub_col == self.actual_cols - 1)
                        
                        # Calculate absolute position
                        abs_row = matrix_row * self.actual_rows + sub_row
                        abs_col = matrix_col * self.actual_cols + sub_col
                        
                        # Cell center position
                        cell_center_x = abs_col * self.cell_pitch_x + self.gr_width + \
                                      (self.cell_pitch_x - self.gr_width) // 2
                        cell_center_y = abs_row * self.cell_pitch_y + self.gr_width + \
                                      (self.cell_pitch_y - self.gr_width) // 2
                        
                        # Transistor placement
                        trans_x = cell_center_x - t_bbox.center().x
                        trans_y = cell_center_y - t_bbox.center().y
                        
                        trans = db.Trans(db.Point(trans_x, trans_y))
                        self.top_cell.insert(db.CellInstArray(transistor_idx, trans))
                        
                        if is_dummy:
                            dummy_count += 1
                        else:
                            transistor_count += 1
        
        print(f"  Placed {transistor_count} active transistors")
        print(f"  Placed {dummy_count} dummy transistors")
        print(f"  Total: {transistor_count + dummy_count} transistors")
        
        return transistor_count, dummy_count
    
    def add_guardring_contacts(self):
        """Add contacts to guardring structure"""
        print("\nAdding guardring contacts...")
        
        cont_size = self.dbu(CONT_SIZE)
        cont_spacing = self.dbu(0.60)
        cont_pitch = cont_size + cont_spacing
        m1_enc = self.dbu(0.06)
        
        contacts_added = 0
        
        # Simplified contact placement - add contacts at regular intervals
        # Skip intersections
        exclusion_zone = self.dbu(0.5)
        
        # Add contacts along vertical stripes
        total_v_stripes = self.matrix_cols * self.actual_cols + 1
        for stripe_idx in range(total_v_stripes):
            x_center = stripe_idx * self.cell_pitch_x + self.gr_width // 2
            
            y = cont_pitch
            while y < self.matrix_rows * self.actual_rows * self.cell_pitch_y:
                # Check if near horizontal stripe intersection
                if (y % self.cell_pitch_y) > exclusion_zone and \
                   (y % self.cell_pitch_y) < (self.cell_pitch_y - exclusion_zone):
                    # Add contact
                    cont_box = db.Box(
                        x_center - cont_size//2, y - cont_size//2,
                        x_center + cont_size//2, y + cont_size//2
                    )
                    self.top_cell.shapes(self.layers['Cont']).insert(cont_box)
                    
                    # M1 pad
                    m1_box = cont_box.enlarged(m1_enc)
                    self.top_cell.shapes(self.layers['Metal1']).insert(m1_box)
                    contacts_added += 1
                
                y += cont_pitch
        
        print(f"  Added {contacts_added} contacts to guardring")
    
    def add_matrix_labels(self):
        """Add labels for the matrix"""
        print("\nAdding matrix labels...")
        
        bbox = self.top_cell.bbox()
        
        # Main title
        title_y = bbox.top + self.dbu(15)
        title = f"{self.device_type.upper()} Matrix {self.matrix_rows}x{self.matrix_cols} ({self.subarray_size}x{self.subarray_size} each)"
        text_obj = db.Text(title, db.Trans(db.Point(bbox.center().x, title_y)))
        self.top_cell.shapes(self.layers['TEXT']).insert(text_obj)
        
        # L values (horizontal labels at top)
        label_y = bbox.top + self.dbu(8)
        for col in range(self.matrix_cols):
            x_pos = (col + 0.5) * self.actual_cols * self.cell_pitch_x
            l_text = f"L={self.l_values[col]}μm"
            text_obj = db.Text(l_text, db.Trans(db.Point(x_pos, label_y)))
            self.top_cell.shapes(self.layers['TEXT']).insert(text_obj)
        
        # W values (vertical labels on left)
        for row in range(self.matrix_rows):
            y_pos = (row + 0.5) * self.actual_rows * self.cell_pitch_y
            w_text = f"W={self.w_values[row]}μm"
            text_obj = db.Text(w_text, db.Trans(db.Point(bbox.left - self.dbu(15), y_pos)))
            self.top_cell.shapes(self.layers['TEXT']).insert(text_obj)
        
        # Statistics at bottom
        active_transistors = self.matrix_rows * self.matrix_cols * self.subarray_size * self.subarray_size
        if self.dummy_mode == 'sides':
            dummy_transistors = self.matrix_rows * self.matrix_cols * 2 * self.subarray_size
        elif self.dummy_mode == 'full':
            dummy_transistors = self.matrix_rows * self.matrix_cols * ((self.subarray_size + 2) ** 2 - self.subarray_size ** 2)
        else:
            dummy_transistors = 0
        
        info_y = bbox.bottom - self.dbu(10)
        info_text = f"Active: {active_transistors} | Dummy: {dummy_transistors} | Total: {active_transistors + dummy_transistors}"
        text_obj = db.Text(info_text, db.Trans(db.Point(bbox.center().x, info_y)))
        self.top_cell.shapes(self.layers['TEXT']).insert(text_obj)
        
        print(f"  Added labels for {self.matrix_rows}x{self.matrix_cols} matrix")
    
    def generate(self, output_file):
        """
        Main generation function
        """
        # Create unified guardring structure
        self.create_merged_guardring_structure()
        
        # Place all transistors
        active_count, dummy_count = self.place_transistors_in_matrix()
        
        # Add guardring contacts
        self.add_guardring_contacts()
        
        # Add labels
        self.add_matrix_labels()
        
        # Save result
        print(f"\nSaving to: {output_file}")
        self.layout.write(output_file)
        
        # Final report
        bbox = self.top_cell.bbox()
        area_um2 = bbox.width() * bbox.height() * self.layout.dbu * self.layout.dbu
        
        print("\n" + "="*70)
        print("MATRIX GENERATION COMPLETE")
        print("="*70)
        print(f"Matrix: {self.matrix_rows}x{self.matrix_cols} subarrays")
        print(f"Each subarray: {self.subarray_size}x{self.subarray_size} transistors")
        print(f"Active transistors: {active_count}")
        print(f"Dummy transistors: {dummy_count}")
        print(f"Total transistors: {active_count + dummy_count}")
        print(f"Chip dimensions: {bbox.width() * self.layout.dbu:.1f} x {bbox.height() * self.layout.dbu:.1f} μm")
        print(f"Total area: {area_um2:.0f} μm²")
        print("\nParametric variation:")
        print(f"  W (vertical): {self.w_values} μm")
        print(f"  L (horizontal): {self.l_values} μm")
        print("\n✓ Matrix generated with merged guardrings")
        print("="*70)


def main():
    """Main function for KLayout execution"""
    
    # Check if running in KLayout with -rd parameters
    if 'config_file' in globals():
        # Running in KLayout with -rd parameters
        config_file = globals()['config_file']
        output_file = globals().get('output', 'matrix_output.gds')
        
        print(f"Running in KLayout mode")
        print(f"Config file: {config_file}")
        print(f"Output file: {output_file}")
        
    else:
        # Running as standalone Python script
        import argparse
        
        parser = argparse.ArgumentParser(
            description='Generate matrix of mismatch arrays',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  # Run with KLayout:
  klayout -zz -r integrated_matrix_generator.py -rd config_file=matrix_config.json -rd output=output.gds
  
  # Run with Python (requires KLayout Python module):
  python integrated_matrix_generator.py matrix_config.json -o output.gds
            """
        )
        parser.add_argument('config', help='JSON configuration file')
        parser.add_argument('-o', '--output', default='matrix_output.gds', help='Output GDS file')
        
        args = parser.parse_args()
        config_file = args.config
        output_file = args.output
        
        print(f"Running in standalone Python mode")
        print(f"Config file: {config_file}")
        print(f"Output file: {output_file}")
    
    # Check if config file exists
    if not os.path.exists(config_file):
        print(f"ERROR: Configuration file '{config_file}' not found!")
        print("\nPlease create a configuration file with the following format:")
        print(json.dumps({
            "matrix_rows": 3,
            "matrix_cols": 3,
            "subarray_size": 16,
            "device_type": "nmos",
            "dummy_mode": "sides",
            "guardring_spacing": 2.0,
            "w_values": [0.5, 1.0, 2.0],
            "l_values": [0.35, 0.5, 1.0]
        }, indent=2))
        sys.exit(1)
    
    # Generate matrix
    generator = IntegratedMatrixGenerator(config_file)
    generator.generate(output_file)
    
    print(f"\nTo view the result:")
    print(f"  klayout {output_file}")


if __name__ == "__main__":
    main()
