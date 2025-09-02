#!/bin/bash
# Script para corregir el error en mismatch_array_4x4_modified.py

# Cambiar al directorio correcto
cd /foss/designs/MissMatch/design_data/python/layout_transitor_matrix_automatic_gen/

# Hacer backup del archivo original
cp mismatch_array_4x4_modified.py mismatch_array_4x4_modified.py.backup

# Corregir el error: cambiar '$pattern_file' por 'pattern_file'
sed -i "s/if '\$pattern_file' in globals():/if 'pattern_file' in globals():/" mismatch_array_4x4_modified.py

echo "✅ Archivo corregido. El error del $ ha sido removido."

# Verificar el cambio
echo "Verificando la corrección:"
grep "if 'pattern_file' in globals():" mismatch_array_4x4_modified.py

# Test rápido con un array simple
echo "Ejecutando test de generación..."
cat > test_pattern.json << 'EOF'
{
  "metadata": {
    "transistor_W": 0.3,
    "transistor_L": 0.52,
    "guardring_spacing": 4.0,
    "array_rows": 4,
    "device_type": "nmos",
    "dummy_mode": "full"
  },
  "pattern_data": {}
}
EOF

# Ejecutar test directo
klayout -n sg13g2 -zz -r mismatch_array_4x4_modified.py -rd pattern_file=test_pattern.json

# Verificar si se generó algún archivo GDS
echo ""
echo "Archivos GDS generados:"
ls -la *.gds 2>/dev/null || echo "❌ No se generaron archivos GDS"

# Si el test funcionó, ejecutar la matriz completa
if [ -f "mismatch_array_4x4_nmos.gds" ]; then
    echo ""
    echo "✅ Test exitoso! Ahora ejecutando matriz completa..."
    klayout -zz -r matrix_wrapper.py -rd config_file=matrix_config_5x5.json -rd output=matrix_5x5_fixed.gds
else
    echo ""
    echo "⚠️ El test falló. Revisando output detallado..."
    echo "Ejecuta manualmente con -log para ver errores:"
    echo "klayout -n sg13g2 -zz -r mismatch_array_4x4_modified.py -rd pattern_file=test_pattern.json -log"
fi