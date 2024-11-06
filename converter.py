import pandas as pd
from datetime import datetime
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom
from io import StringIO
import os
from pathlib import Path

def create_base_structure():
    # Create root element with all necessary namespaces
    root = Element('Diggs', {
        'xmlns': 'http://diggsml.org/schemas/2.5.a',
        'xmlns:diggs': 'http://diggsml.org/schemas/2.5.a',
        'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
        'xmlns:xlink': 'http://www.w3.org/1999/xlink',
        'xmlns:gml': 'http://www.opengis.net/gml/3.2'
    })
    
    # Add document information
    doc_info = SubElement(root, 'documentInformation')
    doc_info_elem = SubElement(doc_info, 'DocumentInformation')
    doc_info_elem.set('gml:id', 'd1')
    creation_date = SubElement(doc_info_elem, 'creationDate')
    creation_date.text = datetime.now().strftime('%Y-%m-%d')
    
    return root

def add_project(root):
    project = SubElement(root, 'project')
    proj = SubElement(project, 'Project')
    proj.set('gml:id', 'p1')
    name = SubElement(proj, 'gml:name')
    name.text = 'Monitoring Project'
    return proj

def add_well(root, lat, lon, sensor_id):
    well = SubElement(root, 'samplingFeature')
    well_elem = SubElement(well, 'Well')
    well_elem.set('gml:id', f'Piezometer_{sensor_id}')
    
    name = SubElement(well_elem, 'gml:name')
    name.text = f'{sensor_id} Piezometer'
    
    ref_point = SubElement(well_elem, 'referencePoint')
    point_loc = SubElement(ref_point, 'PointLocation')
    point_loc.set('gml:id', f'p2-{sensor_id}')
    
    pos = SubElement(point_loc, 'gml:pos')
    pos.set('srsDimension', '3')
    pos.set('srsName', 'urn:diggs:def:crs:DIGGS:0.1:4326_5702')
    pos.set('uomLabels', 'dega dega ftUS')
    pos.set('axisLabels', 'latitude longitude height')
    pos.text = f'{lat} {lon} 0'
    
    return well_elem

def add_measurements(root, df, sensor_id):
    measurement = SubElement(root, 'measurement')
    monitor = SubElement(measurement, 'Monitor')
    monitor.set('gml:id', f'Water_Levels_{sensor_id}')
    
    reading = SubElement(monitor, 'reading')
    reading_elem = SubElement(reading, 'Reading')
    reading_elem.set('gml:id', f'Reading_Water_Levels_{sensor_id}')
    
    outcome = SubElement(reading_elem, 'outcome')
    result = SubElement(outcome, 'MonitorResult')
    result.set('gml:id', f'Result_Water_Levels_{sensor_id}')
    
    # Add time domain
    time_domain = SubElement(result, 'timeDomain')
    time_pos_list = SubElement(time_domain, 'TimePositionList')
    time_pos_list.set('gml:id', f'TP_Water_Levels_{sensor_id}')
    
    # Format timestamps
    time_list = SubElement(time_pos_list, 'timePositionList')
    time_list.text = ' '.join(df['Date'].dt.strftime('%Y/%m/%d %H:%M'))
    
    # Add results
    results = SubElement(result, 'results')
    
    # Property definitions
    properties_data = [
        {
            'name': 'Pressure (ft H₂O)',
            'uom': 'ft H₂O',
            'column': 'Pressure (ft H₂O)'
        },
        {
            'name': 'Elevation H₂O (ft)',
            'uom': 'ft',
            'column': 'Elevation H₂O (ft)'
        },
        {
            'name': 'Temperature (deg F)',
            'uom': 'deg F',
            'column': 'Temperature (deg F)'
        }
    ]
    
    # Create a separate ResultSet for each property
    for idx, prop in enumerate(properties_data, 1):
        result_set = SubElement(results, 'ResultSet')
        
        # Add parameters
        parameters = SubElement(result_set, 'parameters')
        prop_params = SubElement(parameters, 'PropertyParameters')
        prop_params.set('gml:id', f'pp_Water_Levels_{sensor_id}_{idx}')
        
        properties = SubElement(prop_params, 'properties')
        property_elem = SubElement(properties, 'Property')
        property_elem.set('index', str(idx))
        property_elem.set('gml:id', f'prop{idx}_Water_Levels_{sensor_id}')
        
        prop_name = SubElement(property_elem, 'gml:name')
        prop_name.text = prop['name']
        
        type_data = SubElement(property_elem, 'typeData')
        type_data.text = 'double'
        
        uom = SubElement(property_elem, 'uom')
        uom.text = prop['uom']
        
        # Add data values for this property
        data_values = SubElement(result_set, 'dataValues')
        values = ' '.join(df[prop['column']].astype(str))
        data_values.text = values

    # Add sensor information after outcome
    sensor = SubElement(reading_elem, 'sensor')
    sensor_elem = SubElement(sensor, 'Sensor')
    sensor_elem.set('gml:id', sensor_id)
    
    sensor_name = SubElement(sensor_elem, 'gml:name')
    sensor_name.text = sensor_id
    
    sensor_class = SubElement(sensor_elem, 'class')
    sensor_class.text = 'Piezometer'
    
    detector = SubElement(sensor_elem, 'detector')
    detector_elem = SubElement(detector, 'Detector')
    detector_elem.set('gml:id', 'metric')
    
    measurand = SubElement(detector_elem, 'measurand')
    measurand.set('codeSpace', 'http://diggsml.org/prope/properties-diggs.xml#water_depth')
    measurand.text = 'Water Depth'

def convert_csv_to_xml(input_file):
    try:
        # Read the tab-separated CSV file
        df = pd.read_csv(input_file)
        df['Date'] = pd.to_datetime(df['Date'])
        
        # Create base XML structure
        root = create_base_structure()
        
        # Add project
        add_project(root)
        
        # Get unique sensor info
        sensor_info = df[['Latitude', 'Longitude', 'Sensor']].iloc[0]
        
        # Add well information
        add_well(root, sensor_info['Latitude'], sensor_info['Longitude'], sensor_info['Sensor'])
        
        # Add measurements
        add_measurements(root, df, sensor_info['Sensor'])
        
        # Pretty print XML
        xml_str = tostring(root, encoding='unicode')
        pretty_xml = minidom.parseString(xml_str).toprettyxml(indent="    ")
        
        return pretty_xml
    except Exception as e:
        print(f"Error processing {input_file}: {str(e)}")
        return None

def process_folder(input_folder, output_folder):
    # Create output folder if it doesn't exist
    Path(output_folder).mkdir(parents=True, exist_ok=True)
    
    # Process each CSV file in the input folder
    processed_count = 0
    error_count = 0
    
    for csv_file in Path(input_folder).glob('*.csv'):
        print(f"Processing {csv_file.name}...")
        
        # Generate output file path with same name but .xml extension
        output_file = Path(output_folder) / csv_file.with_suffix('.xml').name
        
        # Convert CSV to XML
        xml_output = convert_csv_to_xml(csv_file)
        
        if xml_output:
            # Save XML file
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(xml_output)
            processed_count += 1
            print(f"Successfully created {output_file.name}")
        else:
            error_count += 1
    
    print(f"\nProcessing complete!")
    print(f"Files processed successfully: {processed_count}")
    print(f"Files with errors: {error_count}")

# Example usage
if __name__ == "__main__":
    input_folder = "/workspaces/Diggs_Piezometer_Converter/Piezometers_CSVs"    # Folder containing CSV files
    output_folder = "/workspaces/Diggs_Piezometer_Converter/DIGGS_Piezometers"  # Folder where XML files will be saved
    
    process_folder(input_folder, output_folder)