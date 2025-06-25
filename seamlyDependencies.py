#
'''
This script is used to extract the dependencies of a Seamly2d CAD file.
It is used to create a dependency graph of the CAD file.
'''

import xml.etree.ElementTree as ET
import os, re
from collections import defaultdict

import tkinter as tk
from tkinter import filedialog

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

def lookup_name_by_id(object_id, objects_by_type):
    """
    Lookup an object's name by its ID across all object types.
    
    Args:
        object_id: The ID to search for
        objects_by_type: The objects organized by type
    
    Returns:
        tuple: (object_type, object_name) or (None, None) if not found
    """
    for obj_type, objs in objects_by_type.items():
        for key, attrs in objs.items():
            if attrs.get('id') == object_id:
                # Return the object type and the name (key)
                return obj_type, key
    return None, None

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
    print(f"\nDEPENDENCIES OF {target_var}:")
    if deps:
        for dep in sorted(deps):
            print(f"  - {dep}")
    else:
        print("  No dependencies found")
    
    # Find what uses this variable
    users = find_variables_using_target(target_var, dependencies)
    print(f"\nVARIABLES THAT USE {target_var}:")
    if users:
        for user in sorted(users):
            print(f"  - {user}")
    else:
        print("  No variables use this")
    
    # Find the object type and attributes
    obj_found = False
    for obj_type, objs in objects_by_type.items():
        if target_var in objs:
            print(f"\nOBJECT TYPE: {obj_type}")
            print("ATTRIBUTES:")
            for attr, value in objs[target_var].items():
                print(f"  {attr}: {value}")
            obj_found = True
            break
    
    if not obj_found:
        print(f"\nOBJECT TYPE: Not found in objects_by_type")
        print("This might be an implicit or referenced variable")
    return

def categorize_elements(element):
    """Recursively categorize all XML elements, starting with the root element """

    # get number of children of element
    num_children = len(element)
    if num_children == 0 or num_children == None:
        print(f"    This {element.tag} has no children")
        return
    # endif no children


    object_tags = ['root', 'measurements', 'm', 'variables', 'variable', 'draftBlock', 'point', 'line','arc', 'elArc', 'operation', 'spline']
    skip_tags   = ['unit', 'version', 'description', 'notes', 'patternLabel']

    obj_type = element.tag  # e.g., 'root''point', 'line', 'arc', 'variable' 
    obj_id   = element.attrib.get('id')
    obj_name = element.attrib.get('name')
    key      = None

    print(f"processing {obj_type}, {obj_id}, {obj_name}")

    if element.tag in skip_tags:
        print(f"   Skipping {obj_type}, {obj_id}, {obj_name}")
        return
    # endif

    # Special handling for line tags - create name from firstPoint and secondPoint
    # line tags have firstPoint and secondPoint attributes
    match obj_type:

        case 'line':
            first_point_id  = element.attrib.get('firstPoint')
            second_point_id = element.attrib.get('secondPoint')
            
            if first_point_id and second_point_id:
                # Find the names of the first and second points
                first_point_name  = None
                second_point_name = None
                
                # get point names from objects_by_type
                for point_id, point_attrs in objects_by_type.get('point', {}).items():
                    if point_attrs.get('id') == first_point_id:
                        first_point_name = point_attrs.get('name', first_point_id)
                    elif point_attrs.get('id') == second_point_id:
                        second_point_name = point_attrs.get('name', second_point_id) 
                    # endif point.attrs.get('id)   
                # end for point_id, point_attrs in objects_by_type.get('point', {}).items()

                # If we found both names, create the line name Line_P1_P2
                if first_point_name and second_point_name:
                    key = f"Line_{first_point_name}_{second_point_name}"
                else:
                    # Fallback to id if names not found
                    key = f"line_id_{obj_id}"
                # end if first_point_name and second_point_name
            else:
                # Fallback to id if firstPoint or secondPoint not found
                key = f"line_id_{obj_id}"
            # endif first_point_id and second_point_id exist for <line>
            print(f"line -- key={key}")
        # end case 'line'
        case 'm' |'draftBlock' | 'point' | 'variable':
            # draftBlock and pointtags have name attribute
            if obj_name:
                key = f"{obj_name}" 
            else:
                key = f"id_{obj_id}"
            # endif obj_name
            print(f"{obj_type} -- key={key}")
        # end case 'm' |'draftBlock' | 'point'
        case 'arc' | 'elArc':
            # arc tags have name attribute
            if obj_name:
                key = f"{obj_name}"
            else:
                key = f"id_{obj_id}"
            # endif obj_type == 'arc'
            print(f"{obj_type} -- key={key}")
        # end case 'arc' | 'elArc'
        case 'spline':
            spl_prefix  = ""
            spl_type    = element.attrib.get('type')            
            if spl_type == 'cubicBezier':
                spl_prefix = "SplPath"
            else:
                spl_prefix = "Spl"
            # endif type == 'cubicBezier'
            # create a list of all attributes that begin with 'point'
            point_attrs = [attr for attr in element.attrib if attr.startswith('point')]
            # get the values of the point attributes
            point_id_values = [element.attrib[attr] for attr in point_attrs]
            name_values = []      
            for id_value in point_id_values:
                # lookup id_value in objects_by_type
                if id_value in objects_by_type['point']:
                    name_values.append(objects_by_type['point'][id_value]['name'])
                else:
                    name_values.append(f"point_{id_value}")
                # end if id_value in objects_by_type['point']
            # end for value in point_values
            # create spline name from prefix & first & last point names
            key = f"{spl_prefix}_{name_values[0]}_{name_values[-1]}" 
            print(f"{spl_type} -- key={key}")
        case 'operation':
            # operation tags have no attribute
            op_type = element.attrib.get('type')
            match op_type:
                case 'rotation':
                    # lookup the names of the source id's in objects_by_type
                    source_names = []
                    for source in element.findall('source'):
                        for item in source.findall('item'):
                            idObject = item.attrib.get('idObject')
                            if idObject in objects_by_type['line']:
                                source_names.append(objects_by_type['line'][idObject]['name'])  
                    key = f"Rot_{obj_id}"
                case 'move':
                    key = f"Scale_{obj_id}"
                case 'translate':
                    key = f"Trans_{obj_id}"
        case _:
            print(f"   Nothing to do for {obj_type}, {obj_id}, {obj_name}")
    # end match obj_type

    # add to objects_by_type dictionary
    if key:
        # append object type (line) and key (name) to objects_by_type dictionary
        objects_by_type[obj_type][key] = element.attrib
    else:
        input(f"   No key found for {obj_type}, {obj_id}, {obj_name}")
    # end if key exists
    
    # Recursively process child elements
    print(f"   Processing children of {obj_type}, {obj_id}, {obj_name}")
    for child in element:
        categorize_elements(child)
    # end for child in element

    return


###############################
# MAIN
###############################
'''
Loads and parses the file.
Sets up two main data structures:
objects_by_type: Groups XML elements by their tag (e.g., 'point', 'line'), using their name or id as a key.
dependencies: Tracks which objects reference which other objects.
'''

# change to the directory of this script
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# clear the console for windows or linux or macos
if os.name == 'nt':
    os.system('cls')
elif os.name == 'posix':
    os.system('clear')
else:
    print("Unsupported operating system" )


# Select the Seamly2d pattern file with a file dialog
root = tk.Tk()
root.withdraw()
# set the initial directory to "G:\My Drive\seamly2d\patterns"
initial_dir = "G:/My Drive/seamly2d/patterns"
file_path = filedialog.askopenfilename(filetypes=[("Seamly2d pattern files", "*.sm2d")], initialdir=initial_dir)

# get base file name
base_file_name = os.path.basename(file_path)
print(f"Let's get started on {base_file_name}")
input("Press Enter to continue...")

# Load and parse the XML
tree = ET.parse(file_path)
root = tree.getroot()

# Object storage: {'point': {'pointA': {...}}, 'line': {'lineAB': {...}}}
objects_by_type = defaultdict(dict)

# Dependency storage: {'lineAB': ['pointA', 'pointB']}
dependencies = defaultdict(list)

# Regular expression to find object references (alphanumeric + underscores or dots)
ref_pattern = re.compile(r'\b[a-zA-Z_][a-zA-Z0-9_.]*\b')

'''
Object Categorization:
Iterates through the root XML elements.
For each element, determines its type (tag), and unique key (name or id).
Stores the element's attributes in objects_by_type under its type and key.
'''
# Categorize objects - recursively find all elements
input(f"Let's categorize the objects...")
categorize_elements(root)

'''
Dependency Extraction :
For each object, examines all its attribute values.
Uses a regex to find all tokens that look like object references (alphanumeric, underscores, or dots).
Adds references that are not numbers to the dependencies dictionary.
If a reference starts with "Line_" and isn't already in the objects, it creates an implicit line object.
If a reference is a "Line_", it adds the current object as dependent on that line.
Otherwise, it adds the reference as a dependency of the current object.
'''
input(f"Now let's extract the dependencies...")

# Extract dependencies
for obj_type, objs in objects_by_type.items():
    for key, attrs in objs.items():
        for attr_name, attr_value in attrs.items():
            if attr_name not in ['implicit', 'description']:
                if obj_type == 'draftBlock' and attr_name == 'name':
                    # Use the full name string as a single dependency
                    if attr_value and not re.fullmatch(r'[0-9.]+', attr_value):
                        dependencies[key].append(attr_value)
                        print(f"draftBlock -- key={key}, dependency={dependencies[key]}")
                else:
                    # Special handling for point attributes that reference other objects
                    if obj_type == 'point' and attr_name in ['firstPoint', 'secondPoint', 'basePoint', 'center', 'p1Line', 'p2Line', 'thirdPoint']:
                        # These attributes directly reference other objects by ID
                        if attr_value and not re.fullmatch(r'[0-9.]+', attr_value):
                            dependencies[key].append(attr_value)
                            print(f"point  -- key={key}, dependency={dependencies[key]}")

                    else:
                        print(f"{attr_name}, {attr_value}")
                        # Regular token-based dependency extraction for other attributes
                        refs = ref_pattern.findall(attr_value)
                        for ref in refs:
                            if re.fullmatch(r'[0-9.]+', ref):
                                continue
                            if ref.startswith("Line_"):
                                if ref not in objects_by_type['line']:
                                    objects_by_type['line'][ref] = {'implicit': True}
                                dependencies[ref].append(key)
                            else:
                                dependencies[key].append(ref)
                            # endif ref.startswith("Line_")
                            print(f"3. other -- key={key}, dependency={dependencies[key]}")
                        # end for ref in refs
                    # endif attr_name not in ['implicit', 'description']
                # endif obj_type == 'draftBlock' and attr_name == 'name'
            # end for attr_name, attr_value in attrs.items()
        # end for key, attrs in objs.items()
    # end for obj_type, objs in objects_by_type.items()
# end for obj_type, objs in objects_by_type.items()

# Pretty-print results
print("Objects by type:")
for t, objs in objects_by_type.items():
    print(f"{t}: {list(objs.keys())}")

print("\nDependencies:")
for obj, deps in dependencies.items():
    print(f"{obj}: {deps}")

# Find all variables starting with # (XML name attributes)
print(f"\n{'='*60}")
print("VARIABLES STARTING WITH # (XML NAME ATTRIBUTES)")
print(f"{'='*60}")
hash_variables = []
for obj_type, objs in objects_by_type.items():
    for key in objs.keys():
        if key.startswith('#'):
            hash_variables.append(key)

if hash_variables:
    print(f"Found {len(hash_variables)} variables starting with #:")
    for var in sorted(hash_variables):
        print(f"  - {var}")
    
    # Analyze each # variable
    print(f"\n{'='*60}")
    print(f"ANALYZING {len(hash_variables)} # VARIABLES")
    print(f"{'='*60}")
    
    for var in sorted(hash_variables):
        analyze_variable(var, dependencies, objects_by_type)
else:
    print("No variables starting with # found")

# Summary statistics
print(f"\n{'='*60}")
print("SUMMARY STATISTICS")
print(f"{'='*60}")
total_objects = sum(len(objs) for objs in objects_by_type.values())
print(f"Total objects: {total_objects}")
print(f"Object types: {list(objects_by_type.keys())}")
print(f"Total dependencies: {len(dependencies)}")
print(f"Variables with # prefix: {len(hash_variables)}")