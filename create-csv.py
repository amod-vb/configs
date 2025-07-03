import json
import csv
import os
from pathlib import Path
from typing import Any, Dict, List, Union, Set

def flatten_json(data: Union[Dict, List], parent_key: str = '', separator: str = '.') -> Dict[str, Any]:
    """
    Flatten nested JSON data with custom list handling.
    
    For lists of objects, uses the object's "name" property as the key.
    For nested dictionaries, joins keys with the separator.
    """
    items = []
    
    if isinstance(data, dict):
        for key, value in data.items():
            new_key = f"{parent_key}{separator}{key}" if parent_key else key
            
            if isinstance(value, dict):
                items.extend(flatten_json(value, new_key, separator).items())
            elif isinstance(value, list):
                items.extend(flatten_json(value, new_key, separator).items())
            else:
                items.append((new_key, value))
    
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                if "name" in item:
                    name = item["name"]
                    new_key = f"{parent_key}{separator}{name}" if parent_key else name
                    
                    item_copy = {k: v for k, v in item.items() if k != "name"}
                    if item_copy:
                        items.extend(flatten_json(item_copy, new_key, separator).items())
                    else:
                        items.append((new_key, name))
                else:
                    for i, list_item in enumerate([item]):
                        new_key = f"{parent_key}{separator}{i}" if parent_key else str(i)
                        items.extend(flatten_json(list_item, new_key, separator).items())
            else:
                for i, list_item in enumerate(data):
                    new_key = f"{parent_key}{separator}{i}" if parent_key else str(i)
                    items.append((new_key, list_item))
                break
    
    return dict(items)

def process_json_files_in_directory(directory_path: str) -> Dict[str, Any]:
    """
    Process all JSON files in a directory and merge their flattened data.
    
    Args:
        directory_path: Path to the directory containing JSON files
    
    Returns:
        Dictionary with merged flattened data from all JSON files
    """
    merged_data = {}
    directory = Path(directory_path)
    
    # Find all JSON files in the directory
    json_files = list(directory.glob("*.json"))
    
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Flatten the JSON data
            flattened = flatten_json(data)
            
            # Add file prefix to avoid key conflicts
            file_prefix = json_file.stem  # filename without extension
            for key, value in flattened.items():
                prefixed_key = f"{file_prefix}.{key}" if len(json_files) > 1 else key
                merged_data[prefixed_key] = value
                
        except Exception as e:
            print(f"Error processing {json_file}: {e}")
    
    return merged_data

def create_csv_from_directories(output_file: str = "instruments_data.csv", 
                               script_directory: str = ".") -> None:
    """
    Create a CSV file from JSON data in subdirectories.
    
    Each subdirectory name becomes the "instrument" field value.
    Each row contains flattened data from all JSON files in that directory.
    
    Args:
        output_file: Name of the output CSV file
        script_directory: Directory to scan for subdirectories (default: current directory)
    """
    script_path = Path(script_directory)
    all_rows = []
    all_columns = set(["instrument"])  # Start with instrument column
    
    # Get all subdirectories
    subdirectories = [d for d in script_path.iterdir() if d.is_dir()]
    
    if not subdirectories:
        print("No subdirectories found!")
        return
    
    print(f"Found {len(subdirectories)} directories to process...")
    
    # Process each directory
    for directory in subdirectories:
        instrument_name = directory.name
        print(f"Processing directory: {instrument_name}")
        
        # Get flattened data from all JSON files in this directory
        flattened_data = process_json_files_in_directory(directory)
        
        if flattened_data:
            # Create row with instrument name
            row = {"instrument": instrument_name}
            row.update(flattened_data)
            all_rows.append(row)
            
            # Track all unique columns
            all_columns.update(flattened_data.keys())
        else:
            print(f"No JSON data found in {instrument_name}")
    
    if not all_rows:
        print("No data to write to CSV!")
        return
    
    # Sort columns for consistent output (instrument first, then alphabetical)
    sorted_columns = ["instrument"] + sorted([col for col in all_columns if col != "instrument"])
    
    # Write to CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=sorted_columns)
        writer.writeheader()
        writer.writerows(all_rows)
    
    print(f"CSV file created: {output_file}")
    print(f"Total rows: {len(all_rows)}")
    print(f"Total columns: {len(sorted_columns)}")

def preview_data(max_directories: int = 3) -> None:
    """
    Preview the data that would be processed without creating the CSV.
    
    Args:
        max_directories: Maximum number of directories to preview
    """
    script_path = Path(".")
    subdirectories = [d for d in script_path.iterdir() if d.is_dir()][:max_directories]
    
    print("Data Preview:")
    print("=" * 50)
    
    for directory in subdirectories:
        instrument_name = directory.name
        print(f"\nInstrument: {instrument_name}")
        print("-" * 30)
        
        flattened_data = process_json_files_in_directory(directory)
        
        if flattened_data:
            for key, value in list(flattened_data.items())[:5]:  # Show first 5 keys
                print(f"  {key}: {value}")
            if len(flattened_data) > 5:
                print(f"  ... and {len(flattened_data) - 5} more fields")
        else:
            print("  No JSON files found")

# Example usage
if __name__ == "__main__":
    # Preview what would be processed
    print("Previewing data structure...")
    preview_data()
    
    # Create the CSV file
    print("\nCreating CSV file...")
    create_csv_from_directories("instruments_data.csv")
    
    # You can also specify a different output file or directory
    # create_csv_from_directories("my_instruments.csv", "/path/to/your/data")
