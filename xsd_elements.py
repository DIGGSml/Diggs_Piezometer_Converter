import xml.etree.ElementTree as ET
import csv

# Path to the XSD file
xsd_path = '/workspaces/Diggs_Piezometer_Converter/Geotechnical.xsd'

# Path to the output CSV file
csv_output_path = '/workspaces/Diggs_Piezometer_Converter/xsd_elements.csv'

# Parse the XSD file
tree = ET.parse(xsd_path)
root = tree.getroot()

# Define the namespace (modify if your XSD uses a different one)
namespace = '{http://www.w3.org/2001/XMLSchema}'

# Initialize a list to store elements with their attributes
elements_data = []

# Recursively extract elements and attributes from the XSD
def extract_elements(element, parent_name=""):
    for child in element:
        if child.tag == f"{namespace}element":
            element_name = child.attrib.get('name', 'Unnamed')
            element_type = child.attrib.get('type', 'N/A')
            min_occurs = child.attrib.get('minOccurs', '1')
            max_occurs = child.attrib.get('maxOccurs', '1')
            parent = parent_name if parent_name else "Root"

            elements_data.append([parent, element_name, element_type, min_occurs, max_occurs])

            # Check if there are nested complex types
            if child.find(f"{namespace}complexType") is not None:
                extract_elements(child.find(f"{namespace}complexType"), element_name)

        # If it's a complexType directly in the XSD, handle its children
        elif child.tag == f"{namespace}complexType":
            extract_elements(child, parent_name)

# Start extraction from the root element
extract_elements(root)

# Write elements data to CSV
with open(csv_output_path, mode='w', newline='') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(["ParentElement", "ElementName", "Type", "MinOccurs", "MaxOccurs"])  # Header

    # Write each element's data as a row in the CSV
    for row in elements_data:
        writer.writerow(row)

print(f"Extraction complete. Data saved to {csv_output_path}")
