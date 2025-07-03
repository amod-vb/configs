import csv
import pandas as pd
from typing import Dict, List, Tuple, Any, Optional
from pathlib import Path

class RowComparator:
    def __init__(self, csv_file: str):
        """
        Initialize the comparator with a CSV file.
        
        Args:
            csv_file: Path to the CSV file
        """
        self.csv_file = csv_file
        self.df = pd.read_csv(csv_file)
        self.instruments = self.df['instrument'].tolist() if 'instrument' in self.df.columns else []
    
    def get_available_instruments(self) -> List[str]:
        """Get list of available instruments (row identifiers)."""
        return self.instruments
    
    def get_row_by_instrument(self, instrument: str) -> Optional[Dict[str, Any]]:
        """
        Get a row by instrument name.
        
        Args:
            instrument: Name of the instrument
            
        Returns:
            Dictionary representation of the row, or None if not found
        """
        matching_rows = self.df[self.df['instrument'] == instrument]
        if matching_rows.empty:
            return None
        return matching_rows.iloc[0].to_dict()
    
    def get_row_by_index(self, index: int) -> Optional[Dict[str, Any]]:
        """
        Get a row by its index.
        
        Args:
            index: Row index (0-based)
            
        Returns:
            Dictionary representation of the row, or None if index is invalid
        """
        if 0 <= index < len(self.df):
            return self.df.iloc[index].to_dict()
        return None
    
    def compare_rows(self, row1: Dict[str, Any], row2: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare two rows and return a summary of differences.
        
        Args:
            row1: First row as dictionary
            row2: Second row as dictionary
            
        Returns:
            Dictionary containing comparison results
        """
        # Get all unique columns from both rows
        all_columns = set(row1.keys()) | set(row2.keys())
        
        # Remove instrument column from comparison (it's the identifier)
        comparison_columns = all_columns - {'instrument'}
        
        differences = {}
        only_in_row1 = {}
        only_in_row2 = {}
        same_values = {}
        
        for column in comparison_columns:
            val1 = row1.get(column)
            val2 = row2.get(column)
            
            # Handle NaN values (pandas represents missing values as NaN)
            val1_is_nan = pd.isna(val1) if val1 is not None else True
            val2_is_nan = pd.isna(val2) if val2 is not None else True
            
            if val1_is_nan and val2_is_nan:
                # Both are missing - consider them the same
                same_values[column] = "Both missing"
            elif val1_is_nan and not val2_is_nan:
                # Only row1 is missing this value
                only_in_row2[column] = val2
            elif not val1_is_nan and val2_is_nan:
                # Only row2 is missing this value
                only_in_row1[column] = val1
            elif val1 != val2:
                # Values are different
                differences[column] = {
                    row1['instrument']: val1,
                    row2['instrument']: val2
                }
            else:
                # Values are the same
                same_values[column] = val1
        
        return {
            'instruments_compared': (row1['instrument'], row2['instrument']),
            'differences': differences,
            'only_in_first': only_in_row1,
            'only_in_second': only_in_row2,
            'same_values': same_values,
            'summary': {
                'total_fields': len(comparison_columns),
                'different_fields': len(differences),
                'fields_only_in_first': len(only_in_row1),
                'fields_only_in_second': len(only_in_row2),
                'same_fields': len(same_values)
            }
        }
    
    def compare_by_instrument(self, instrument1: str, instrument2: str) -> Optional[Dict[str, Any]]:
        """
        Compare two instruments by name.
        
        Args:
            instrument1: Name of first instrument
            instrument2: Name of second instrument
            
        Returns:
            Comparison results or None if either instrument not found
        """
        row1 = self.get_row_by_instrument(instrument1)
        row2 = self.get_row_by_instrument(instrument2)
        
        if row1 is None:
            print(f"Instrument '{instrument1}' not found!")
            return None
        if row2 is None:
            print(f"Instrument '{instrument2}' not found!")
            return None
        
        return self.compare_rows(row1, row2)
    
    def compare_by_index(self, index1: int, index2: int) -> Optional[Dict[str, Any]]:
        """
        Compare two rows by their indices.
        
        Args:
            index1: Index of first row
            index2: Index of second row
            
        Returns:
            Comparison results or None if either index is invalid
        """
        row1 = self.get_row_by_index(index1)
        row2 = self.get_row_by_index(index2)
        
        if row1 is None:
            print(f"Row index {index1} is invalid!")
            return None
        if row2 is None:
            print(f"Row index {index2} is invalid!")
            return None
        
        return self.compare_rows(row1, row2)
    
    def print_comparison(self, comparison: Dict[str, Any]) -> None:
        """
        Print a formatted comparison summary.
        
        Args:
            comparison: Result from compare_rows or compare_by_instrument
        """
        if not comparison:
            print("No comparison data available.")
            return
        
        inst1, inst2 = comparison['instruments_compared']
        summary = comparison['summary']
        
        print(f"\n{'='*60}")
        print(f"COMPARISON: {inst1} vs {inst2}")
        print(f"{'='*60}")
        
        print(f"\nSUMMARY:")
        print(f"  Total fields compared: {summary['total_fields']}")
        print(f"  Different values: {summary['different_fields']}")
        print(f"  Only in {inst1}: {summary['fields_only_in_first']}")
        print(f"  Only in {inst2}: {summary['fields_only_in_second']}")
        print(f"  Same values: {summary['same_fields']}")
        
        if comparison['differences']:
            print(f"\nDIFFERENCES:")
            for field, values in comparison['differences'].items():
                print(f"  {field}:")
                print(f"    {inst1}: {values[inst1]}")
                print(f"    {inst2}: {values[inst2]}")
        
        if comparison['only_in_first']:
            print(f"\nONLY IN {inst1}:")
            for field, value in comparison['only_in_first'].items():
                print(f"  {field}: {value}")
        
        if comparison['only_in_second']:
            print(f"\nONLY IN {inst2}:")
            for field, value in comparison['only_in_second'].items():
                print(f"  {field}: {value}")
        
        if comparison['same_values']:
            print(f"\nSAME VALUES:")
            for field, value in list(comparison['same_values'].items())[:5]:  # Show first 5
                print(f"  {field}: {value}")
            if len(comparison['same_values']) > 5:
                print(f"  ... and {len(comparison['same_values']) - 5} more fields")

# Example usage and interactive functions
def interactive_comparison(csv_file: str):
    """
    Interactive function to compare instruments from command line.
    
    Args:
        csv_file: Path to the CSV file
    """
    comparator = RowComparator(csv_file)
    instruments = comparator.get_available_instruments()
    
    print(f"Available instruments: {', '.join(instruments)}")
    print("\nEnter two instrument names to compare, or 'quit' to exit:")
    
    while True:
        try:
            choice = input("\nEnter command (compare/list/quit): ").strip().lower()
            
            if choice == 'quit':
                break
            elif choice == 'list':
                print(f"Available instruments: {', '.join(instruments)}")
            elif choice == 'compare':
                inst1 = input("First instrument: ").strip()
                inst2 = input("Second instrument: ").strip()
                
                comparison = comparator.compare_by_instrument(inst1, inst2)
                if comparison:
                    comparator.print_comparison(comparison)
            else:
                print("Invalid command. Use 'compare', 'list', or 'quit'")
                
        except KeyboardInterrupt:
            print("\nExiting...")
            break

# Example usage
if __name__ == "__main__":
    # Example with the CSV file we created earlier
    csv_file = "instruments_data.csv"
    
    # Check if file exists
    if not Path(csv_file).exists():
        print(f"CSV file '{csv_file}' not found!")
        print("Please run the JSON to CSV processor first.")
    else:
        # Create comparator
        comparator = RowComparator(csv_file)
        
        # Show available instruments
        instruments = comparator.get_available_instruments()
        print(f"Available instruments: {instruments}")
        
        # Example comparison (if we have at least 2 instruments)
        if len(instruments) >= 2:
            print(f"\nExample comparison between {instruments[0]} and {instruments[1]}:")
            comparison = comparator.compare_by_instrument(instruments[0], instruments[1])
            if comparison:
                comparator.print_comparison(comparison)
        
        # Start interactive mode
        print("\nStarting interactive mode...")
        interactive_comparison(csv_file)
