    '''
    This script is used to extract the dependencies of a Seamly2d CAD file.
    It is used to create a dependency graph of the CAD file.
    '''
    # Extend the existing objects_by_type and dependencies from earlier

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
        obj_type = element.tag  # e.g., 'point', 'line', 'arc', 'variable' 
        obj_id   = element.attrib.get('id')
        obj_name = element.attrib.get('name')

        # Special handling for line tags - create name from firstPoint and secondPoint
        # line tags have firstPoint and secondPoint attributes
        if obj_type == 'line':
            first_point_id  = element.attrib.get('firstPoint')
            second_point_id = element.attrib.get('secondPoint')
            
            if first_point_id and second_point_id:
                # Find the names of the first and second points
                first_point_name  = None
                second_point_name = None
                
                # Look through all points to find the names
                for point_id, point_attrs in objects_by_type.get('point', {}).items():
                    found1 = False
                    found2 = False
                    if point_attrs.get('id') == first_point_id:
                        first_point_name = point_attrs.get('name', first_point_id)
                        found1 = True
                    elif point_attrs.get('id') == second_point_id:
                        second_point_name = point_attrs.get('name', second_point_id)
                        found2 = True         
                # If we found both names, create the line name
                if first_point_name and second_point_name:
                    key = f"Line_{first_point_name}_{second_point_name}"
                else:
                    # Fallback to id if names not found
                    key = obj_id
            else:
                # Fallback to id if firstPoint or secondPoint not found
                key = obj_id
        else:
            # Use name as unique key if available, otherwise fall back to id
            key = obj_name or obj_id
        
        if key:
            objects_by_type[obj_type][key] = element.attrib
        
        # Recursively process child elements
        for child in element:
            categorize_elements(child)

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


    input(f"Let's get started on file {file_path}...")

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

    # Start categorization from root
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

    # Extract dependencies
    for obj_type, objs in objects_by_type.items():
        for key, attrs in objs.items():
            for attr_name, attr_value in attrs.items():
                if attr_name not in ['implicit']:
                    if obj_type == 'draftBlock' and attr_name == 'name':
                        # Use the full name string as a single dependency
                        if attr_value and not re.fullmatch(r'[0-9.]+', attr_value):
                            dependencies[key].append(attr_value)
                    else:
                        # Special handling for point attributes that reference other objects
                        if obj_type == 'point' and attr_name in ['firstPoint', 'secondPoint', 'basePoint', 'center', 'p1Line', 'p2Line', 'thirdPoint']:
                            # These attributes directly reference other objects by ID
                            if attr_value and not re.fullmatch(r'[0-9.]+', attr_value):
                                dependencies[key].append(attr_value)
                        else:
                            print(f"attr_name: {attr_name}, attr_value: {attr_value}")
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