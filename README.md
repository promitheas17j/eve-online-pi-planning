# PI Planner

This project aims to help identify solar systems that contain specific combinations of planetary raw PI (P0), based on CSV input data. It supports saving and reloading previous queries, and exporting results to CSV files.

## Features
- Reads planetary data from CSV files in the Regions/ directory (data is from dotlan.net)
- Allows interactive selection of target raw PI materials
- Finds all solar systems that can produce all selected raw PI completely in within themselves (no need to spread out across multiple systems)
- Can display a bit more in-depth information for each matching system found
- Saves query states and results to dedicated directories
- Allows to load previously saved queries to continue where you left off

## Requirements
- Python 3.7 or higher
- Standard modules only - no external dependencies
