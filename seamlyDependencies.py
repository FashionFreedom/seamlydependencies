#
'''
This script is used to extract the dependencies of a Seamly2d CAD file.
It is used to create a dependency graph of the CAD file.
'''

import xml.etree.ElementTree as ET
import os, re
from collections import defaultdict
import csv

import tkinter as tk
from tkinter import filedialog
import pprint

# get the directory of this script
script_dir = os.path.dirname(os.path.abspath(__file__))
# csv file is in the same directory as this scri
measurements_csv_file_path = os.path.join(script_dir, 'empty_measurements.csv')


# ------------------------------------------------------------
# GLOBAL VARIABLES
# ------------------------------------------------------------
# Global variable to track variable IDs
block_id_counter       = 1
measurement_id_counter = 1
var_id_counter         = -1

# ------------------------------------------------------------
# DICTIONARIES AND LISTS
# ------------------------------------------------------------
object_tags = ['root', 'measurements', 'm', 'variables', 'variable', 'draftBlock', 'calculation','point', 'line','spline','arc', 'elArc', 'operation', 'rotation', 'path', 'nodes', 'node', 'pieces', 'piece', 'data','line','patternInfo','grainline','iPaths', 'iPath', 'record', 'anchors', 'group', 'item']

skip_tags   = ['unit', 'version', 'description', 'notes', 'patternLabel']

display_attributes = ['implicit', 'description', 'mx', 'my', 'x', 'y','lineColor','lineType','lineWeight','showPointName','penStyle', 'alias', 'color', 'crossPoint']

id_attributes = ['basePoint', 'block', 'center', 'center1', 'center2','c1Center','c2Center', 'curve','point1', 'point2', 'point3', 'point4', 'firstPoint', 'secondPoint', 'thirdPoint', 'p1Line', 'p2Line', 'p1Line1',  'p2Line1','p1Line2', 'p2Line2', 'op']

formula_attributes = ['angle', 'angle1', 'angle2', 'center', 'center1', 'center2','c1Radius', 'c2Radius', 'formula', 'length', 'length1', 'length2', 'radius', 'radius1', 'radius2', 'rotation', 'width']

point_attributes = ['basePoint', 'center', 'center1', 'center2', 'point1', 'point2', 'point3', 'point4', 'firstPoint', 'secondPoint']

line_attributes = ['firstPoint', 'secondPoint', 'basePoint', 'width']

arc_attributes = ['center', 'radius', 'angle1', 'angle2']

spline_attributes = ['point1', 'point2', 'point3', 'point4', 'firstPoint', 'secondPoint', 'basePoint',  'width']

# ------------------------------------------------------------
# FUNCTIONS
# ------------------------------------------------------------
def find_in_csv_first_column(csv_file_path, search_string):
    """
    Search for a string in the first column of a CSV file.
    
    Args:
        csv_file_path: Path to the CSV file
        search_string: String to search for in the first column
    
    Returns:
        bool: True if found, False if not found
    """
    try:
        with open(csv_file_path, 'r', newline='', encoding='utf-8') as csvfile:
            csv_reader = csv.reader(csvfile)
            for row in csv_reader:
                if row and row[0].strip() == search_string.strip():
                    return True
        return False
    except FileNotFoundError:
        print(f"CSV file not found: {csv_file_path}")
        return False
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return False

def find_variable_dependencies(target_var, dependencies, visited=None):
    """
    Recursively find all dependencies of a target variable.
    
    Args:
        target_var: The variable to find dependencies for
        dependencies: The dependencies dictionary
        visited: Set of already visited variables to prevent cycles
    
    Returns:
        set: All dependencies (direct and indirect) of the target variable
    """
    if visited is None:
        visited = set()
    
    if target_var in visited:
        return set()  # Prevent infinite recursion
    
    visited.add(target_var)
    all_deps = set()
    
    # Get direct dependencies
    direct_deps = dependencies.get(target_var, [])
    all_deps.update(direct_deps)
    
    # Recursively get indirect dependencies
    for dep in direct_deps:
        indirect_deps = find_variable_dependencies(dep, dependencies, visited.copy())
        all_deps.update(indirect_deps)
    
    return all_deps

def find_variables_using_target(target_var, dependencies):
    """
    Find all variables that use the target variable.
    
    Args:
        target_var: The variable to find users for
        dependencies: The dependencies dictionary
    
    Returns:
        list: Variables that depend on the target variable
    """
    users = []
    for var, deps in dependencies.items():
        if target_var in deps:
            users.append(var)
    return users

def analyze_variable(target_var, dependencies, objects_by_type):
    """
    Comprehensive analysis of a variable's dependencies and usage.
    
    Args:
        target_var: The variable to analyze
        dependencies: The dependencies dictionary
        objects_by_type: Objects organized by type
    """
    
    # Find what this variable depends on
    deps = find_variable_dependencies(target_var, dependencies)
    print(f"\n1. DEPENDENCIES OF {target_var}:")
    if deps:
        for dep in sorted(deps):
            print(f"  - {dep}")
    else:
        print("2. No dependencies found")
    
    # Find what uses this variable
    users = find_variables_using_target(target_var, dependencies)
    print(f"\n3. VARIABLES THAT USE {target_var}:")
    if users:
        for user in sorted(users):
            print(f"4.  - {user}")
    else:
        print("5. No variables use this")
    
    # Find the object type and attributes
    obj_found = False
    for obj_tag, objs in objects_by_type.items():
        if target_var in objs:
            print(f"\n6. OBJECT TYPE: {obj_tag}")
            print("7. ATTRIBUTES:")
            for attr, value in objs[target_var].items():
                print(f"8.  {attr}: {value}")
            obj_found = True
            break
    
    if not obj_found:
        print(f"\n9. OBJECT TYPE: {obj_tag} Not found in objects_by_type")
        print("10. This might be an implicit or referenced variable")
    return

def lookup_name_by_id(object_id, objects_by_type):
    """
    Lookup an object's name by its ID across all object types.
    
    Args:
        object_id: The ID to search for
        objects_by_type: The objects organized by type
    
    Returns:
        tuple: (object_type, object_name) or (None, None) if not found
    """
    # search objects_by_type for idObject
    for obj_tag in object_tags:
        if object_id in objects_by_type[obj_tag]:
            obj_name = objects_by_type[obj_tag][object_id].get('name')
            break
    # end for obj_tag in object_tags
    if obj_tag is None:            
        obj_tag = 'unknown'
        obj_name = f"Unknown_{object_id}"   
    return obj_tag, obj_name

def add_to_objects_by_type(obj_tag, obj_id, element, name, objects_by_type):
    """
    Add an element and its name to objects_by_type.
    
    Args:
        obj_tag: The type of object (e.g., 'point', 'line', 'variable')
        obj_id: The ID of the object
        element: The XML element
        name: The name to assign to the object
        objects_by_type: The objects organized by type
    """
    # add object to objects_by_type with filtered attributes
    objects_by_type[obj_tag][obj_id] = {k:v for k,v in element.attrib.items() if k not in display_attributes}
    # add 'name' to object because not all objects have a name in their attributes
    objects_by_type[obj_tag][obj_id]['name'] = name
    print(f"add_obj 1.    added {obj_tag} object to objects_by_type => {objects_by_type[obj_tag][obj_id]}")

def create_filtered_element(element, obj_id, name):
    """
    Create a new XML element with obj_id, name, and attributes that are not in display_attributes.
    
    Args:
        element: The original XML element
        obj_id: The ID to assign to the new element
        name: The name to assign to the new element
    
    Returns:
        ET.Element: A new XML element with filtered attributes
    """
    obj_tag = element.tag
    new_element = ET.Element(obj_tag)
    new_element.attrib['id'] = obj_id
    new_element.attrib['name'] = name
    
    # add attributes that are not in display_attributes
    for attr, value in element.attrib.items():
        if attr not in display_attributes:
            new_element.attrib[attr] = value
    
    return new_element

def categorize_line(element, objects_by_type):
    """
    Process a line element and create its name from firstPoint and secondPoint.
    
    Args:
        element: The line XML element
        objects_by_type: The objects organized by type
    
    Returns:
        tuple: (name, processed) where name is the line name and processed is boolean
    """
    obj_tag         = element.tag
    obj_id          = element.attrib.get('id')
    first_point_id  = element.attrib.get('firstPoint')
    second_point_id = element.attrib.get('secondPoint')
    print(f"cat_line 1. Processing line {obj_id}, {first_point_id}, {second_point_id}")
    
    # get names of first and second points & create line name
    if first_point_id and second_point_id:
        # Find the names of the first and second points
        first_point_name  = None
        second_point_name = None
        # get point names from attributes from objects_by_type
        for point_id, point_attrs in objects_by_type.get('point', {}).items(): # get all the points
            if point_id == first_point_id:
                first_point_name = point_attrs.get('name')
                print(f"cat_line 2.      firstPoint = {first_point_id}, {first_point_name}")
            elif point_id == second_point_id:   
                second_point_name = point_attrs.get('name')
                print(f"cat_line 3.      secondPoint = {second_point_id}, {second_point_name}")
            # endif point_id == first_point_id:  
        # end for point_id, point_attrs in objects_by_type.get('point', {}).items()
        # If we found both names, create the line name Line_P1_P2
        if first_point_name and second_point_name:
            name = f"Line_{first_point_name}_{second_point_name}"
        else:
            # Fallback to id if names not found
            name = f"line{obj_id}"
        # end if first_point_name and second_point_name
    else:
        # Fallback to id if firstPoint or secondPoint not found
        name = f"line{obj_id}"
    # endif first_point_id and second_point_id exist for <line>
    print(f"cat_line 4.    {obj_tag} = {obj_id}, {name}")

    # create new element with obj_id, name, and attributes that are not in display_attributes
    new_element = create_filtered_element(element, obj_id, name)
    # add line object to objects_by_type
    add_to_objects_by_type(obj_tag, obj_id, new_element, name, objects_by_type)

    return

def process_intersectXY_alongLinepoint(element, obj_id, obj_name, objects_by_type):
    """
    Process an intersectXY or alongLinepoint by creating two implicit lines.
    
    Args:
        element: The intersectXY point XML element
        obj_id: The ID of the intersectXY point
        obj_name: The name of the intersectXY point
        objects_by_type: The objects organized by type
    """
    type = element.get('type')
    if type == 'intersectXY':
        line_id_prefix = f"Line_intersectXY_{obj_id}_"
    elif type == 'alongLine':
        line_id_prefix = f"Line_alongLine_{obj_id}_"
    else:
        print(f"cat_intersect 1. Warning: {type} is not a valid intersectXY or alongLine point")
        exit()
    # endif type == 'intersectXY' or type == 'alongLine'
    first_point_id  = element.attrib.get('firstPoint')
    second_point_id = element.attrib.get('secondPoint')
    
    if first_point_id and second_point_id:
        # Get the names of the first and second points
        first_point_type, first_point_name   = lookup_name_by_id(first_point_id, objects_by_type)
        second_point_type, second_point_name = lookup_name_by_id(second_point_id, objects_by_type)

        if first_point_name and second_point_name:         # Create two lines with the specified naming convention
            line_id_1      = f"{line_id_prefix}1"
            line_id_2      = f"{line_id_prefix}2"
            line_name_1    = f"Line_{first_point_name}_{obj_name}"
            line_name_2    = f"Line_{second_point_name}_{obj_name}"

            # Create 1st implicit line element
            line_element_1                       = ET.Element('line')
            line_element_1.attrib['id']          = line_id_1
            line_element_1.attrib['name']        = line_name_1
            line_element_1.attrib['firstPoint']  = first_point_id
            line_element_1.attrib['secondPoint'] = obj_id
            line_element_1.attrib['implicit']    = 'True'

            # Create 2nd implicit line eleme nt
            line_element_2                       = ET.Element('line')
            line_element_2.attrib['id']          = line_id_2
            line_element_2.attrib['name']        = line_name_2
            line_element_2.attrib['firstPoint']  = second_point_id 
            line_element_2.attrib['secondPoint'] = obj_id
            line_element_2.attrib['implicit']    = 'True'
                
            # Add lines to objects_by_type
            add_to_objects_by_type('line', line_id_1, line_element_1, line_name_1, objects_by_type)
            add_to_objects_by_type('line', line_id_2, line_element_2, line_name_2, objects_by_type)
            print(f"cat_intersect 1. Created implicit lines {line_id_1}: {line_name_1} and {line_id_2}: {line_name_2}")

        else:
            print(f"cat_intersect 2. Warning: Could not find names for points {first_point_id} or {second_point_id}")
        # endif first_point_name and second_point_name
    else:
        print(f"cat_intersect 3. Warning: intersectXY point {obj_id} missing firstPoint or secondPoint")
    # endif first_point_id and second_point_id
    return

def process_endLine_point(element, obj_id, obj_name, objects_by_type):
    """
    Process an endLine point by creating an implicit line from baseLine to the point.
    
    Args:
        element: The endLine point XML element
        obj_id: The ID of the endLine point
        obj_name: The name of the endLine point
        objects_by_type: The objects organized by type
    """
    print(f"cat_endLine 1. Processing endLine point {obj_id}, {obj_name}")
    base_id = element.attrib.get('basePoint')
    
    if base_id:
        # Get the name of the base line
        base_type, base_name = lookup_name_by_id(base_id, objects_by_type)

        if base_name:
            # Create line with the specified naming convention
            line_id = f"Line_endLine_{base_id}_{obj_id}"
            line_name = f"Line_{base_name}_{obj_name}"

            # Create implicit line element
            line_element                       = ET.Element('line')
            line_element.attrib['id']          = line_id
            line_element.attrib['name']        = line_name
            line_element.attrib['firstPoint']  = base_id
            line_element.attrib['secondPoint'] = obj_id
            line_element.attrib['implicit']    = 'True'
                
            # Add line to objects_by_type
            add_to_objects_by_type('line', line_id, line_element, line_name, objects_by_type)
            print(f"cat_endLine 1. Created implicit line {line_id}: {line_name} -> {objects_by_type['line'][line_id]}")

        else:
            print(f"cat_endLine 2. Warning: Could not find name for base line {base_id}")
        # endif base_line_name
    else:
        print(f"cat_endLine 3. Warning: endLine point {obj_id} missing basePoint")
    # endif base_id
    return

def process_lineIntersectAxis_point(element, obj_id, obj_name, objects_by_type):
    """
    Process a lineIntersectAxis point by creating an implicit line from basePoint to the point.
    
    Args:
        element: The lineIntersectAxis point XML element
        obj_id: The ID of the lineIntersectAxis point
        obj_name: The name of the lineIntersectAxis point
        objects_by_type: The objects organized by type
    """
    print(f"cat_lineIntersectAxis 1. Processing lineIntersectAxis point {obj_id}, {obj_name}")
    base_id = element.attrib.get('basePoint')
    
    if base_id:
        # Get the name of the base point
        base_type, base_name = lookup_name_by_id(base_id, objects_by_type)

        if base_name:
            # Create line with the specified naming convention
            line_id   = f"Line_lineIntersectAxis_{base_id}_{obj_id}"
            line_name = f"Line_{base_name}_{obj_name}"

            # Create implicit line element
            line_element                       = ET.Element('line')
            line_element.attrib['id']          = line_id
            line_element.attrib['name']        = line_name
            line_element.attrib['firstPoint']  = base_id
            line_element.attrib['secondPoint'] = obj_id
            line_element.attrib['implicit']    = 'True'
                
            # Add line to objects_by_type
            add_to_objects_by_type('line', line_id, line_element, line_name, objects_by_type)
            print(f"cat_lineIntersectAxis 2. Created implicit line {line_id}: {line_name}")

        else:
            print(f"cat_lineIntersectAxis 3. Warning: Could not find name for base point {base_id}")
        # endif base_name
    else:
        print(f"cat_lineIntersectAxis 4. Warning: lineIntersectAxis point {obj_id} missing basePoint")
    # endif base_id
    return

def process_single_point(element, obj_id, obj_name, objects_by_type):
    """
    Process a single point by adding a block attribute with the last draftBlock ID.
    
    Args:
        element: The single point XML element
        obj_id: The ID of the single point
        obj_name: The name of the single point
        objects_by_type: The objects organized by type
    """
    print(f"cat_single 1. Processing single point {obj_id}, {obj_name}")
    
    # Find the last draftBlock ID
    draft_blocks = objects_by_type.get('draftBlock', {})
    if draft_blocks:
        # Get the last draftBlock ID (assuming they're added in order)
        last_block_id = list(draft_blocks.keys())[-1]
        print(f"cat_single 2. Found last draftBlock ID: {last_block_id}")
        
        # Add block attribute to the element
        element.attrib['block'] = last_block_id
        print(f"cat_single 3. Added block attribute: {last_block_id}")
    else:
        print(f"cat_single 4. Warning: No draftBlocks found for single point {obj_id}")
    # endif draft_blocks
    
    return element

def categorize_point(element, objects_by_type):
    """
    Process a point element and create its name.
    
    Args:
        element: The point XML element
        objects_by_type: The objects organized by type
    """
    obj_tag         = element.tag
    obj_id          = element.attrib.get('id')
    obj_name        = element.attrib.get('name')
    obj_type        = element.attrib.get('type')
    name            = obj_name
    print(f"cat_point 1.    Processing {obj_tag}, {obj_id}, {obj_name}, {obj_type}") 
    if name is None:
        name = f"Point_{obj_id}"
    # endif name is None
    print(f"cat_point 2.    {obj_tag} = {obj_id}, {name}, {obj_type}")

    # create new element with obj_id, obj_name, name, and attributes that are not in display_attributes
    new_element = create_filtered_element(element, obj_id, name)
    if obj_type == 'single':
        new_element = process_single_point(new_element, obj_id, obj_name, objects_by_type)
    # add point object to objects_by_type
    add_to_objects_by_type(obj_tag, obj_id, new_element, name, objects_by_type)
    
    # add addtional objects to objects_by_type
    match obj_type:
        case 'intersectXY' | 'alongLine':
            process_intersectXY_alongLinepoint(element, obj_id, obj_name, objects_by_type)
        case 'endLine':
            process_endLine_point(element, obj_id, obj_name, objects_by_type)
        case 'lineIntersectAxis':
            process_lineIntersectAxis_point(element, obj_id, obj_name, objects_by_type)
        case _:
            print(f"cat_point 3.    Unknown point type: {obj_id}, {obj_name}, {obj_type}")
    # end match obj_type
    
    return

def categorize_variable(element, objects_by_type):
    """
    Process a variable element and create its name.
    
    Args:
        element: The variable XML element
        objects_by_type: The objects organized by type
    """
    global var_id_counter
    
    obj_tag         = element.tag
    obj_name        = element.attrib.get('name')
    if obj_name[0:2] in ['#_', '##']:
        print(f"cat_var 1.   Skipping {obj_tag}, {obj_name} because it is a variable header")
        return
    # endif obj_name[0:2] == '#_'
    obj_id          = str(var_id_counter)
    var_id_counter -= 1
    name            = obj_name
    print(f"cat_var 2. Processing variable {obj_id}, {obj_name}")
    print(f"cat_var 3.    {obj_tag} = {obj_id}, {name}")

    # create new element with obj_id, formula and name
    new_element = create_filtered_element(element, obj_id, name)
    # add variable object to objects_by_type
    add_to_objects_by_type(obj_tag, obj_id, new_element, name, objects_by_type)

    return

def categorize_draftBlock(element, objects_by_type):
    """
    Process a draftBlock element and create its name.
    
    Args:
        element: The draftBlock XML element
        objects_by_type: The objects organized by type
    """
    global block_id_counter
    # there is no id for blockDraft tags){}
    obj_tag           = element.tag
    obj_id            = f"block_id_{block_id_counter}"
    block_id_counter += 1
    obj_name          = element.attrib.get('name')
    print(f"cat_draft 1. Processing draftBlock {obj_id}, {obj_name}")
    
    # create draftBlock name
    if obj_name:
        name = f"{obj_name}" 
    else:
        name = f"Block{obj_id}"
    # endif obj_name
    print(f"cat_draft 2.    {obj_tag} = {obj_id}, {name}")

    # create new element with obj_id, name, and attributes that are not in display_attributes
    new_element = create_filtered_element(element, obj_id, name)
    # add draftBlock object to objects_by_type
    add_to_objects_by_type(obj_tag, obj_id, new_element, name, objects_by_type)
    return

def categorize_measurement(element, objects_by_type):
    """
    Process a measurement ('m') element and create its name.
    
    Args:
        element: The measurement XML element
        objects_by_type: The objects organized by type
    """
    global measurement_id_counter
    # there is not id for measurement <m> tags
    obj_tag                 = element.tag
    obj_id                  = f"m_id_{measurement_id_counter}"
    measurement_id_counter += 1
    obj_name                = element.attrib.get('name')
    name                    = None
    print(f"cat_meas 1. Processing measurement {obj_id}, {obj_name}")
    
    # create measurement name
    if obj_name:
        name = f"{obj_name}" 
    else:
        name = f"m{obj_id}"
    # endif obj_name
    print(f"cat_meas 2.    {obj_tag} = {obj_id}, {name}")

    # create new element with obj_id, name, and attributes that are not in display_attributes
    new_element = create_filtered_element(element, obj_id, name)
    # add measurement object to objects_by_type
    add_to_objects_by_type(obj_tag, obj_id, new_element, name, objects_by_type)
    return

def categorize_arc(element, objects_by_type):
    """
    Process an arc or elArc element and create its name.
    
    Args:
        element: The arc/elArc XML element
        objects_by_type: The objects organized by type
    """
    obj_id   = element.attrib.get('id')
    obj_name = element.attrib.get('name')
    obj_tag  = element.tag  # 'arc' or 'elArc'
    name     = None
    print(f"cat_arc 1. Processing {obj_tag}, {obj_id}, {obj_name}")
    
    # create arc name
    if obj_name:
        name = f"{obj_name}"
    else:
        if obj_tag == 'elArc':
            obj_center1 = element.get('center1')
            obj_center2 = element.get('center2')
            obj_radius1 = element.get('radius1')
            obj_radius2 = element.get('radius2')
            name = f"elArc_{obj_center1}_{obj_center2}_{obj_radius1}_{obj_radius2}"
        else:
            obj_center = element.get('center')  
            obj_radius = element.get('radius')
            name = f"arc_{obj_center}_{obj_radius}"
        # endif obj_tag == 'elArc'
    # endif obj_name
    print(f"cat_arc 2.    {obj_tag} = {obj_id}, {name}")

    # create new element with obj_id, name, and attributes that are not in display_attributes
    new_element = create_filtered_element(element, obj_id, name)
    # add arc object to objects_by_type
    add_to_objects_by_type(obj_tag, obj_id, new_element, name, objects_by_type)
    return

def categorize_spline(element, objects_by_type):
    """
    Process a spline element and create its name based on type.
    
    Args:
        element: The spline XML element
        objects_by_type: The objects organized by type
    """
    obj_tag         = element.tag
    obj_id          = element.attrib.get('id')
    obj_name        = element.attrib.get('name')
    name            = None
    name_values     = []
    spl_type        = element.attrib.get('type')
    spl_prefix      = None
    point_attrs     = []
    point_id_values = []
    print(f"cat_spline 1. Processing {obj_tag}, {spl_type}, {obj_id}, {obj_name}")
    
    # Determine prefix based on spline type
    if spl_type == 'cubicBezier':
        spl_prefix = "SplPath"
    elif spl_type in ['simpleInteractive', 'pathInteractive']:
        spl_prefix = "Spl"
    else:
        spl_prefix = "Spl"
    # endif spl_type
    
    # create a list of all attributes that begin with 'point'
    point_attrs = [attr for attr in element.attrib if attr.startswith('point')]
    # get the id values of the point attributes
    point_id_values = [element.attrib[attr] for attr in point_attrs]
    # lookup the name values of the point ids from objects_by_type
    for id_value in point_id_values:
        # lookup id_value in objects_by_type
        if id_value in objects_by_type['point']:
            name = objects_by_type['point'][id_value].get('name', f"point_{id_value}")
            name_values.append(name)
        else:
            input(f"cat_spline 2.    point {id_value} not found in objects_by_type['point']")
            exit
        # endif id_value in objects_by_type['point']
    # end for id_value in point_id_values
    # create spline name from prefix & first & last point names
    name = f"{spl_prefix}_{name_values[0]}_{name_values[-1]}"
    print(f"cat_spline 3.    {obj_tag} = {obj_id}, {name}")
    
    # create new element with obj_id, name, and attributes that are not in display_attributes       
    new_element = create_filtered_element(element, obj_id, name)
    # add spline object to objects_by_type
    add_to_objects_by_type(obj_tag, obj_id, new_element, name, objects_by_type)
    return

def categorize_operation(element, objects_by_type):
    """
    Process an operation element and create its name.
    
    Args:
        element: The operation XML element
        objects_by_type: The objects organized by type
    """
    obj_tag      = element.tag
    obj_id       = element.attrib.get('id')
    obj_type     = element.attrib.get('type')
    obj_suffix   = element.attrib.get('suffix')
    name         = obj_suffix
    source_names = []
    source_types = []
    print(f"cat_op 1. Processing {obj_tag}, {obj_type}, {obj_id}, {name}")
    
    # Add name attribute to the original operation element before filtering
    element.attrib['name'] = name
    
    # create new element with obj_id, name, and attributes that are not in display_attributes
    # process top level operation object
    # create new element with obj_id, name, and attributes that are not in display_attributes
    new_element = create_filtered_element(element, obj_id, name)
    add_to_objects_by_type(obj_type, obj_id, new_element, name, objects_by_type)
    
    for source in element.findall('source'):
        for item in source.findall('item'):
            # get the id's of the source <item> children 
            src_id = item.attrib.get('idObject')   
            # lookup name and type in objects_by_type
            src_type, src_name = lookup_name_by_id(src_id, objects_by_type)
            # add name to source_names
            source_types.append(src_type)
            source_names.append(src_name) 
        # end for item in source.findall('item')
        print(f"cat_op 2.    source_names = {source_names}")
    # end for source in element.findall('source')
    
    for dest in element.findall('destination'):
        for i, dest_item in enumerate(dest.findall('item')):
            # get the id's of the destination <item> children 
            dest_id    = dest_item.attrib.get('idObject')
            dest_type  = source_types[i]
            dest_name  = f"{source_names[i]}{obj_suffix}"
            print(f"cat_op 3.     source[{i}] = {source_names[i]}, {source_types[i]}")
            print(f"cat_op 4.     {obj_type} {dest_type} = {dest_id}, {dest_name}")
            # create new element with dest_id, dest_name, dest_type, and op=obj_id
            new_element                     = create_filtered_element(dest_item, dest_id, dest_name)
            new_element.attrib['op'] = obj_id
            # remove idObject attribute
            new_element.attrib.pop('idObject', None)
            # add to objects_by_type 
            add_to_objects_by_type(dest_type, dest_id, new_element, dest_name, objects_by_type)
        # end for item in dest.findall('item')
    # end for dest in element.findall('destination')
    
    return # return to categorize_elements

def categorize_elements(element):
    """Recursively categorize all XML elements, starting with the root element """
    global objects_by_type
    global var_id_counter
    global object_tags

    # get element type, id, and name
    obj_tag = element.tag  # e.g., 'root''point', 'line', 'arc', 'variable' 
    obj_id   = element.attrib.get('id')
    obj_name = element.attrib.get('name')
    print(f"cat_el 1. Processing {obj_tag}, {obj_id}, {obj_name} with attributes {element.attrib}")
    if obj_tag in skip_tags:
        print(f"cat_el 2.    Skipping {obj_tag}, {obj_id}, {obj_name} because it is a skip tag")
        return
    # endif

    # Special handling for line tags - create name from firstPoint and secondPoint
    # line tags have firstPoint and secondPoint attributes
    match obj_tag:
        case 'line':
            # create line name & add line object to objects_by_type
            categorize_line(element, objects_by_type)
        case 'point':
            # create point name & add point object to objects_by_type
            categorize_point(element, objects_by_type)
        case 'variable':
            # variable tags have no attributes
            categorize_variable(element, objects_by_type)
        case 'draftBlock':
            # create draftBlock name & add draftBlock object to objects_by_type
            categorize_draftBlock(element, objects_by_type)
        case 'm':
            # create measurement name & add measurement object to objects_by_type
            categorize_measurement(element, objects_by_type)
        case 'arc' | 'elArc':
            # arc tags have name attribute
            categorize_arc(element, objects_by_type)
        case 'spline':
            categorize_spline(element, objects_by_type)
        case 'operation':   
            categorize_operation(element, objects_by_type)
        case 'pattern' | 'measurements' | 'variables' | 'draftBlocks' | 'calculation' |'modeling' | 'pieces' | 'groups':
            print(f"cat_el 4.    Skipping {obj_tag}, {obj_id}, {obj_name} because it is a parent tag")
        case _:
            input(f"cat_el 4.    Unknown tag {obj_tag}, {obj_id}, {obj_name}")
            exit()
        # end case _
    # end match obj_tag
    
    # get number of children of element
    num_children = len(element)
    if num_children == 0 or num_children == None:
        print(f"cat_el 3.    This {obj_tag}, {obj_id}, {obj_name} has no children")
    elif obj_tag!= 'operation':
        # Recursively process child elements
        print(f"cat_el 4.    Processing children of {obj_tag}, {obj_id}, {obj_name}")         
        for child in element:
            categorize_elements(child)
        # end for child in element
    # endif num_children > 0

    return # return to main


# ------------------------------------------------------------
# MAIN
# ------------------------------------------------------------
'''
Loads and parses the file.
Sets up two main data structures:
objects_by_type: Groups XML elements by their tag (e.g., 'point', 'line'), using their name or id as a key.
dependencies: Tracks which objects reference which other objects.
'''

# ------------------------------------------------------------
# Environment

# change to the directory of this script
os.chdir(os.path.dirname(os.path.abspath(__file__)))
# clear the console for windows or linux or macos
if os.name == 'nt':
    os.system('cls')
elif os.name == 'posix':
    os.system('clear')
else:
    print("main 1. Unsupported operating system" )

# ------------------------------------------------------------
# Get the Data

# Select the Seamly2d pattern file with a file dialog
root = tk.Tk()
root.withdraw()
# set the initial directory to "G:\My Drive\seamly2d\patterns"
initial_dir = "G:/My Drive/seamly2d/patterns"
file_path = filedialog.askopenfilename(filetypes=[("Seamly2d pattern files", "*.sm2d")], initialdir=initial_dir)
# get base file name
base_file_name = os.path.basename(file_path)
print(f"main 2. Let's get started on {base_file_name}")
# Load and parse the XML file
tree = ET.parse(file_path)
root = tree.getroot()

# ------------------------------------------------------------
# DATA STRUCTURES
# ------------------------------------------------------------

# Object storage: {'point': {'pointA': {...}}, 'line': {'lineAB': {...}}}
objects_by_type = defaultdict(dict)

# Dependency storage: {'obj_id': {'name': 'obj_name', 'dependencies': [['dep_id', 'dep_name'], ...]}}
dependencies = defaultdict(dict)


# ------------------------------------------------------------
# CATEGORIZE OBJECTS
# ------------------------------------------------------------

print(f"\n\n\n{'='*60}")
print(f"main 3. Let's categorize the objects...")
input(f"{'='*60}")

# Categorize objects - recursively find all elements
categorize_elements(root)

# output results to a file in the same directory as this script
with open(os.path.join(script_dir, 'objects_by_type.txt'), 'w') as f: # objects_by_type
    pp = pprint.PrettyPrinter(indent=2, width=120, stream=f)
    pp.pprint(dict(objects_by_type))


# ------------------------------------------------------------
# EXTRACT DEPENDENCIES
# ------------------------------------------------------------

print(f"\n\n\n{'='*60}")
print("main 4. Now let's extract the dependencies...")
input(f"{'='*60}")

# Regular expression to find object references
ref_pattern = re.compile(r'\b[a-zA-Z_][a-zA-Z0-9_.]*\b')

# Extract dependencies from objects_by_type
for obj_tag, objs in dict(objects_by_type).items():
    for obj_id, obj_data in objs.items():

        # add current object to dependencies dictionary with empty dependency list
        obj_name                             = obj_data.get('name') 
        dependencies[obj_id]                 = {}
        dependencies[obj_id]['name']         = obj_name
        dependencies[obj_id]['dependencies'] = []
        print(f"main 5a. processing {obj_id},{obj_name} for dependencies")

        for attr_name, attr_value in obj_data.items():
            
            print(f"main 5b1.      is {attr_name}, {attr_value} a dependency?")

            if attr_name in ['id', 'name', 'type', 'suffix']:
                # the object's id , name, type are not it's own dependencies
                print(f"main 5b2.      skipping {attr_name}")
                continue
            # endif attr_name == 'id' or attr_name == 'name'

            dep_id   = None
            dep_type = None
            dep_name = None

            if attr_name.startswith('point') or attr_name.startswith('Point') or attr_name.endswith('point') or attr_name.endswith('Point'):
                is_point = True
            else:
                is_point = False
            # endif attr_name.startswith('point') or attr_name.endswith('Point')

            # attr_name id or a calculation
            if attr_name in id_attributes or is_point:
                dep_id             = attr_value # is id of the dependency
                dep_type, dep_name = lookup_name_by_id(attr_value, objects_by_type)
                dependency_pair    = [dep_id, dep_name]
                dependencies[obj_id]['dependencies'].append(dependency_pair) # add dependency 
                print(f"main 5c.      added {dep_id}, {dep_name} to dependencies")
            elif attr_name in formula_attributes:
                formula = attr_value
                # parse the formula into segments
                segments = re.split(r'[\+\-\*/\(\)\<\>\=\?\:\;]', formula)
                # filter out empty segments
                segments = [segment.strip() for segment in segments if segment.strip()]
                print(f"main 5c.      segments = {segments}")
                for segment in segments:
                    print(f"main 5d1.      segment = {segment}")
                    if segment.startswith('AngleLine'):
                        # remove 'Angle" from start of segment
                        segment = segment[5:]
                        print(f"main 5d2.      segment = {segment}")
                    # if segment is a math operator, skip it
                    if segment in ['+', '-', '*', '/', '(', ')', '<', '>', '=', '?', ':', ';']:
                        print(f"main 5e.      {segment} is a math operator, skipping")
                        continue  # get the next segment
                    # if segment is a math function, skip it
                    elif segment.lower() in ['max', 'min', 'abs', 'sqrt', 'sin', 'cos', 'tan', 'log', 'exp']:
                        print(f"main 5f.      {segment} is a math function, skipping")
                        continue  # get the next segment
                    # if the segment is a number, skip it
                    elif re.fullmatch(r'[0-9.]+', segment):
                        print(f"main 5g.      {segment} is a number, skipping")
                        continue
                    # is segment a measurement?
                    elif find_in_csv_first_column(measurements_csv_file_path, segment):
                        # if segment is a measurement, add it to the dependencies
                        dep_id                  = str(measurement_id_counter)
                        measurement_id_counter += 1
                        dep_type                = 'measurement'
                        dep_name                = segment
                        dependency_pair         = [dep_id, dep_name]
                        print(f"main 5h.      added {dep_id}, {dep_name} to dependencies")
                    # is segment a pattern object?
                    else:
                        # look up name in objects_by_type
                        found = False
                        for type, items in objects_by_type.items():
                            for id, item in items.items():
                                name = item.get('name')
                                if name is None:
                                    print(f"main 5d1.      objects_by_type[{type}][{id}] has no name")
                                    input(f"main 5d2.      item = {item}")  
                                    exit()
                                if segment == name:
                                    dep_id          = id
                                    dep_type        = type
                                    dep_name        = segment
                                    dependency_pair = [dep_id, dep_name]
                                    dependencies[obj_id]['dependencies'].append(dependency_pair)
                                    print(f"main 5d.      added {dep_id}, {dep_name} to dependencies")
                                    found = True
                                    break # leave this loop to get next segment
                                # end if segment == items.name
                            # end id, item in items.items()
                        # end for type, items
                        # if found continue to the next segment
                        if found:
                            continue # get next segment
                        else:
                            input(f"main 5e.      {segment} not found in objects_by_type")
                            exit()
                        # endif found
                    # endif segment is a number
                # end for segment in segments
            else:
                # if attr_name is not an id or a formula, exit
                input(f"main 5c.      {attr_name} is not an id or a formula")
                exit()
            # endif attr_name in formula_attributes
        # end for attr_name, attr_value in obj_data.items()
    # end for obj_id, obj_data in objs.items()
# end for obj_tag, objs in objects_by_type.items()

# ------------------------------------------------------------
# DISPLAY THE OBJECT BY TYPE DATA
# ------------------------------------------------------------
print(f"\n{'='*60}")
# Pretty-print results
print("main 8. Objects by type:")
input(f"{'='*60}")

for type, objs in objects_by_type.items():
    # list the ids for each type, group the types together
    input(f"{type}: {list(objs.keys())}")

# ------------------------------------------------------------
# DISPLAY THE DEPENDENCIES DATA
# ------------------------------------------------------------
print(f"\n{'='*60}")
print("main 9. Dependencies:")
input(f"{'='*60}")

for obj, deps in dependencies.items():
    print(f"{obj}: {deps}")

# ------------------------------------------------------------
# DISPLAY VARIABLES 
# ------------------------------------------------------------  
# Find custom variables starting with # (XML name attributes)
print(f"\n{'='*60}")
print("DISPLAY VARIABLES")
input(f"{'='*60}")

for key, var_data in objects_by_type['variable'].items():
    name = var_data.get('name')
    print(f"{key}, {name}, value = {var_data}")

total_variables = len(objects_by_type['variable'])

# ------------------------------------------------------------
# DISPLAY MEASUREMENTS
# ------------------------------------------------------------
print(f"\n{'='*60}")
print("DISPLAY MEASUREMENTS")
input(f"{'='*60}")

for key, m_data in objects_by_type['measurement'].items():
    name = m_data.get('name')
    print(f"{key}, {name}, value = {data}")

total_measurements = len(objects_by_type['measurement'])


    

# ------------------------------------------------------------
# DISPLAY SUMMARY STATISTICS
# ------------------------------------------------------------
# Summary statistics
print(f"\n{'='*60}")
print("SUMMARY STATISTICS")
input(f"{'='*60}")

total_objects = sum(len(objs) for objs in objects_by_type.values())
print(f"Total objects: {total_objects}")
print(f"Object types: {list(objects_by_type.keys())}")
print(f"Total dependencies: {len(dependencies)}")
print(f"Variables: {total_variables}")
print(f"Measurements: {total_measurements}")

# EOF