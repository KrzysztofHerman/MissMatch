#!/usr/bin/env python3
"""
Script ultra simple para localizar errores M1.b
Funciona con cualquier versión de KLayout
"""

import pya

def find_m1_violations(gds_file):
    """Localiza violaciones M1 de forma simple"""
    
    print("\n" + "="*60)
    print("BÚSQUEDA DE VIOLACIONES M1.b")
    print("="*60)
    
    # Cargar layout
    layout = pya.Layout()
    layout.read(gds_file)
    
    # Layer de Metal1
    m1_layer = layout.layer(8, 0)
    
    # Celda principal
    top_cell = layout.top_cell()
    
    # Crear región con todos los M1
    m1_region = pya.Region(top_cell.begin_shapes_rec(m1_layer))
    
    # Space check básico - 180nm = 0.18um
    violations = m1_region.space_check(180)  # en database units (nm)
    
    print(f"Archivo: {gds_file}")
    print(f"Celda: {top_cell.name}")
    print(f"Espaciado mínimo M1: 0.18 μm")
    print(f"Violaciones encontradas: {violations.count()}")
    
    if violations.count() > 0:
        print("\n" + "-"*60)
        print("UBICACIÓN APROXIMADA DE VIOLACIONES:")
        print("-"*60)
        
        # Obtener el bounding box de las violaciones
        violations_bbox = violations.bbox()
        if violations_bbox:
            min_x = violations_bbox.left * layout.dbu
            max_x = violations_bbox.right * layout.dbu
            min_y = violations_bbox.bottom * layout.dbu
            max_y = violations_bbox.top * layout.dbu
            
            print(f"\nRango de violaciones:")
            print(f"  X: {min_x:.2f} - {max_x:.2f} μm")
            print(f"  Y: {min_y:.2f} - {max_y:.2f} μm")
            
            # Estimar qué matrices están afectadas
            print("\nMatrices probablemente afectadas (matriz 5x5):")
            
            # Configuración de la matriz
            w_values = [0.155, 0.3, 0.60, 1.20, 2.40]
            l_values = [2.080, 1.040, 0.520, 0.260, 0.130]
            
            # Asumiendo ~20μm por subarray
            col_start = int(min_x / 20)
            col_end = int(max_x / 20)
            row_start = int(min_y / 20)
            row_end = int(max_y / 20)
            
            for row in range(row_start, min(row_end + 1, 5)):
                for col in range(col_start, min(col_end + 1, 5)):
                    matrix_num = row * 5 + (5 - col)
                    if row < len(w_values) and col < len(l_values):
                        print(f"  Matriz #{matrix_num}: W={w_values[row]}μm, L={l_values[4-col]}μm")
        
        # Analizar patrón de violaciones
        print("\n" + "-"*60)
        print("ANÁLISIS DEL PATRÓN:")
        print("-"*60)
        
        # Crear una lista simple de puntos de violación
        violation_points = []
        i = 0
        for edge in violations.each():
            i += 1
            if i > 10:  # Limitar a 10 para no saturar
                break
            # edge es un EdgePair, intentar obtener información básica
            try:
                # Intentar diferentes métodos según la versión
                bbox = edge.bbox() if hasattr(edge, 'bbox') else None
                if bbox:
                    cx = bbox.center().x * layout.dbu
                    cy = bbox.center().y * layout.dbu
                    violation_points.append((cx, cy))
            except:
                pass
        
        if violation_points:
            print(f"Primeras {len(violation_points)} violaciones:")
            for i, (x, y) in enumerate(violation_points):
                print(f"  {i+1}. Cerca de ({x:.2f}, {y:.2f}) μm")
                
                # Identificar si es zona de dummy
                local_x = x % 20
                if local_x < 4:
                    print(f"     → Probable dummy IZQUIERDO")
                elif local_x > 16:
                    print(f"     → Probable dummy DERECHO")
    
    print("\n" + "="*60)
    print("SOLUCIONES SUGERIDAS:")
    print("="*60)
    
    print("""
Para transistores con W ≤ 0.3μm:
1. En connect_dummies_to_vss():
   - Cambiar: bar_y = t['y'] - self.dbu(0.4)
   - Por:     bar_y = t['y'] - self.dbu(0.8)  # Mayor separación

2. En route_dummies_to_guardring():
   - Cambiar: vss_x = bottom_dummy['x'] - self.dbu(3.7)
   - Por:     vss_x = bottom_dummy['x'] - self.dbu(4.5)  # Más lejos

3. Buscar líneas con "is_min_size" y ajustar:
   - Cambiar umbral de 1.1 a 0.3
   - Aumentar separaciones para W ≤ 0.3
""")
    
    return violations.count()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        gds_file = sys.argv[1]
        violations = find_m1_violations(gds_file)
        
        if violations == 0:
            print("\n✅ No hay violaciones M1.b!")
        else:
            print(f"\n⚠️ Se encontraron {violations} violaciones M1.b")
            print("Aplica las correcciones sugeridas y regenera la matriz.")
    else:
        print("Uso: python locate_m1_errors.py archivo.gds")
