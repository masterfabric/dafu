"""
Main entry point for customer analytics preprocessing.
Controls and orchestrates the preprocessing pipeline.
"""

import argparse
import sys
from pathlib import Path
from preprocessing import preprocess_data, DataFormatError, validate_data_format
import pandas as pd


def main():
    """Main function to run customer analytics preprocessing."""
    parser = argparse.ArgumentParser(
        description="Preprocess customer analytics data: validate, sessionize, and aggregate."
    )
    parser.add_argument(
        "input_file",
        type=str,
        help="Path to input CSV file"
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default=None,
        help="Path to output CSV file (default: input_file with '_aggregated_sessions' suffix)"
    )
    parser.add_argument(
        "-t", "--timeout",
        type=int,
        default=15,
        help="Session timeout in minutes (default: 15)"
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Only validate data format without processing"
    )
    
    args = parser.parse_args()
    
    # Determine output path
    if args.output is None:
        input_path = Path(args.input_file)
        output_path = input_path.parent / f"{input_path.stem}_aggregated_sessions.csv"
    else:
        output_path = args.output
    
    try:
        # Read and validate data
        print(f"Reading data from: {args.input_file}")
        df = pd.read_csv(args.input_file)
        
        print("Validating data format...")
        is_valid, error_msg = validate_data_format(df)
        
        if not is_valid:
            print("ERROR: Data format validation failed!")
            print(error_msg)
            sys.exit(1)
        
        print("✓ Data format validation passed")
        
        if args.validate_only:
            print("Validation-only mode: exiting without processing.")
            sys.exit(0)
        
        # Preprocess data
        print(f"Processing data with session timeout: {args.timeout} minutes...")
        aggregated_sessions = preprocess_data(
            input_path=args.input_file,
            output_path=str(output_path),
            session_timeout_minutes=args.timeout
        )
        
        print(f"✓ Preprocessing completed successfully")
        print(f"  - Input rows: {len(df)}")
        print(f"  - Aggregated sessions: {len(aggregated_sessions)}")
        print(f"  - Output saved to: {output_path}")
        
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        sys.exit(1)
    except DataFormatError as e:
        print(f"ERROR: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

