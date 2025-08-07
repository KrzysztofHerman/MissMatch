#!/bin/bash

# draw the pattern in the guy (testing just with 4x4)
python advanced_routing_gui.py &

# run klayout for automatic layout generation based .json file generated from GUI
klayout -n sg13g2 -zz -r mismatch_array_4x4_modified.py         -rd pattern_file="patron_columna0_debug.json"         -rd output="debug_columna0.gds"

# display layout
klayout mismatch_array_4x4_from_gui.gds &
