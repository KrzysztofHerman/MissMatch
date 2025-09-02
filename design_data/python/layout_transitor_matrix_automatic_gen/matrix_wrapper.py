#!/usr/bin/env python3
"""
MATRIX WRAPPER FOR MISMATCH ARRAYS - FIXED VERSION
- Corrected column ordering (column 0 = rightmost = maximum L)
- Added matrix numbering 1-25 according to specification
- Maintains overlapped guardrings

Usage:
  klayout -zz -r matrix_wrapper_fixed.py -rd config_file=matrix_config_5x5.json -rd output=matrix_5x5.gds
"""

import pya
import klayout.db as db
import json
import subprocess
import os
import tempfile
import sys

class MatrixWrapper:
    """
    Wrapper to combine multiple mismatch arrays with guardring overlap
    Fixed version with correct ordering and numbering
    """
    
    def __init__(self, config_file):
        self.config_file = config_file
        
        # Initialize matrix numbers BEFORE loading configuration
        self.matrix_numbers = {}
        
        # Storage for arrays
        self.array_cells = {}
        self.array_bboxes = {}
        self.x_positions = []
        self.y_positions = []
        
        # Load configuration
        self.load_configuration()
        
        # Now calculate matrix numbers after we know dimensions
        self.calculate_matrix_numbers()
        
        # Create output layout
        self.layout = db.Layout(True)
        self.layout.dbu = 0.001  # 1nm
        
        # Create top cell
        cell_name = f"Matrix_{self.matrix_rows}x{self.matrix_cols}_Array{self.subarray_size}x{self.subarray_size}"
        self.top_cell = self.layout.create_cell(cell_name)
        
        # Layer mapping
        self.layers = {}
        layer_map = {
            'TEXT': (63, 0),
            'Metal3': (30, 0),
            'Metal4': (50, 0),
            'TopMetal1': (126, 0),
            'TopMetal2': (134, 0),
        }
        for name, (layer, datatype) in layer_map.items():
            self.layers[name] = self.layout.layer(layer, datatype)
        
        print("\n" + "="*70)
        print("MATRIX WRAPPER FOR MISMATCH ARRAYS - FIXED VERSION")
        print("="*70)
        
        # Print matrix layout after initialization
        self.print_matrix_layout()
        
    def calculate_matrix_numbers(self):
        """
        Calculate matrix numbers 1-25 according to specification:
        Row 0: [5] [4] [3] [2] [1]
        Row 1: [10][9] [8] [7] [6]
        Row 2: [15][14][13][12][11]
        Row 3: [20][19][18][17][16]
        Row 4: [25][24][23][22][21]
        """
        for row in range(self.matrix_rows):
            for col in range(self.matrix_cols):
                # Number increases from right to left, top to bottom
                # col 4 = rightmost = numbers 1,6,11,16,21
                # col 0 = leftmost = numbers 5,10,15,20,25
                matrix_num = row * 5 + (5 - col)
                self.matrix_numbers[(row, col)] = matrix_num
    
    def print_matrix_layout(self):
        """Print the matrix layout with numbering"""
        print("\nMatrix Layout (Matrix# [W,L]):")
        for row in range(self.matrix_rows):
            row_str = "  "
            for col in range(self.matrix_cols):
                matrix_num = self.matrix_numbers.get((row, col), 0)
                w = self.w_values[row]
                l = self.l_values[col]
                row_str += f"[{matrix_num:2d}:{w:.3f},{l:.3f}] "
            print(row_str)
                
    def load_configuration(self):
        """Load configuration from JSON file"""
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
            
            # Validate dimensions
            if len(self.w_values) < self.matrix_rows:
                self.w_values += [self.w_values[-1]] * (self.matrix_rows - len(self.w_values))
            elif len(self.w_values) > self.matrix_rows:
                self.w_values = self.w_values[:self.matrix_rows]
                
            if len(self.l_values) < self.matrix_cols:
                self.l_values += [self.l_values[-1]] * (self.matrix_cols - len(self.l_values))
            elif len(self.l_values) > self.matrix_cols:
                self.l_values = self.l_values[:self.matrix_cols]
            
            print(f"Configuration loaded:")
            print(f"  Matrix: {self.matrix_rows}x{self.matrix_cols}")
            print(f"  Subarray size: {self.subarray_size}x{self.subarray_size}")
            print(f"  Device type: {self.device_type}")
            print(f"  W values (rows): {self.w_values}")
            print(f"  L values (cols): {self.l_values}")
            
        except Exception as e:
            print(f"ERROR loading configuration: {e}")
            sys.exit(1)
    
    def generate_single_array(self, w, l, row, col, matrix_num):
        """
        Generate a single array using mismatch_array_4x4_modified.py
        Returns the GDS file path
        """
        # First check if there's a default pattern file that might interfere
        default_patterns = ['temp_pattern.json']
        for default in default_patterns:
            if os.path.exists(default):
                print(f"    WARNING: Found default pattern file {default}, removing it")
                os.unlink(default)
        
        # Create pattern file for this specific array
        pattern_data = {
            'metadata': {
                'transistor_W': w,
                'transistor_L': l,
                'guardring_spacing': self.guardring_spacing,
                'array_rows': self.subarray_size,
                'device_type': self.device_type,
                'dummy_mode': self.dummy_mode,
                'matrix_number': matrix_num  # Add matrix number for tracking
            },
            'pattern_data': {}
        }
        
        # Use specific pattern filename
        pattern_name = f'pattern_matrix{matrix_num}_w{str(w).replace(".", "_")}_l{str(l).replace(".", "_")}'
        pattern_filename = f'{pattern_name}.json'
        
        # First, record existing GDS files before generation
        import glob
        existing_gds = set(glob.glob('*.gds'))
        
        try:
            # Write pattern file
            with open(pattern_filename, 'w') as f:
                json.dump(pattern_data, f, indent=2)
            
            print(f"  Generating Matrix #{matrix_num} [{row},{col}]: W={w}um, L={l}um")
            
            # Run the mismatch array generator with sg13g2 technology
            cmd = [
                'klayout', '-n', 'sg13g2', '-zz', '-r', 'mismatch_array_4x4_modified.py',
                '-rd', f'pattern_file={pattern_filename}'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if result.returncode != 0:
                print(f"    ERROR: Return code {result.returncode}")
                if result.stderr:
                    print(f"    STDERR: {result.stderr[:1000]}")
                return None
            
            # Find the newly generated file
            new_gds = set(glob.glob('*.gds')) - existing_gds
            
            if new_gds:
                actual_output = list(new_gds)[0]
            else:
                # Try to find by expected pattern
                possible_outputs = [
                    f'mismatch_array_{self.subarray_size}x{self.subarray_size}_nmos.gds',
                    f'mismatch_array_{self.subarray_size}x{self.subarray_size}_pmos.gds',
                ]
                
                actual_output = None
                for possible in possible_outputs:
                    if os.path.exists(possible):
                        actual_output = possible
                        break
            
            if actual_output and os.path.exists(actual_output):
                file_size = os.path.getsize(actual_output)
                if file_size > 0:
                    # Rename to a unique name to avoid conflicts
                    unique_output = f'array_matrix{matrix_num}_r{row}c{col}.gds'
                    if os.path.exists(unique_output):
                        os.unlink(unique_output)
                    os.rename(actual_output, unique_output)
                    print(f"    ” Generated: {unique_output} ({file_size} bytes)")
                    return unique_output
                else:
                    print(f"    ERROR: Generated file is empty")
                    return None
            else:
                print(f"    ERROR: Could not find output file")
                return None
            
        except Exception as e:
            print(f"    ERROR: {e}")
            return None
        finally:
            # Clean up pattern file
            if os.path.exists(pattern_filename):
                os.unlink(pattern_filename)
    
    def read_gds_cell(self, gds_file):
        """
        Read GDS file and return the main array cell
        """
        try:
            temp_layout = db.Layout()
            temp_layout.read(gds_file)
            
            # Try to find cell by name
            possible_names = [
                f'MismatchArray_{self.subarray_size}x{self.subarray_size}_NMOS',
                f'MismatchArray_{self.subarray_size}x{self.subarray_size}_PMOS',
                f'nmos_array_{self.subarray_size}x{self.subarray_size}',
                f'pmos_array_{self.subarray_size}x{self.subarray_size}',
            ]
            
            for cell_name in possible_names:
                try:
                    cell = temp_layout.cell(cell_name)
                    if cell:
                        return cell, temp_layout
                except:
                    continue
            
            # If not found by name, use top cell
            top = temp_layout.top_cell()
            if top:
                return top, temp_layout
            
            # Last resort: use first cell
            cell_index = 0
            while True:
                try:
                    cell = temp_layout.cell(cell_index)
                    if cell:
                        return cell, temp_layout
                    cell_index += 1
                except:
                    break
            
            raise Exception("No cells found in GDS file")
            
        except Exception as e:
            print(f"      ERROR reading GDS: {e}")
            raise
    
    def update_connection_labels(self, array_cell, matrix_num):
        """
        Update connection labels in the array cell to use matrix numbering
        Replace D_COL#, S_R#, G_ROW# with M#_D_COL#, M#_S_R#, M#_G_ROW#
        """
        # This would require modifying the text objects in the cell
        # Since we can't easily modify text objects after creation,
        # we'll add additional labels with the matrix number
        
        # Add matrix number label at the center of each array
        bbox = array_cell.bbox()
        center_x = bbox.center().x
        center_y = bbox.bottom - int(5 / self.layout.dbu)  # 5um below array
        
        label = f"MATRIX_{matrix_num}"
        text_obj = db.Text(label, db.Trans(db.Point(center_x, center_y)))
        array_cell.shapes(self.layers['TEXT']).insert(text_obj)
    
    def generate_matrix(self, output_file):
        """
        Generate the complete matrix of arrays
        """
        print(f"\nGenerating {self.matrix_rows}x{self.matrix_cols} matrix (25 subarrays)...")
        
        # Storage for temp files
        temp_files = []
        
        # Step 1: Generate all individual arrays
        print("\nStep 1: Generating individual arrays...")
        for row in range(self.matrix_rows):
            for col in range(self.matrix_cols):
                w = self.w_values[row]
                l = self.l_values[col]
                matrix_num = self.matrix_numbers[(row, col)]
                
                # Generate array GDS
                gds_file = self.generate_single_array(w, l, row, col, matrix_num)
                if gds_file and os.path.exists(gds_file):
                    temp_files.append(gds_file)
                    
                    # Create a cell to hold this array
                    cell_name = f"Array_M{matrix_num}_W{str(w).replace('.', '_')}_L{str(l).replace('.', '_')}"
                    array_cell = self.layout.create_cell(cell_name)
                    
                    # Read the GDS file
                    temp_layout = db.Layout()
                    temp_layout.read(gds_file)
                    
                    # Get the main cell
                    source_cell, source_layout = self.read_gds_cell(gds_file)
                    bbox = source_cell.bbox()
                    
                    # Copy all shapes (flattened)
                    for layer_info in temp_layout.layer_infos():
                        layer = layer_info.layer
                        datatype = layer_info.datatype
                        
                        source_layer_idx = temp_layout.layer(layer, datatype)
                        target_layer_idx = self.layout.layer(layer, datatype)
                        
                        # Use Region to get all shapes
                        region = db.Region(source_cell.begin_shapes_rec(source_layer_idx))
                        for polygon in region.each():
                            array_cell.shapes(target_layer_idx).insert(polygon)
                    
                    # Add matrix number label
                    self.update_connection_labels(array_cell, matrix_num)
                    
                    self.array_cells[(row, col)] = array_cell
                    self.array_bboxes[(row, col)] = bbox
                    
                    print(f"    ” Imported Matrix #{matrix_num}: {bbox.width()*0.001:.1f} x {bbox.height()*0.001:.1f}um")
                    print(f"      W={w}um, L={l}um, bbox=({bbox.width()*self.layout.dbu:.3f} x {bbox.height()*self.layout.dbu:.3f})um")
                else:
                    print(f"    Failed to generate Matrix #{matrix_num} [{row},{col}]")
        
        if not self.array_cells:
            print("ERROR: No arrays were generated successfully!")
            return
        
        # Step 2: Calculate positions with guardring overlap
        print("\nStep 2: Calculating positions with guardring overlap...")
        
        # Overlap values that work well
        overlap_x_um = 4.6+1.14-0.5   # um - Horizontal overlap (left/right)
        overlap_y_um = 13.5  # um - Vertical overlap (top/bottom)
        
        overlap_x_dbu = int(overlap_x_um / self.layout.dbu)
        overlap_y_dbu = int(overlap_y_um / self.layout.dbu)
        
        print(f"  Using overlap values:")
        print(f"    Horizontal (X): {overlap_x_um}um")
        print(f"    Vertical (Y): {overlap_y_um}um")
        
        # Calculate column widths (max width for each column)
        col_widths = []
        for col in range(self.matrix_cols):
            max_width = 0
            for row in range(self.matrix_rows):
                if (row, col) in self.array_bboxes:
                    width = self.array_bboxes[(row, col)].width()
                    max_width = max(max_width, width)
            col_widths.append(max_width)
        
        # Calculate row heights (max height for each row)
        row_heights = []
        for row in range(self.matrix_rows):
            max_height = 0
            for col in range(self.matrix_cols):
                if (row, col) in self.array_bboxes:
                    height = self.array_bboxes[(row, col)].height()
                    max_height = max(max_height, height)
            row_heights.append(max_height)
        
        # Print dimensions for debugging
        print(f"  Column widths: {[w*self.layout.dbu for w in col_widths]}")
        print(f"  Row heights: {[h*self.layout.dbu for h in row_heights]}")
        
        # Calculate X positions based on column widths
        self.x_positions = [0]
        for col in range(1, self.matrix_cols):
            x_pos = self.x_positions[-1] + col_widths[col-1] - overlap_x_dbu
            self.x_positions.append(x_pos)
        
        # Calculate Y positions based on row heights
        self.y_positions = [0]
        for row in range(1, self.matrix_rows):
            y_pos = self.y_positions[-1] + row_heights[row-1] - overlap_y_dbu
            self.y_positions.append(y_pos)
        
        # Step 3: Place arrays
        print("\nStep 3: Placing arrays...")
        for row in range(self.matrix_rows):
            for col in range(self.matrix_cols):
                if (row, col) in self.array_cells:
                    cell = self.array_cells[(row, col)]
                    matrix_num = self.matrix_numbers[(row, col)]
                    x = self.x_positions[col] if col < len(self.x_positions) else 0
                    y = self.y_positions[row] if row < len(self.y_positions) else 0
                    
                    trans = db.Trans(db.Point(x, y))
                    self.top_cell.insert(db.CellInstArray(cell.cell_index(), trans))
                    
                    print(f"    Placed Matrix #{matrix_num} at ({x*self.layout.dbu:.1f}, {y*self.layout.dbu:.1f})um")
        
        # Step 4: Add labels
        print("\nStep 4: Adding matrix labels...")
        self.add_matrix_labels()
        
        # Step 5: Add global connection labels
        print("\nStep 5: Adding global routing labels...")
        self.add_global_routing_labels()
        
        # Clean up temp files
        print("\nStep 6: Cleaning up...")
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
        
        # Clean up pattern files
        import glob
        for pattern_file in glob.glob('pattern_matrix*.json'):
            os.unlink(pattern_file)
        
        # Save result
        print(f"\nSaving to: {output_file}")
        self.layout.write(output_file)
        
        # Final report
        self.print_final_report()
    
    def add_matrix_labels(self):
        """Add labels for the complete matrix"""
        bbox = self.top_cell.bbox()
        
        # Title
        title_y = bbox.top + int(20 / self.layout.dbu)
        title = f"{self.device_type.upper()} Matrix {self.matrix_rows}x{self.matrix_cols} - Total 25 Subarrays"
        text_obj = db.Text(title, db.Trans(db.Point(bbox.center().x, title_y)))
        self.top_cell.shapes(self.layers['TEXT']).insert(text_obj)
        
        # Add W/L value labels on sides
        for row in range(self.matrix_rows):
            # W values on left
            if (row, 0) in self.array_bboxes:
                bbox_row = self.array_bboxes[(row, 0)]
                label_x = bbox_row.left - int(10 / self.layout.dbu)
                label_y = self.y_positions[row] + bbox_row.height() // 2
                label = f"W={self.w_values[row]}um"
                text_obj = db.Text(label, db.Trans(db.Point(label_x, label_y)))
                self.top_cell.shapes(self.layers['TEXT']).insert(text_obj)
        
        for col in range(self.matrix_cols):
            # L values on bottom
            if (0, col) in self.array_bboxes:
                bbox_col = self.array_bboxes[(0, col)]
                label_x = self.x_positions[col] + bbox_col.width() // 2
                label_y = bbox_col.bottom - int(10 / self.layout.dbu)
                label = f"L={self.l_values[col]}um"
                text_obj = db.Text(label, db.Trans(db.Point(label_x, label_y)))
                self.top_cell.shapes(self.layers['TEXT']).insert(text_obj)
    
    def add_global_routing_labels(self):
        """Add labels for global routing connections"""
        # This would add labels for the combined routing buses
        # For example: "GATES_M1-5", "DRAINS_M1-5", etc.
        pass
    
    def print_final_report(self):
        """Print summary report"""
        bbox = self.top_cell.bbox()
        area_um2 = bbox.width() * bbox.height() * self.layout.dbu * self.layout.dbu
        
        print("\n" + "="*70)
        print("MATRIX GENERATION COMPLETE")
        print("="*70)
        print(f"Matrix: {self.matrix_rows}x{self.matrix_cols} = 25 subarrays")
        print(f"Each subarray: {self.subarray_size}x{self.subarray_size} transistors")
        if self.dummy_mode == "full":
            actual_size = self.subarray_size + 2
            print(f"  With full dummy ring: {actual_size}x{actual_size} total")
        print(f"Chip size: {bbox.width()*self.layout.dbu:.1f} x {bbox.height()*self.layout.dbu:.1f} um")
        print(f"Total area: {area_um2:.0f} umÂ²")
        print(f"\nTotal transistors:")
        print(f"  Active: {25 * self.subarray_size * self.subarray_size}")
        if self.dummy_mode == "full":
            dummy_count = 25 * (4 * self.subarray_size + 4)
            print(f"  Dummies: {dummy_count}")
            print(f"  Total: {25 * self.subarray_size * self.subarray_size + dummy_count}")
        
        print("\nMatrix arrangement (Matrix# [W,L]):")
        for row in range(self.matrix_rows):
            row_str = "  "
            for col in range(self.matrix_cols):
                matrix_num = self.matrix_numbers[(row, col)]
                w = self.w_values[row]
                l = self.l_values[col]
                row_str += f"[{matrix_num:2d}:{w:.3f},{l:.3f}] "
            print(row_str)
        print("="*70)


def main():
    """Main entry point"""
    
    # Check if running in KLayout with -rd parameters
    if 'config_file' in globals():
        config_file = globals()['config_file']
        output_file = globals().get('output', 'matrix_output.gds')
    else:
        # Standalone Python mode
        import argparse
        
        parser = argparse.ArgumentParser(description='Generate matrix of mismatch arrays')
        parser.add_argument('config', help='JSON configuration file')
        parser.add_argument('-o', '--output', default='matrix_output.gds', help='Output GDS file')
        
        args = parser.parse_args()
        config_file = args.config
        output_file = args.output
    
    # Check config file exists
    if not os.path.exists(config_file):
        print(f"ERROR: Configuration file '{config_file}' not found!")
        sys.exit(1)
    
    # Check that base script exists
    if not os.path.exists('mismatch_array_4x4_modified.py'):
        print("ERROR: mismatch_array_4x4_modified.py not found!")
        sys.exit(1)
    
    # Generate matrix
    wrapper = MatrixWrapper(config_file)
    wrapper.generate_matrix(output_file)
    
    print(f"\nTo view:")
    print(f"  klayout {output_file}")


if __name__ == "__main__":
    main()