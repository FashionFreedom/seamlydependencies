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
