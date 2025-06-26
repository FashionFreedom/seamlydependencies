# Developer notes

> **⚠️ Development Status: This code is still in active development and may contain bugs or incomplete features. Use at your own risk and expect breaking changes in future versions.**

## Files

- **`seamlyDependencies.py`** - Main analysis script
- **`empty_measurements.csv`** - Reference file for measurement names
- **`objects_by_type.txt`** - Generated output file with categorized objects

## Requirements

- Python 3.7+
- Windows/Linux/macOS
- Tkinter (usually included with Python)

## Usage

1. Run the script:
   ```bash
   python seamlyDependencies.py
   ```

2. A file dialog will open - select your `.sm2d` pattern file

3. The script will:
   - Parse and categorize all elements
   - Extract dependencies
   - Display analysis results
   - Generate output files

### Console Output

- Real-time processing information
- Object categorization results
- Dependency mapping
- Variable analysis
- Summary statistics

### Generated Files

- **`objects_by_type.txt`**: Detailed categorization of all objects by type
- Console output with dependency graphs and analysis

## Key Functions

### Analysis Functions
- `categorize_elements()` - Main recursive categorization function
- `categorize_line()`, `categorize_point()`, `categorize_variable()` - Type-specific categorization
- `find_variable_dependencies()` - Recursive dependency tracing
- `analyze_variable()` - Variable analysis

### Helper Functions
- `add_to_objects_by_type()` - Adds elements to categorization structure
- `create_filtered_element()` - Creates elements with selected attributes, removes attributes not needed for analysis
- `lookup_name_by_id()` - Cross-references objects by ID
- `find_in_csv_first_column()` - Searches measurement references

## Data Structures

### `objects_by_type`
```python
{
    'point': {'pointA': {...}, 'pointB': {...}},
    'line': {'lineAB': {...}, 'lineBC': {...}},
    'variable': {'#EaseRatioBust': {...}},
    # ... other types
}
```

### `dependencies`
```python
{
    'obj_id': {
        'name': 'object_name',
        'dependencies': [['dep_id', 'dep_name'], ...]
    }
}
```

## Element Types Handled

### Geometric Elements
- **Points**: Base points, center points, intersection points
- **Lines**: Straight lines, construction lines
- **Arcs**: Circular arcs, elliptical arcs
- **Splines**: Cubic Bezier, interactive splines

### Pattern Elements
- **Variables**: Custom calculations and formulas
- **Measurements**: Body measurements and dimensions
- **DraftBlocks**: Reusable pattern components
- **Operations**: Pattern construction operations

### Special Cases
- **Intersection Points**: Points created by line intersections
- **End Points**: Points at line endpoints
- **Axis Intersections**: Points where lines meet axes

## Formula Analysis

Parses formulas to extract dependencies:
- Splits formulas on mathematical operators
- Filters out numbers and mathematical functions
- Identifies object references and measurements
- Handles special cases like references to implicit objects 

## License

GPLv3


---

