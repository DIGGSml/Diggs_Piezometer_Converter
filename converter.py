import pandas as pd
from datetime import datetime
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom
from pathlib import Path

def create_base_structure():
    # Create root element with updated namespaces and schema
    root = Element('Diggs', {
        'xmlns': 'http://diggsml.org/schemas/2.6',
        'xmlns:diggs': 'http://diggsml.org/schemas/2.6',
        'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
        'xmlns:xlink': 'http://www.w3.org/1999/xlink',
        'xmlns:gml': 'http://www.opengis.net/gml/3.2',
        'xsi:schemaLocation': 'http://diggsml.org/schemas/2.6 https://diggsml.org/schema-dev/Diggs.xsd',
        'gml:id': 'piez1'
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
    
    # Add name
    name = SubElement(well_elem, 'gml:name')
    name.text = f'{sensor_id} Piezometer'
    
    # Add required investigation target
    inv_target = SubElement(well_elem, 'investigationTarget')
    inv_target.text = 'Natural Ground'
    
    # Add required project reference
    proj_ref = SubElement(well_elem, 'projectRef')
    proj_ref.set('xlink:href', '#p1')
    
    # Add reference point
    ref_point = SubElement(well_elem, 'referencePoint')
    point_loc = SubElement(ref_point, 'PointLocation')
    point_loc.set('gml:id', f'p2-{sensor_id}')
    
    pos = SubElement(point_loc, 'gml:pos')
    pos.set('srsDimension', '3')
    pos.set('srsName', 'urn:diggs:def:crs:DIGGS:0.1:4326_5702')
    pos.set('uomLabels', 'dega dega ftUS')
    pos.set('axisLabels', 'latitude longitude height')
    pos.text = f'{lat} {lon} 0'
    
    # Add required centerLine
    center_line = SubElement(well_elem, 'centerLine')
    linear_extent = SubElement(center_line, 'LinearExtent')
    linear_extent.set('gml:id', f'cl-{sensor_id}')
    
    pos_list = SubElement(linear_extent, 'gml:posList')
    pos_list.set('srsDimension', '3')
    pos_list.set('srsName', 'urn:diggs:def:crs:DIGGS:0.1:4326_5702')
    pos_list.set('uomLabels', 'dega dega ftUS')
    pos_list.set('axisLabels', 'latitude longitude height')
    pos_list.text = f'{lat} {lon} 0 {lat} {lon} -50'
    
        # Add linear referencing with correct namespace
    lin_ref = SubElement(well_elem, 'linearReferencing')
    lsrs = SubElement(lin_ref, 'LinearSpatialReferenceSystem')
    lsrs.set('gml:id', f'Boring1_lsrs_{sensor_id}')
    
    identifier = SubElement(lsrs, 'gml:identifier')
    identifier.set('codeSpace', 'Geosetta')
    identifier.text = f'Boring1_lsrs_{sensor_id}'
    
    # Create linearElement with correct namespace
    lin_elem = SubElement(lsrs, 'linearElement')
    lin_elem.set('xmlns', 'http://www.opengis.net/gml/3.3/lr')
    lin_elem.set('xlink:href', f'#cl-{sensor_id}')
    
    # Create lrm with correct namespace
    lrm = SubElement(lsrs, 'lrm')
    lrm.set('xmlns', 'http://www.opengis.net/gml/3.3/lr')
    
    lrm_method = SubElement(lrm, 'LinearReferencingMethod')
    lrm_method.set('gml:id', f'Boring1_lsrs_lrm_{sensor_id}')
    
    lrm_name = SubElement(lrm_method, 'name')
    lrm_name.text = 'chainage'
    lrm_type = SubElement(lrm_method, 'type')
    lrm_type.text = 'absolute'
    lrm_units = SubElement(lrm_method, 'units')
    lrm_units.text = 'ft'
    
    # Add empty samplingFeatureRef
    SubElement(well_elem, 'samplingFeatureRef')
    
    # Add well opening
    opening = SubElement(well_elem, 'opening')
    well_opening = SubElement(opening, 'WellOpening')
    well_opening.set('gml:id', 'wo1')
    
    open_interval = SubElement(well_opening, 'openInterval')
    interval_extent = SubElement(open_interval, 'LinearExtent')
    interval_extent.set('gml:id', 'rzl')
    
    interval_pos = SubElement(interval_extent, 'gml:posList')
    interval_pos.text = '45 50'
    
    return well_elem

def add_measurements(root, df, sensor_id):
    measurement = SubElement(root, 'measurement')
    monitor = SubElement(measurement, 'Monitor')
    monitor.set('gml:id', f'Water_Levels_{sensor_id}')
    
    # Add required investigation target
    inv_target = SubElement(monitor, 'investigationTarget')
    inv_target.text = 'Natural Ground'
    
    # Add required project reference
    proj_ref = SubElement(monitor, 'projectRef')
    proj_ref.set('xlink:href', '#p1')
    
    reading = SubElement(monitor, 'reading')
    reading_elem = SubElement(reading, 'Reading')
    reading_elem.set('gml:id', f'Reading_Water_Levels_{sensor_id}')
    
    # Add required response zone location
    resp_zone = SubElement(reading_elem, 'responseZoneLocation')
    resp_zone.set('xlink:href', '#rzl')
    
    outcome = SubElement(reading_elem, 'outcome')
    result = SubElement(outcome, 'MonitorResult')
    result.set('gml:id', f'Result_Water_Levels_{sensor_id}')
    
    # Add time domain
    time_domain = SubElement(result, 'timeDomain')
    time_pos_list = SubElement(time_domain, 'TimePositionList')
    time_pos_list.set('gml:id', f'TP_Water_Levels_{sensor_id}')
    
    # Format timestamps in ISO format
    time_list = SubElement(time_pos_list, 'timePositionList')
    time_list.text = ' '.join(df['Date'].dt.strftime('%Y-%m-%dT%H:%M:%S'))
    
    # Add results
    results = SubElement(result, 'results')
    result_set = SubElement(results, 'ResultSet')
    
    # Add parameters
    parameters = SubElement(result_set, 'parameters')
    prop_params = SubElement(parameters, 'PropertyParameters')
    prop_params.set('gml:id', f'pp_Water_Levels_{sensor_id}_1')
    
    properties = SubElement(prop_params, 'properties')
    
    # Property definitions with updated structure
    properties_data = [
        {
            'name': 'Pressure (ft H₂O)',
            'type': 'double',
            'class': 'water_depth',
            'uom': 'ft',
            'column': 'Pressure (ft H₂O)'
        },
        {
            'name': 'Elevation H₂O (ft)',
            'type': 'double',
            'class': 'water_elev',
            'uom': 'ft',
            'column': 'Elevation H₂O (ft)'
        },
        {
            'name': 'Temperature (deg F)',
            'type': 'double',
            'class': 'temperature',
            'uom': 'degF',
            'column': 'Temperature (deg F)'
        }
    ]
    
    # Create property elements
    for idx, prop in enumerate(properties_data, 1):
        property_elem = SubElement(properties, 'Property')
        property_elem.set('index', str(idx))
        property_elem.set('gml:id', f'prop{idx}_Water_Levels_{sensor_id}')
        
        prop_name = SubElement(property_elem, 'propertyName')
        prop_name.text = prop['name']
        
        type_data = SubElement(property_elem, 'typeData')
        type_data.text = prop['type']
        
        prop_class = SubElement(property_elem, 'propertyClass')
        prop_class.set('codeSpace', 'https://diggsml.org/def/codes/DIGGS/0.1/properties.xml')
        prop_class.text = prop['class']
        
        uom = SubElement(property_elem, 'uom')
        uom.text = prop['uom']
    
    # Add data values as comma-separated tuples
    data_values = SubElement(result_set, 'dataValues')
    values = []
    for _, row in df.iterrows():
        tuple_values = [str(row[prop['column']]) for prop in properties_data]
        values.append(','.join(tuple_values))
    data_values.text = ' '.join(values)
    
    # Add sensor information
    sensor = SubElement(reading_elem, 'sensor')
    sensor_elem = SubElement(sensor, 'Sensor')
    sensor_elem.set('gml:id', sensor_id)
    
    sensor_name = SubElement(sensor_elem, 'gml:name')
    sensor_name.text = sensor_id
    
    sensor_class = SubElement(sensor_elem, 'class')
    sensor_class.text = 'Pressure transducer'
    
    detector = SubElement(sensor_elem, 'detector')
    detector_elem = SubElement(detector, 'Detector')
    detector_elem.set('gml:id', 'metric')
    
    measurand = SubElement(detector_elem, 'measurand')
    measurand.set('codeSpace', 'https://diggsml.org/def/codes/DIGGS/0.1/properties.xml')
    measurand.text = 'water_depth_calc'

def convert_csv_to_xml(input_file):
    try:
        # Read the CSV file
        df = pd.read_csv(input_file)
        df['Date'] = pd.to_datetime(df['Date'])
        
        # Get the first row where Latitude and Longitude are not empty
        first_valid_row = df[df['Latitude'].notna() & df['Longitude'].notna()].iloc[0]
        
        # Get sensor info using the first valid row
        sensor_info = {
            'Sensor': first_valid_row['Sensor'],
            'Latitude': first_valid_row['Latitude'],
            'Longitude': first_valid_row['Longitude']
        }
        
        # Format coordinates to 8 decimal places
        lat = format(float(sensor_info['Latitude']), '.8f')
        lon = format(float(sensor_info['Longitude']), '.8f')
        
        print(f"Processing file for sensor {sensor_info['Sensor']} with coordinates: Lat={lat}, Lon={lon}")
        
        # Create base XML structure
        root = create_base_structure()
        
        # Add project
        add_project(root)
        
        # Add well information with verified coordinates
        add_well(root, lat, lon, sensor_info['Sensor'])
        
        # Add measurements
        add_measurements(root, df, sensor_info['Sensor'])
        
        # Pretty print XML
        xml_str = tostring(root, encoding='unicode')
        pretty_xml = minidom.parseString(xml_str).toprettyxml(indent="    ")
        
        return pretty_xml
    except Exception as e:
        print(f"Error processing {input_file}: {str(e)}")
        print(f"Error details: {str(e.__class__.__name__)}")
        import traceback
        traceback.print_exc()
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

if __name__ == "__main__":
    input_folder = "Piezometers_CSVs"    # Folder containing CSV files
    output_folder = "DIGGS_Piezometers"  # Folder where XML files will be saved
    
    process_folder(input_folder, output_folder)