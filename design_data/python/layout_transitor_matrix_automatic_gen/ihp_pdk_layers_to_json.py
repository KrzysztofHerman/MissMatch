import xml.etree.ElementTree as ET
import json
import re

def hex_to_rgb_list(hex_color):
    """
    Converts a hexadecimal color format (e.g., '#RRGGBB') to a list of
    RGB values normalized between 0.0 and 1.0.
    """
    hex_color = hex_color.lstrip('#')
    # Convert the R, G, and B components to integers and normalize them by dividing by 255.
    return [round(int(hex_color[i:i+2], 16) / 255.0, 2) for i in (0, 2, 4)]

def convert_ihp_xml_to_json(xml_file_path):
    """
    Parses an IHP PDK layer properties XML file and converts it into a
    JSON data structure.

    Args:
        xml_file_path (str): The path to the input XML file.

    Returns:
        str: A JSON formatted string representing the layer data, or None on error.
    """
    try:
        tree = ET.parse(xml_file_path)
        root = tree.getroot()
    except (ET.ParseError, FileNotFoundError) as e:
        print(f"Error: {e}")
        return None

    layers_data = {"layers": []}
    # We use a set to track the base layers we have already processed
    # to avoid duplicates in the output (e.g., Metal1.drawing, Metal1.pin, etc.).
    processed_base_layers = set()

    # Iterate over each <properties> element in the XML file.
    for properties_element in root.findall('properties'):
        name_tag = properties_element.find('name')
        source_tag = properties_element.find('source')
        fill_color_tag = properties_element.find('fill-color')

        # Ensure the necessary tags exist.
        if name_tag is not None and source_tag is not None and fill_color_tag is not None:
            full_layer_name = name_tag.text
            
            # Extract the base name of the layer (e.g., "Metal1" from "Metal1.drawing").
            base_name_match = re.match(r"([a-zA-Z0-9_]+)", full_layer_name)
            if not base_name_match:
                continue
            
            base_name = base_name_match.group(1)

            # If we have already processed this base layer, skip it.
            if base_name in processed_base_layers:
                continue
            
            processed_base_layers.add(base_name)

            # Split the text of the <source> tag to get GDS layer and datatype.
            try:
                gds_layer, gds_datatype = map(int, source_tag.text.split('/'))
            except (ValueError, AttributeError):
                continue # Skip if the source format is invalid

            # Get the fill color and convert it.
            color = hex_to_rgb_list(fill_color_tag.text)
            
            # NOTE: 'thickness' and 'zmin' values are not present in the XML file.
            # Placeholder/example values are used. You will need to replace these
            # with the correct values from your PDK's documentation.
            layer_info = {
                "name": base_name,
                "gds_layer": gds_layer,
                "gds_datatype": gds_datatype,
                "thickness": 0.2,  # <-- PLACEHOLDER VALUE
                "zmin": 0.2,       # <-- PLACEHOLDER VALUE
                "color": color
            }
            layers_data["layers"].append(layer_info)

    # Convert the Python dictionary to a JSON string with indented formatting.
    return json.dumps(layers_data, indent=2)

# --- START OF EXECUTION ---
# Name of the input XML file
xml_filename = 'sg13g2.lyp'

# Call the function to perform the conversion.
json_output = convert_ihp_xml_to_json(xml_filename)

# If the conversion was successful, print the result and save it to a file.
if json_output:
    print(json_output)
    
    # Save the output to a new .json file.
    output_filename = 'ihp_pdk_layers.json'
    with open(output_filename, 'w') as f:
        f.write(json_output)
    print(f"\nOutput saved to '{output_filename}'")
