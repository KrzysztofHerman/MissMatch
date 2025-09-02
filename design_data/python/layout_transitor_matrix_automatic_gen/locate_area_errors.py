#!/usr/bin/env python3
"""
Script to locate minimum area and aspect ratio violations in metal layers
For IHP SG13G2 PDK - finds M#.j/k and TM#.c/d errors
"""

import pya

def analyze_metal_area_violations(gds_file):
    """Analyze metal layers for minimum area violations"""
    
    print("\n" + "="*60)
    print("METAL AREA AND ASPECT RATIO VIOLATION ANALYSIS")
    print("="*60)
    print(f"File: {gds_file}")
    
    # Load layout
    layout = pya.Layout()
    layout.read(gds_file)
    
    # Get top cell
    top_cell = layout.top_cell()
    if not top_cell:
        print("ERROR: No top cell found")
        return
    
    print(f"Top cell: {top_cell.name}")
    
    # Define layers and their minimum area requirements (in um²)
    # These are typical values - adjust based on actual PDK rules
    metal_layers = {
        'M1': {'layer': (8, 0), 'min_area': 0.09, 'max_aspect': 3.0},
        'M2': {'layer': (10, 0), 'min_area': 0.09, 'max_aspect': 3.0},
        'M3': {'layer': (30, 0), 'min_area': 0.09, 'max_aspect': 3.0},
        'M4': {'layer': (50, 0), 'min_area': 0.16, 'max_aspect': 3.0},
        'M5': {'layer': (67, 0), 'min_area': 0.16, 'max_aspect': 3.0},
        'TM1': {'layer': (126, 0), 'min_area': 2.0, 'max_aspect': 5.0},
        'TM2': {'layer': (134, 0), 'min_area': 4.0, 'max_aspect': 5.0}
    }
    
    violations_found = {}
    
    print("\nChecking each metal layer...")
    print("-" * 60)
    
    for metal_name, specs in metal_layers.items():
        layer_num, datatype = specs['layer']
        min_area_um2 = specs['min_area']
        max_aspect = specs['max_aspect']
        
        # Get layer index
        layer = layout.layer(layer_num, datatype)
        
        # Create region with all shapes from this layer
        region = pya.Region(top_cell.begin_shapes_rec(layer))
        
        # Convert to database units for area calculation
        min_area_dbu2 = min_area_um2 / (layout.dbu * layout.dbu)
        
        violations = []
        shape_count = 0
        
        # Check each polygon in the region
        for polygon in region.each():
            shape_count += 1
            area_dbu2 = polygon.area()
            area_um2 = area_dbu2 * layout.dbu * layout.dbu
            
            # Get bounding box for aspect ratio and position
            bbox = polygon.bbox()
            width = bbox.width() * layout.dbu
            height = bbox.height() * layout.dbu
            center_x = bbox.center().x * layout.dbu
            center_y = bbox.center().y * layout.dbu
            
            # Calculate aspect ratio
            if height > 0:
                aspect_ratio = width / height if width > height else height / width
            else:
                aspect_ratio = float('inf')
            
            # Check for violations
            violation_type = None
            
            if area_um2 < min_area_um2:
                violation_type = f"Area violation ({area_um2:.4f} < {min_area_um2} um²)"
            elif aspect_ratio > max_aspect:
                violation_type = f"Aspect ratio violation ({aspect_ratio:.2f} > {max_aspect})"
            
            if violation_type:
                violations.append({
                    'type': violation_type,
                    'area': area_um2,
                    'width': width,
                    'height': height,
                    'aspect': aspect_ratio,
                    'x': center_x,
                    'y': center_y,
                    'bbox': bbox
                })
        
        # Report findings for this layer
        if violations:
            print(f"\n{metal_name} Layer ({layer_num},{datatype}):")
            print(f"  Total shapes: {shape_count}")
            print(f"  Violations found: {len(violations)}")
            print(f"  Minimum area required: {min_area_um2} um²")
            print(f"  Maximum aspect ratio: {max_aspect}")
            
            violations_found[metal_name] = violations
            
            # Show details of each violation
            for i, viol in enumerate(violations[:5], 1):  # Limit to first 5
                print(f"\n  Violation #{i}:")
                print(f"    Type: {viol['type']}")
                print(f"    Location: ({viol['x']:.2f}, {viol['y']:.2f}) um")
                print(f"    Size: {viol['width']:.3f} x {viol['height']:.3f} um")
                print(f"    Area: {viol['area']:.4f} um²")
                print(f"    Aspect ratio: {viol['aspect']:.2f}")
                
                # Determine which matrix this belongs to (5x5 grid)
                matrix_col = int(viol['x'] / 20)
                matrix_row = int(viol['y'] / 20)
                if matrix_row < 5 and matrix_col < 5:
                    matrix_num = matrix_row * 5 + (5 - matrix_col)
                    print(f"    Matrix: #{matrix_num} [row {matrix_row}, col {matrix_col}]")
                    
                    # Determine W and L values
                    w_values = [0.155, 0.3, 0.60, 1.20, 2.40]
                    l_values = [2.080, 1.040, 0.520, 0.260, 0.130]
                    if matrix_row < len(w_values) and matrix_col < len(l_values):
                        print(f"    Transistor params: W={w_values[matrix_row]}um, L={l_values[4-matrix_col]}um")
            
            if len(violations) > 5:
                print(f"\n  ... and {len(violations)-5} more violations")
        else:
            print(f"\n{metal_name}: ✓ No violations found")
    
    return violations_found

def suggest_fixes_for_violations(violations_dict):
    """Suggest fixes based on violation patterns"""
    
    print("\n" + "="*60)
    print("SUGGESTED FIXES")
    print("="*60)
    
    if not violations_dict:
        print("No violations found - design is clean!")
        return
    
    # Analyze patterns
    has_m_violations = any(k.startswith('M') and not k.startswith('TM') for k in violations_dict.keys())
    has_tm_violations = any(k.startswith('TM') for k in violations_dict.keys())
    
    if has_m_violations:
        print("\nFor Metal layer violations (M1-M5):")
        print("-" * 40)
        print("""
Common causes and fixes:
1. Small metal pads at via connections:
   - Increase pad size around vias
   - Ensure minimum enclosure + margin
   - Example: Change enlarged(0.05) to enlarged(0.08)

2. Short metal stubs or fragments:
   - Extend or remove very short segments
   - Merge adjacent small shapes
   
3. Thin metal lines with high aspect ratio:
   - Increase width of long thin traces
   - Break long lines with vias if needed

Code locations to check in mismatch_array_4x4_modified.py:
- create_via_stack_* functions (via pad sizes)
- route_column_drains_tm1 (M1 bar dimensions)
- route_row_sources_tm2 (M1/M2 connections)
""")
    
    if has_tm_violations:
        print("\nFor TopMetal violations (TM1/TM2):")
        print("-" * 40)
        print("""
Common causes and fixes:
1. Individual small TM pads instead of continuous:
   - Merge individual pads into larger continuous pads
   - Current code may create separate pads per via
   
2. Minimum area not met (TM1: 2um², TM2: 4um²):
   - Increase TopMetal pad dimensions
   - Consolidate nearby pads

Code fixes needed:
- In create_vertical_via_array_m1_to_tm1():
  Create ONE continuous TM1 pad instead of individual pads
  
- In create_vertical_via_array_m1_to_tm2():
  Ensure TM2 pad is large enough (>4um²)

Example fix for TM1:
```python
# Instead of individual pads per via:
for via in vias:
    create_tm1_pad(via)  # BAD - creates small individual pads

# Use single continuous pad:
tm1_continuous = db.Box(
    x - tm1_width//2,
    min_y - margin,
    x + tm1_width//2, 
    max_y + margin
)
cell.shapes(self.layers['TopMetal1']).insert(tm1_continuous)  # GOOD
```
""")
    
    # Specific fixes based on violation locations
    print("\n" + "="*60)
    print("PRIORITY FIXES BASED ON YOUR VIOLATIONS:")
    print("="*60)
    
    priority = 1
    for metal_name, violations in violations_dict.items():
        if violations:
            avg_area = sum(v['area'] for v in violations) / len(violations)
            print(f"\n{priority}. Fix {metal_name} violations:")
            print(f"   - {len(violations)} shapes with area < required")
            print(f"   - Average violating area: {avg_area:.4f} um²")
            
            if metal_name in ['TM1', 'TM2']:
                print(f"   - ACTION: Consolidate {metal_name} pads in via arrays")
                print(f"   - Search for: create_vertical_via_array_m1_to_{metal_name.lower()}")
            else:
                print(f"   - ACTION: Increase {metal_name} pad sizes at vias")
                print(f"   - Search for: {metal_name.lower()}_pad = ")
            
            priority += 1

def main():
    """Main function"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python locate_area_errors.py <gds_file>")
        print("\nExample:")
        print("  python locate_area_errors.py matrix_5x5_25arrays.gds")
        return
    
    gds_file = sys.argv[1]
    
    # Analyze violations
    violations = analyze_metal_area_violations(gds_file)
    
    # Suggest fixes
    suggest_fixes_for_violations(violations)
    
    # Summary
    total_violations = sum(len(v) for v in violations.values())
    if total_violations > 0:
        print("\n" + "="*60)
        print(f"TOTAL: {total_violations} area/aspect violations found")
        print("="*60)
        print("\nNext steps:")
        print("1. Apply the suggested fixes to mismatch_array_4x4_modified.py")
        print("2. Regenerate the matrix")
        print("3. Re-run this script to verify fixes")
    else:
        print("\n✅ SUCCESS: No area/aspect violations found!")

if __name__ == "__main__":
    main()