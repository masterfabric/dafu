"""
Main entry point for customer analytics preprocessing and feature engineering.
Controls and orchestrates the preprocessing and feature engineering pipeline.

Usage:
    # Interactive mode (recommended)
    python main.py --interactive
    # or
    python interactive_cli.py
    
    # Command-line mode
    python main.py input.csv --feature-engineering
"""

import argparse
import sys
from pathlib import Path
from preprocessing import preprocess_data, DataFormatError, validate_data_format
from feature_engineering import engineer_features
import pandas as pd


def main():
    """Main function to run customer analytics preprocessing and feature engineering."""
    parser = argparse.ArgumentParser(
        description="Preprocess and engineer features for customer analytics data.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode (recommended for first-time users)
  python main.py --interactive
  
  # Command-line mode
  python main.py input.csv --feature-engineering
  
  # With custom options
  python main.py input.csv --feature-engineering --split-time 2015-08-20 --train-ratio 0.8
        """
    )
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Run in interactive mode (recommended)"
    )
    parser.add_argument(
        "input_file",
        type=str,
        nargs="?",
        help="Path to input CSV file (required in non-interactive mode)"
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default=None,
        help="Path to output aggregated sessions CSV (default: input_file with '_aggregated_sessions' suffix)"
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
    parser.add_argument(
        "--feature-engineering",
        action="store_true",
        help="Run feature engineering after preprocessing"
    )
    parser.add_argument(
        "--split-time",
        type=str,
        default=None,
        help="Split time for feature engineering (format: YYYY-MM-DD). If not provided, automatically calculated at 70%% point."
    )
    parser.add_argument(
        "--train-ratio",
        type=float,
        default=0.7,
        help="Ratio of data for feature calculation when split_time is auto-calculated (default: 0.7, meaning 70%% for features, 30%% for target)"
    )
    parser.add_argument(
        "--feature-output",
        type=str,
        default=None,
        help="Path to output feature engineering CSV (default: saves to results/ directory with timestamp)"
    )
    parser.add_argument(
        "--min-sessions",
        type=int,
        default=1,
        help="Minimum number of sessions required for feature engineering (default: 1)"
    )
    parser.add_argument(
        "--max-recency-days",
        type=int,
        default=31,
        help="Maximum days since last session for inclusion in feature engineering (default: 31)"
    )
    
    args = parser.parse_args()
    
    # If interactive mode, launch interactive CLI
    if args.interactive:
        try:
            from interactive_cli import CustomerAnalyticsCLI
            cli = CustomerAnalyticsCLI()
            cli.run()
            return
        except ImportError as e:
            print(f"❌ Error importing interactive CLI: {str(e)}")
            print("Falling back to command-line mode...")
        except Exception as e:
            print(f"❌ Error in interactive mode: {str(e)}")
            sys.exit(1)
    
    # Non-interactive mode requires input_file
    if not args.input_file:
        parser.error("input_file is required in non-interactive mode. Use --interactive for interactive mode.")
    
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
        
        # Validate train_ratio if provided
        if args.train_ratio <= 0 or args.train_ratio >= 1:
            print("ERROR: --train-ratio must be between 0 and 1 (e.g., 0.7 for 70%%)")
            sys.exit(1)
        
        # Preprocess data
        print(f"Processing data with session timeout: {args.timeout} minutes...")
        return_sessionized = args.feature_engineering
        result = preprocess_data(
            input_path=args.input_file,
            output_path=str(output_path) if not args.feature_engineering else None,
            session_timeout_minutes=args.timeout,
            return_sessionized=return_sessionized
        )
        
        if return_sessionized:
            aggregated_sessions, sessionized_data = result
        else:
            aggregated_sessions = result
            sessionized_data = None
        
        print(f"✓ Preprocessing completed successfully")
        print(f"  - Input rows: {len(df)}")
        print(f"  - Aggregated sessions: {len(aggregated_sessions)}")
        if not args.feature_engineering:
            print(f"  - Output saved to: {output_path}")
        
        # Run feature engineering if requested
        if args.feature_engineering:
            if args.split_time:
                print(f"\nRunning feature engineering with split_time: {args.split_time}...")
            else:
                print(f"\nRunning feature engineering with auto-calculated split_time...")
                print(f"  - Train ratio: {args.train_ratio*100:.0f}% for features, {(1-args.train_ratio)*100:.0f}% for target evaluation")
            
            # Determine feature output path
            # If not specified, None will be passed and engineer_features will save to results/ directory
            feature_output_path = args.feature_output
            
            classification_data, used_split_time, saved_output_path = engineer_features(
                aggregated_sessions=aggregated_sessions,
                sessionized_data=sessionized_data,
                split_time=args.split_time,
                output_path=feature_output_path,
                min_sessions=args.min_sessions,
                max_recency_days=args.max_recency_days,
                train_ratio=args.train_ratio
            )
            
            print(f"✓ Feature engineering completed successfully")
            print(f"  - Split time used: {used_split_time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Show data distribution
            pre_split_count = len(aggregated_sessions[aggregated_sessions["end_time"] < used_split_time])
            post_split_count = len(aggregated_sessions[aggregated_sessions["end_time"] >= used_split_time])
            total_count = len(aggregated_sessions)
            print(f"  - Sessions for features: {pre_split_count} ({pre_split_count/total_count*100:.1f}%)")
            print(f"  - Sessions for target: {post_split_count} ({post_split_count/total_count*100:.1f}%)")
            print(f"  - Customers in final dataset: {len(classification_data)}")
            print(f"  - Features calculated: {len(classification_data.columns) - 2}")  # Exclude visitorid and target_class
            print(f"  - Output saved to: {saved_output_path}")
            
            # Save aggregated sessions if output path was provided
            if args.output:
                aggregated_sessions.to_csv(str(output_path), index=False)
                print(f"  - Aggregated sessions saved to: {output_path}")
        
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

