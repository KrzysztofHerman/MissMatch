#!/usr/bin/env python3
"""
Script para analizar y visualizar los errores M1.b en conexiones de dummies
"""

import pya

# Cargar el archivo GDS con errores
def analyze_m1_spacing(gds_file):
    """Analiza espaciado de Metal1 en el GDS"""
    
    # Crear layout y cargar archivo
    layout = pya.Layout()
    layout.read(gds_file)
    
    # Layer de Metal1 (8, 0)
    m1_layer = layout.layer(8, 0)
    
    # Obtener la celda principal
    top_cell = layout.top_cell()
    
    # Crear región con todos los shapes de M1
    m1_region = pya.Region(top_cell.begin_shapes_rec(m1_layer))
    
    # Verificar espaciado mínimo (0.18 μm = 180 nm)
    min_spacing_nm = 180
    
    # Encontrar violaciones de espaciado
    # Versión simplificada sin Metrics (compatible con más versiones de KLayout)
    violations = m1_region.space_check(min_spacing_nm)
    
    print(f"Analizando archivo: {gds_file}")
    print(f"Espaciado mínimo M1 requerido: {min_spacing_nm} nm")
    print(f"Violaciones encontradas: {violations.count()}")
    
    # Analizar ubicación de violaciones
    if violations.count() > 0:
        print("\nUbicación de violaciones:")
        # Convertir EdgePairs a polígonos para análisis
        violation_polygons = []
        for edge_pair in violations.each():
            # Obtener los puntos del edge pair
            p1 = edge_pair.p1
            p2 = edge_pair.p2
            
            # Calcular centro aproximado
            center_x = (p1.x + p2.x) / 2
            center_y = (p1.y + p2.y) / 2
            
            # Convertir a micrones
            center_x_um = center_x * layout.dbu
            center_y_um = center_y * layout.dbu
            
            violation_polygons.append({
                'x': center_x_um,
                'y': center_y_um
            })
        
        # Mostrar información de cada violación
        for i, viol in enumerate(violation_polygons):
            print(f"  Violación {i+1}:")
            print(f"    Posición aproximada: ({viol['x']:.2f}, {viol['y']:.2f}) μm")
            
            # Determinar en qué matriz está (5x5 grid)
            matrix_col = int(viol['x'] / 20)  # Asumiendo ~20μm por subarray
            matrix_row = int(viol['y'] / 20)
            
            print(f"    Probable matriz: [{matrix_row},{matrix_col}]")
            
            # Identificar si está cerca de dummies
            # Los dummies están en los bordes de cada subarray
            subarray_x = viol['x'] % 20
            subarray_y = viol['y'] % 20
            
            if subarray_x < 3 or subarray_x > 17:
                print(f"    -> Probablemente en columna de dummies")
            if subarray_y < 3 or subarray_y > 17:
                print(f"    -> Probablemente en fila de dummies")
    
    return violations

# Función para identificar patrones problemáticos
def identify_dummy_m1_issues():
    """Identifica problemas comunes en conexiones M1 de dummies"""
    
    print("\n" + "="*60)
    print("PROBLEMAS COMUNES EN CONEXIONES M1 DE DUMMIES:")
    print("="*60)
    
    issues = [
        {
            "problema": "M1 bar demasiado ancho para transistores pequeños",
            "descripción": "Para W≤0.3μm, el M1 bar de 2.32μm puede ser muy ancho",
            "solución": "Reducir m1_bar_width para transistores pequeños",
            "código": """
# En route_column_drains_tm1:
if TRANSISTOR_W <= 0.3:
    m1_bar_width = self.dbu(1.5)  # Reducido de 2.32
else:
    m1_bar_width = self.dbu(2.32)
"""
        },
        {
            "problema": "Conexiones E-shape muy cerca entre dummies adyacentes",
            "descripción": "El bar horizontal a y=-0.4μm puede quedar muy cerca",
            "solución": "Ajustar posición vertical del bar según tamaño",
            "código": """
# En connect_dummies_to_vss:
if TRANSISTOR_W <= 0.3:
    bar_y = trans_center_y - self.dbu(0.6)  # Más separación
else:
    bar_y = trans_center_y - self.dbu(0.4)
"""
        },
        {
            "problema": "M2 bus demasiado cerca del transistor",
            "descripción": "La posición x-3.7μm puede causar conflictos",
            "solución": "Ajustar offset según el tamaño del transistor",
            "código": """
# En route_dummies_to_guardring:
if TRANSISTOR_W <= 0.3:
    vss_x = bottom_dummy['x'] - self.dbu(4.2)  # Más lejos
else:
    vss_x = bottom_dummy['x'] - self.dbu(3.7)
"""
        }
    ]
    
    for i, issue in enumerate(issues, 1):
        print(f"\n{i}. {issue['problema']}")
        print(f"   {issue['descripción']}")
        print(f"   Solución: {issue['solución']}")
        print(f"   {issue['código']}")
    
    return issues

# Script principal
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        gds_file = sys.argv[1]
        violations = analyze_m1_spacing(gds_file)
    else:
        print("Uso: python debug_m1.py archivo.gds")
        
    # Mostrar problemas comunes
    identify_dummy_m1_issues()