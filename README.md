# Seamly2D Dependencies Analyzer

> **⚠️ Development Status: This code is still in active development and may contain bugs or incomplete features. Use at your own risk and expect breaking changes in future versions.**

A Python tool for analyzing dependencies in Seamly2D CAD pattern files (`.sm2d`). This script parses XML pattern files, categorizes elements by type, and extracts dependencies between various objects to create a comprehensive dependency graph.

## Overview

Seamly2D is an open-source patternmaking software that uses XML-based `.sm2d` files to store pattern data. This analyzer helps understand the complex relationships between different elements in a pattern, including:

- **Points**: Geometric points with coordinates and relationships
- **Lines**: Straight lines connecting points
- **Arcs**: Curved elements with radius and angle properties
- **Splines**: Complex curved elements (cubicBezier, simpleInteractive, pathInteractive)
- **Variables**: Custom calculations and formulas
- **Measurements**: Body measurements and dimensions
- **DraftBlocks**: Reusable pattern blocks
- **Operations**: Pattern construction operations

## Features

### 🔍 **Comprehensive Element Categorization**
- Recursively parses all XML elements in `.sm2d` files
- Categorizes elements by type (points, lines, variables, etc.)
- Handles nested elements and special cases
- Filters out display attributes to focus on functional relationships

### 📊 **Dependency Analysis**
- Extracts direct and indirect dependencies between objects
- Analyzes formula-based relationships
- Identifies measurement dependencies
- Tracks variable usage and dependencies

### 🎯 **Variable Analysis**
- Special focus on custom variables (starting with `#`)
- Recursive dependency tracing
- Usage analysis (what uses each variable)
- Comprehensive variable relationship mapping

### 📈 **Data Export**
- Generates detailed object categorization reports
- Creates dependency graphs
- Provides summary statistics
- Outputs structured data for further analysis

## Files

- **`seamlyDependencies.py`** - Main analysis script
- **`empty_measurements.csv`** - Reference file for measurement names
- **`empty_measurements_with header.csv`** - CSV with headers
- **`empty_measurements.smis`** - Seamly2D measurement file
- **`objects_by_type.txt`** - Generated output file with categorized objects

## Requirements

### Python Dependencies
```python
import xml.etree.ElementTree as ET
import os
import re
from collections import defaultdict
import csv
import tkinter as tk
from tkinter import filedialog
import pprint
```

### System Requirements
- Python 3.7+
- Windows/Linux/macOS
- Tkinter (usually included with Python)

## Usage

### Basic Usage
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

### Interactive Analysis
The script provides interactive prompts to:
- Review object categorization
- Examine dependency extraction
- Analyze specific variables
- View summary statistics

## Output

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

### Core Analysis Functions
- `categorize_elements()` - Main recursive categorization function
- `categorize_line()`, `categorize_point()`, `categorize_variable()` - Type-specific categorization
- `find_variable_dependencies()` - Recursive dependency tracing
- `analyze_variable()` - Comprehensive variable analysis

### Helper Functions
- `add_to_objects_by_type()` - Adds elements to categorization structure
- `create_filtered_element()` - Creates elements with filtered attributes
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

The script intelligently parses formulas to extract dependencies:
- Splits formulas on mathematical operators
- Filters out numbers and mathematical functions
- Identifies object references and measurements
- Handles special cases like `AngleLine` references

## Configuration

### Global Variables
- `block_id_counter` - Tracks draft block IDs
- `measurement_id_counter` - Tracks measurement IDs  
- `var_id_counter` - Tracks variable IDs (negative values)

### Attribute Categories
- `display_attributes` - Visual properties (filtered out)
- `id_attributes` - Reference attributes
- `formula_attributes` - Calculation attributes
- `point_attributes` - Point-specific attributes

## Error Handling

The script includes comprehensive error handling for:
- File not found errors
- XML parsing errors
- Missing attributes
- Invalid references
- CSV file issues

## Development

### Code Structure
- **Functional programming approach** (as per user requirements)
- Modular functions for each element type
- Clear separation of concerns
- Comprehensive documentation

### Debugging
- Detailed debug print statements
- Interactive prompts for troubleshooting
- Step-by-step processing information

## Contributing

1. Follow the functional programming paradigm
2. Add comprehensive error handling
3. Include debug output for new features
4. Update documentation for any changes

## License

This project is open source. Please check the license terms in your repository.

## Support

For issues or questions:
1. Check the debug output for error messages
2. Verify your `.sm2d` file is valid
3. Ensure all required files are present
4. Review the console output for processing details

---

**Note**: This tool is specifically designed for Seamly2D pattern files and may not work with other CAD file formats. 