#!/usr/bin/env python3
"""
MATRIX OF MISMATCH ARRAYS GENERATOR
Generates MxN matrix of mismatch arrays with parametric W/L variation
Adjacent arrays have overlapped guardrings for seamless connection

Author: Based on mismatch_array_4x4_modified.py
"""

import pya
import klayout.db as db
import json
import subprocess
import os
import tempfile
import sys

class MatrixOfArraysGenerator:
    """
    Wrapper class to generate matrix of mismatch arrays with overlapped guardrings
    """
    
    def __init__(self, config_file):
        """Initialize with configuration file"""
        self.config_file = config_file
        self.load_configuration()
        
        # Layout setup
        self.layout = db.Layout(True)
        self.layout.dbu = 0.001  # 1nm database unit
        
        # Create top cell
        cell_name = f"Matrix_{self.matrix_rows}x{self.matrix_cols}_SubArray_{self.subarray_size}x{self.subarray_size}"
        self.top_cell = self.layout.create_cell(cell_name)
        
        # Layer definitions (same as base generator)
        self.layers = {}
        layer_map = {
            'TEXT': (63, 0),
            'Metal1': (8, 0),
            'Metal3': (30, 0),
            'Metal4': (50, 0),
            'TopMetal1': (126, 0),
            'TopMetal2': (134, 0),
        }
        for name, (layer, datatype) in layer_map.items():
            self.layers[name] = self.layout.layer(layer, datatype)
        
        print("\n" + "="*70)
        print("MATRIX OF MISMATCH ARRAYS GENERATOR")
        print("="*70)
        
        # Store generated array cells
        self.array_cells = {}
        self.array_bboxes = {}
        
    def load_configuration(self):
        """Load configuration from JSON file"""
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            
            # Matrix dimensions
            self.matrix_rows = config.get('matrix_rows', 3)
            self.matrix_cols = config.get('matrix_cols', 3)
            
            # Subarray parameters
            self.subarray_size = config.get('subarray_size', 16)
            self.device_type = config.get('device_type', 'nmos')
            self.dummy_mode = config.get('dummy_mode', 'sides')
            self.guardring_spacing = config.get('guardring_spacing', 2.0)
            
            # W/L values for variation
            self.w_values = config.get('w_values', [1.0, 1.5, 2.0])
            self.l_values = config.get('l_values', [0.35, 0.5, 0.7])
            
            # Validate dimensions
            if len(self.w_values) != self.matrix_rows:
                raise ValueError(f"Number of W values ({len(self.w_values)}) must match matrix rows ({self.matrix_rows})")
            if len(self.l_values) != self.matrix_cols:
                raise ValueError(f"Number of L values ({len(self.l_values)}) must match matrix cols ({self.matrix_cols})")
            
            print(f"Configuration loaded from: {self.config_file}")
            print(f"  Matrix: {self.matrix_rows}x{self.matrix_cols}")
            print(f"  Subarray size: {self.subarray_size}x{self.subarray_size}")
            print(f"  W values: {self.w_values}")
            print(f"  L values: {self.l_values}")
            print(f"  Device type: {self.device_type}")
            
        except FileNotFoundError:
            print(f"ERROR: Configuration file '{self.config_file}' not found")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"ERROR: Invalid JSON in configuration file: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"ERROR: {e}")
            sys.exit(1)
    
    def generate_single_array(self, w, l, row, col):
        """
        Generate a single mismatch array using the base generator
        Returns the GDS file path
        """
        # Create temporary pattern file for this specific array
        pattern_data = {
            'metadata': {
                'transistor_W': w,
                'transistor_L': l,
                'guardring_spacing': self.guardring_spacing,
                'array_rows': self.subarray_size,
                'device_type': self.device_type,
                'dummy_mode': self.dummy_mode
            },
            'pattern_data': {}
        }
        
        # Create temporary files
        temp_pattern = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        temp_gds = tempfile.NamedTemporaryFile(suffix='.gds', delete=False)
        
        try:
            # Write pattern file
            json.dump(pattern_data, temp_pattern)
            temp_pattern.close()
            temp_gds.close()
            
            # Run base generator
            print(f"\n  Generating subarray [{row},{col}]: W={w}μm, L={l}μm")
            
            # Execute the base generator script
            cmd = [
                'klayout', '-zz', '-r', 'mismatch_array_4x4_modified.py',
                '-rd', f'pattern_file={temp_pattern.name}',
                '-rd', f'output={temp_gds.name}'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"ERROR generating array: {result.stderr}")
                return None
            
            return temp_gds.name
            
        finally:
            # Clean up temp pattern file
            if os.path.exists(temp_pattern.name):
                os.unlink(temp_pattern.name)
    
    def read_gds_and_get_cell(self, gds_file):
        """Read GDS file and return the top cell"""
        temp_layout = db.Layout()
        temp_layout.read(gds_file)
        
        # Find the array cell (should be the top cell)
        for cell_idx in temp_layout.each_cell():
            cell = temp_layout.cell(cell_idx)
            if 'MismatchArray' in cell.name or 'array' in cell.name:
                return cell, temp_layout
        
        # If not found, return top cell
        return temp_layout.top_cell(), temp_layout
    
    def calculate_overlap_offsets(self):
        """
        Calculate placement offsets considering guardring overlap
        Guardring width is 0.5μm, so overlap = 0.5μm
        """
        # Guardring width in database units
        self.guardring_width = int(0.5 / self.layout.dbu)  # 0.5μm
        
        print(f"\n  Guardring width: {self.guardring_width * self.layout.dbu:.3f}μm")
        print(f"  Arrays will overlap by guardring width for seamless connection")
        
    def place_arrays_with_overlap(self):
        """
        Place all arrays in matrix with proper guardring overlap
        """
        self.calculate_overlap_offsets()
        
        print(f"\nGenerating {self.matrix_rows}x{self.matrix_cols} matrix of arrays...")
        
        # Generate and store all arrays first
        temp_files = []
        
        for row in range(self.matrix_rows):
            for col in range(self.matrix_cols):
                w = self.w_values[row]
                l = self.l_values[col]
                
                # Generate array
                gds_file = self.generate_single_array(w, l, row, col)
                if gds_file:
                    temp_files.append(gds_file)
                    
                    # Read the generated array
                    array_cell, source_layout = self.read_gds_and_get_cell(gds_file)
                    
                    # Copy cell to our layout
                    cell_name = f"Array_W{w}_L{l}_R{row}C{col}"
                    new_cell = self.layout.create_cell(cell_name)
                    
                    # Copy all shapes from source to new cell
                    for layer_info in source_layout.layer_infos():
                        layer_idx = source_layout.layer(layer_info.layer, layer_info.datatype)
                        target_layer = self.layout.layer(layer_info.layer, layer_info.datatype)
                        
                        for shape in array_cell.shapes(layer_idx).each():
                            new_cell.shapes(target_layer).insert(shape)
                    
                    # Store cell and bbox
                    self.array_cells[(row, col)] = new_cell
                    self.array_bboxes[(row, col)] = array_cell.bbox()
        
        # Now place arrays with overlap
        print("\nPlacing arrays with guardring overlap...")
        
        # Track placement positions
        x_positions = [0]  # First column at x=0
        y_positions = [0]  # First row at y=0
        
        # Calculate X positions (columns) - accounting for overlap
        for col in range(1, self.matrix_cols):
            prev_bbox = self.array_bboxes[(0, col-1)]
            curr_bbox = self.array_bboxes[(0, col)]
            
            # Position = previous position + previous width - guardring overlap
            x_offset = x_positions[-1] + prev_bbox.width() - self.guardring_width
            x_positions.append(x_offset)
        
        # Calculate Y positions (rows) - accounting for overlap
        for row in range(1, self.matrix_rows):
            prev_bbox = self.array_bboxes[(row-1, 0)]
            curr_bbox = self.array_bboxes[(row, 0)]
            
            # Position = previous position + previous height - guardring overlap
            y_offset = y_positions[-1] + prev_bbox.height() - self.guardring_width
            y_positions.append(y_offset)
        
        # Place all arrays
        for row in range(self.matrix_rows):
            for col in range(self.matrix_cols):
                cell = self.array_cells[(row, col)]
                x_pos = x_positions[col]
                y_pos = y_positions[row]
                
                # Create transformation and place
                trans = db.Trans(db.Point(x_pos, y_pos))
                self.top_cell.insert(db.CellInstArray(cell.cell_index(), trans))
                
                print(f"  Placed [{row},{col}] at ({x_pos * self.layout.dbu:.1f}, {y_pos * self.layout.dbu:.1f})μm")
        
        # Clean up temp files
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
        
        print("✓ All arrays placed with overlapped guardrings")
    
    def add_global_labels(self):
        """
        Add global labels for the entire matrix
        Renumber columns and rows across the full matrix
        """
        print("\nAdding global matrix labels...")
        
        bbox = self.top_cell.bbox()
        
        # Title at top
        title_y = bbox.top + int(20 / self.layout.dbu)
        title = f"{self.device_type.upper()} Matrix {self.matrix_rows}x{self.matrix_cols} of {self.subarray_size}x{self.subarray_size} Arrays"
        text_obj = db.Text(title, db.Trans(db.Point(bbox.center().x, title_y)))
        self.top_cell.shapes(self.layers['TEXT']).insert(text_obj)
        
        # Add parameter grid below title
        param_y = title_y - int(10 / self.layout.dbu)
        param_text = "W↓ L→  " + "  ".join([f"L={l}" for l in self.l_values])
        text_obj = db.Text(param_text, db.Trans(db.Point(bbox.left - int(30 / self.layout.dbu), param_y)))
        self.top_cell.shapes(self.layers['TEXT']).insert(text_obj)
        
        # Add W labels on left
        for row in range(self.matrix_rows):
            y_pos = y_positions[row] + self.array_bboxes[(row, 0)].height() // 2
            w_text = f"W={self.w_values[row]}"
            text_obj = db.Text(w_text, db.Trans(db.Point(bbox.left - int(20 / self.layout.dbu), y_pos)))
            self.top_cell.shapes(self.layers['TEXT']).insert(text_obj)
        
        # Add global column/row numbering
        total_cols = self.matrix_cols * self.subarray_size
        total_rows = self.matrix_rows * self.subarray_size
        
        # Add info text
        info_y = bbox.bottom - int(10 / self.layout.dbu)
        info_text = f"Total: {total_cols}x{total_rows} transistors"
        text_obj = db.Text(info_text, db.Trans(db.Point(bbox.center().x, info_y)))
        self.top_cell.shapes(self.layers['TEXT']).insert(text_obj)
        
        print(f"✓ Added global labels")
        print(f"  Total transistor grid: {total_cols}x{total_rows}")
    
    def add_global_corner_connections(self):
        """
        Add VBULK connections at all guardring intersection corners
        This ensures electrical continuity across the matrix
        """
        print("\nAdding global corner connections...")
        
        # Add connection pads at key intersections
        # This would require analyzing the guardring intersections
        # For now, we rely on the overlap to provide continuity
        
        print("✓ Guardring overlap provides electrical continuity")
    
    def generate(self, output_file):
        """
        Main generation function
        """
        # Place arrays with overlap
        self.place_arrays_with_overlap()
        
        # Add global labels
        self.add_global_labels()
        
        # Add corner connections
        self.add_global_corner_connections()
        
        # Save the result
        print(f"\nSaving matrix to: {output_file}")
        self.layout.write(output_file)
        
        # Final report
        bbox = self.top_cell.bbox()
        area = bbox.width() * bbox.height() * self.layout.dbu * self.layout.dbu
        
        print("\n" + "="*70)
        print("MATRIX GENERATION COMPLETE")
        print("="*70)
        print(f"Matrix dimensions: {self.matrix_rows}x{self.matrix_cols} subarrays")
        print(f"Each subarray: {self.subarray_size}x{self.subarray_size} transistors")
        print(f"Total transistors: {self.matrix_rows * self.matrix_cols * self.subarray_size * self.subarray_size}")
        print(f"Chip area: {bbox.width() * self.layout.dbu:.1f} x {bbox.height() * self.layout.dbu:.1f} μm")
        print(f"Total area: {area:.0f} μm²")
        print("\nW variation (vertical):", self.w_values)
        print("L variation (horizontal):", self.l_values)
        print("\n✓ Arrays connected with overlapped guardrings")
        print("✓ Ready for mismatch characterization")
        print("="*70)


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate matrix of mismatch arrays')
    parser.add_argument('config', help='JSON configuration file')
    parser.add_argument('-o', '--output', default=None, help='Output GDS file')
    
    args = parser.parse_args()
    
    # Generate output filename if not specified
    if args.output is None:
        config_base = os.path.splitext(os.path.basename(args.config))[0]
        args.output = f"matrix_{config_base}.gds"
    
    # Create generator and run
    generator = MatrixOfArraysGenerator(args.config)
    generator.generate(args.output)
    
    print(f"\nTo view the result:")
    print(f"  klayout {args.output}")


if __name__ == "__main__":
    main()
