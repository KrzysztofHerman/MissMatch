#!/bin/bash
# Script para corregir TODAS las instancias del error $pattern_file

cd /foss/designs/MissMatch/design_data/python/layout_transitor_matrix_automatic_gen/

echo "Buscando todas las instancias de '\$pattern_file' en el archivo..."
grep -n "\$pattern_file" mismatch_array_4x4_modified.py

echo ""
echo "Corrigiendo TODAS las instancias..."

# Reemplazar TODAS las ocurrencias de '$pattern_file' con 'pattern_file'
sed -i "s/'\$pattern_file'/'pattern_file'/g" mismatch_array_4x4_modified.py

echo "✅ Todas las instancias corregidas"
echo ""
echo "Verificando que no queden más instancias con el error:"
grep "\$pattern_file" mismatch_array_4x4_modified.py || echo "✅ No se encontraron más instancias con $"

echo ""
echo "Ejecutando test nuevamente..."
cat > test_simple.json << 'EOF'
{
  "metadata": {
    "transistor_W": 0.5,
    "transistor_L": 0.5,
    "guardring_spacing": 4.0,
    "array_rows": 4,
    "device_type": "nmos",
    "dummy_mode": "full"
  },
  "pattern_data": {}
}
EOF

# Ejecutar test
klayout -n sg13g2 -zz -r mismatch_array_4x4_modified.py -rd pattern_file=test_simple.json

# Verificar resultado
echo ""
echo "Verificando archivos generados:"
ls -la mismatch_array_4x4_nmos*.gds 2>/dev/null

if [ -f "mismatch_array_4x4_nmos.gds" ]; then
    echo ""
    echo "✅ ¡ÉXITO! El generador base funciona correctamente"
    echo ""
    echo "Ahora ejecutando la matriz completa 5x5..."
    klayout -zz -r matrix_wrapper.py -rd config_file=matrix_config_5x5.json -rd output=matrix_5x5_fixed.gds
    
    if [ -f "matrix_5x5_fixed.gds" ]; then
        echo "✅ ¡Matriz 5x5 generada exitosamente!"
        ls -lh matrix_5x5_fixed.gds
    fi
else
    echo "❌ Todavía hay problemas. Revisando el error específico..."
fi