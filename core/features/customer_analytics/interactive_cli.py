"""
Interactive CLI for Customer Analytics
Provides a user-friendly terminal interface for data preprocessing and feature engineering.
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import pandas as pd

# Add current directory to path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from preprocessing import preprocess_data, DataFormatError, validate_data_format
from feature_engineering import engineer_features
from modeling import launch_modeling


class CustomerAnalyticsCLI:
    """Interactive CLI for Customer Analytics processing."""
    
    def __init__(self):
        """Initialize the CLI."""
        self.input_file = None
        self.session_timeout = 15
        self.run_feature_engineering = False
        self.split_time = None
        self.train_ratio = 0.7
        self.min_sessions = 1
        self.max_recency_days = 31
        self.save_aggregated_sessions = False
        self.aggregated_sessions_path = None
        self.save_classification_data = True
        self.classification_data_path = None
        self.use_default_location = True
        self.use_default_filename = True
        self.latest_classification_data = None
        self.latest_classification_path = None
    
    def display_welcome_message(self):
        """Display welcome message."""
        print("\n" + "="*80)
        print("📊 CUSTOMER ANALYTICS PLATFORM")
        print("="*80)
        print("Data Preprocessing and Feature Engineering for Customer Behavior Analysis")
        print("Version: 1.0.0")
        print("="*80)
        print("\nThis platform provides:")
        print("• CSV data validation and format checking")
        print("• Sessionization (15-minute timeout by default)")
        print("• Session-level feature aggregation")
        print("• Customer-level feature engineering")
        print("• Churn prediction dataset creation")
        print("="*80)
    
    @staticmethod
    def _prompt_yes_no(message, default=True):
        """Prompt user for yes/no input."""
        suffix = " [Y/n]: " if default else " [y/N]: "
        while True:
            response = input(f"{message}{suffix}").strip().lower()
            if not response:
                return default
            if response in ("y", "yes"):
                return True
            if response in ("n", "no"):
                return False
            print("❌ Please enter 'y' or 'n'.")

    def get_input_file(self):
        """Get input CSV file path from user."""
        print("\n" + "="*60)
        print("📁 DATA SOURCE")
        print("="*60)
        
        while True:
            file_path = input("Enter CSV file path: ").strip()
            
            if not file_path:
                print("❌ Please enter a file path.")
                continue
            
            # Remove quotes if present
            file_path = file_path.strip('"').strip("'")
            
            if not os.path.exists(file_path):
                print(f"❌ File not found: {file_path}")
                retry = input("Try again? (y/n): ").strip().lower()
                if retry not in ['y', 'yes']:
                    return False
                continue
            
            if not file_path.lower().endswith('.csv'):
                print("⚠️  Warning: File doesn't have .csv extension.")
                proceed = input("Continue anyway? (y/n): ").strip().lower()
                if proceed not in ['y', 'yes']:
                    continue
            
            self.input_file = file_path
            print(f"✅ File found: {file_path}")
            return True
    
    def validate_data(self):
        """Validate the input data format."""
        print("\n" + "="*60)
        print("🔍 VALIDATING DATA FORMAT")
        print("="*60)
        
        try:
            print(f"Reading data from: {self.input_file}")
            df = pd.read_csv(self.input_file)
            
            print("Validating data format...")
            is_valid, error_msg = validate_data_format(df)
            
            if not is_valid:
                print("\n❌ Data format validation failed!")
                print(error_msg)
                return False
            
            print("✅ Data format validation passed")
            print(f"  - Total rows: {len(df):,}")
            print(f"  - Columns: {', '.join(df.columns.tolist())}")
            return True
            
        except Exception as e:
            print(f"\n❌ Error reading file: {str(e)}")
            return False
    
    def get_session_timeout(self):
        """Get session timeout from user."""
        print("\n" + "="*60)
        print("⏱️  SESSION TIMEOUT")
        print("="*60)
        print("Session timeout determines when a new session starts.")
        print("Default: 15 minutes (new session if visitor changes or 15+ min gap)")
        
        while True:
            timeout_input = input("\nEnter session timeout in minutes (or press Enter for default 15): ").strip()
            
            if not timeout_input:
                self.session_timeout = 15
                print(f"✅ Using default timeout: {self.session_timeout} minutes")
                return True
            
            try:
                timeout = int(timeout_input)
                if timeout <= 0:
                    print("❌ Timeout must be a positive number.")
                    continue
                self.session_timeout = timeout
                print(f"✅ Session timeout set to: {self.session_timeout} minutes")
                return True
            except ValueError:
                print("❌ Please enter a valid number.")
    
    def get_feature_engineering_options(self):
        """Get feature engineering options from user."""
        print("\n" + "="*60)
        print("🔧 FEATURE ENGINEERING")
        print("="*60)
        print("Feature engineering creates customer-level features and target variables")
        print("for churn prediction models.")
        
        while True:
            choice = input("\nRun feature engineering? (y/n): ").strip().lower()
            
            if choice in ['y', 'yes']:
                self.run_feature_engineering = True
                break
            elif choice in ['n', 'no']:
                self.run_feature_engineering = False
                print("✅ Feature engineering will be skipped.")
                return True
            else:
                print("❌ Please enter 'y' or 'n'.")
        
        # Get split_time option
        print("\n" + "-"*60)
        print("SPLIT TIME CONFIGURATION")
        print("-"*60)
        print("Split time divides data into:")
        print("  • Features: Sessions BEFORE split_time (historical behavior)")
        print("  • Target: Sessions AFTER split_time (future behavior)")
        print("\nOptions:")
        print("  1. Auto-calculate (recommended) - splits at 70% point")
        print("  2. Manual - specify a date (YYYY-MM-DD)")
        
        while True:
            split_choice = input("\nChoose option (1 or 2): ").strip()
            
            if split_choice == '1':
                # Get train ratio
                print("\nTrain ratio determines how much data to use for features.")
                while True:
                    ratio_input = input("Enter train ratio (0.1-0.9, default 0.7): ").strip()
                    if not ratio_input:
                        self.train_ratio = 0.7
                        break
                    try:
                        ratio = float(ratio_input)
                        if 0.1 <= ratio <= 0.9:
                            self.train_ratio = ratio
                            break
                        else:
                            print("❌ Ratio must be between 0.1 and 0.9.")
                    except ValueError:
                        print("❌ Please enter a valid number.")
                
                print(f"✅ Split time will be auto-calculated at {self.train_ratio*100:.0f}% point")
                self.split_time = None
                return True
                
            elif split_choice == '2':
                while True:
                    date_input = input("Enter split time (YYYY-MM-DD): ").strip()
                    try:
                        # Validate date format
                        datetime.strptime(date_input, '%Y-%m-%d')
                        self.split_time = date_input
                        print(f"✅ Split time set to: {self.split_time}")
                        return True
                    except ValueError:
                        print("❌ Invalid date format. Please use YYYY-MM-DD (e.g., 2015-08-20)")
            else:
                print("❌ Please enter '1' or '2'.")
        
        # Get filtering options
        print("\n" + "-"*60)
        print("FILTERING OPTIONS")
        print("-"*60)
        
        while True:
            min_sessions_input = input("Minimum sessions required (default 1): ").strip()
            if not min_sessions_input:
                self.min_sessions = 1
                break
            try:
                self.min_sessions = int(min_sessions_input)
                if self.min_sessions < 1:
                    print("❌ Minimum sessions must be at least 1.")
                    continue
                break
            except ValueError:
                print("❌ Please enter a valid number.")
        
        while True:
            max_recency_input = input("Maximum recency days (default 31): ").strip()
            if not max_recency_input:
                self.max_recency_days = 31
                break
            try:
                self.max_recency_days = int(max_recency_input)
                if self.max_recency_days < 1:
                    print("❌ Maximum recency must be at least 1.")
                    continue
                break
            except ValueError:
                print("❌ Please enter a valid number.")
        
        return True
    
    def get_save_options(self):
        """Get save options from user."""
        print("\n" + "="*60)
        print("💾 SAVE OPTIONS")
        print("="*60)
        
        # Ask about aggregated sessions
        if not self.run_feature_engineering:
            print("Save aggregated sessions CSV?")
            while True:
                choice = input("Save aggregated sessions? (y/n): ").strip().lower()
                if choice in ['y', 'yes']:
                    self.save_aggregated_sessions = True
                    break
                elif choice in ['n', 'no']:
                    self.save_aggregated_sessions = False
                    break
                else:
                    print("❌ Please enter 'y' or 'n'.")
            
            if self.save_aggregated_sessions:
                self._get_aggregated_sessions_save_location()
        
        # Ask about classification data (if feature engineering is enabled)
        if self.run_feature_engineering:
            print("Save classification data CSV?")
            while True:
                choice = input("Save classification data? (y/n, default: y): ").strip().lower()
                if not choice or choice in ['y', 'yes']:
                    self.save_classification_data = True
                    break
                elif choice in ['n', 'no']:
                    self.save_classification_data = False
                    break
                else:
                    print("❌ Please enter 'y' or 'n'.")
            
            if self.save_classification_data:
                self._get_classification_data_save_location()
    
    def _get_aggregated_sessions_save_location(self):
        """Get save location for aggregated sessions."""
        print("\n" + "-"*60)
        print("AGGREGATED SESSIONS SAVE LOCATION")
        print("-"*60)
        print("Options:")
        print("  1. Default location (same directory as input file)")
        print("  2. Custom location")
        
        while True:
            choice = input("\nChoose option (1 or 2): ").strip()
            
            if choice == '1':
                self.use_default_location = True
                input_path = Path(self.input_file)
                self.aggregated_sessions_path = str(
                    input_path.parent / f"{input_path.stem}_aggregated_sessions.csv"
                )
                print(f"✅ Will save to: {self.aggregated_sessions_path}")
                return True
                
            elif choice == '2':
                self.use_default_location = False
                while True:
                    custom_path = input("Enter full file path: ").strip().strip('"').strip("'")
                    if not custom_path:
                        print("❌ Please enter a valid path.")
                        continue
                    if not custom_path.endswith('.csv'):
                        custom_path += '.csv'
                    self.aggregated_sessions_path = custom_path
                    print(f"✅ Will save to: {self.aggregated_sessions_path}")
                    return True
            else:
                print("❌ Please enter '1' or '2'.")
    
    def _get_classification_data_save_location(self):
        """Get save location for classification data."""
        print("\n" + "-"*60)
        print("CLASSIFICATION DATA SAVE LOCATION")
        print("-"*60)
        print("Options:")
        print("  1. Default location (results/ directory with timestamp)")
        print("  2. Custom location")
        
        while True:
            choice = input("\nChoose option (1 or 2): ").strip()
            
            if choice == '1':
                self.use_default_location = True
                self.use_default_filename = True
                # Will be set in feature_engineering.py
                self.classification_data_path = None
                current_file = Path(__file__).resolve()
                results_dir = current_file.parent / "results"
                print(f"✅ Will save to: {results_dir}/classification_data_TIMESTAMP.csv")
                return True
                
            elif choice == '2':
                self.use_default_location = False
                
                # Get directory
                while True:
                    dir_path = input("Enter directory path (or press Enter for current directory): ").strip().strip('"').strip("'")
                    if not dir_path:
                        dir_path = str(Path.cwd())
                    
                    if not os.path.isdir(dir_path):
                        create = input(f"Directory doesn't exist. Create it? (y/n): ").strip().lower()
                        if create in ['y', 'yes']:
                            os.makedirs(dir_path, exist_ok=True)
                        else:
                            continue
                    
                    break
                
                # Get filename
                print("\nFilename options:")
                print("  1. Default (classification_data_TIMESTAMP.csv)")
                print("  2. Custom filename")
                
                while True:
                    filename_choice = input("Choose option (1 or 2): ").strip()
                    
                    if filename_choice == '1':
                        self.use_default_filename = True
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"classification_data_{timestamp}.csv"
                        self.classification_data_path = os.path.join(dir_path, filename)
                        print(f"✅ Will save to: {self.classification_data_path}")
                        return True
                        
                    elif filename_choice == '2':
                        self.use_default_filename = False
                        while True:
                            filename = input("Enter filename (without extension): ").strip()
                            if not filename:
                                print("❌ Please enter a filename.")
                                continue
                            if not filename.endswith('.csv'):
                                filename += '.csv'
                            self.classification_data_path = os.path.join(dir_path, filename)
                            print(f"✅ Will save to: {self.classification_data_path}")
                            return True
                    else:
                        print("❌ Please enter '1' or '2'.")
            else:
                print("❌ Please enter '1' or '2'.")
    
    def process_data(self):
        """Process the data based on user selections."""
        context = {
            "success": False,
            "classification_data": None,
            "classification_path": None,
            "split_time": None,
        }
        print("\n" + "="*80)
        print("🚀 PROCESSING DATA")
        print("="*80)
        
        try:
            # Step 1: Preprocessing
            print("\n📊 Step 1: Preprocessing data...")
            print(f"  - Session timeout: {self.session_timeout} minutes")
            
            return_sessionized = self.run_feature_engineering
            output_path = self.aggregated_sessions_path if self.save_aggregated_sessions else None
            
            result = preprocess_data(
                input_path=self.input_file,
                output_path=output_path,
                session_timeout_minutes=self.session_timeout,
                return_sessionized=return_sessionized
            )
            
            if return_sessionized:
                aggregated_sessions, sessionized_data = result
            else:
                aggregated_sessions = result
                sessionized_data = None
            
            print(f"✅ Preprocessing completed")
            print(f"  - Aggregated sessions: {len(aggregated_sessions):,}")
            
            if output_path:
                print(f"  - Saved to: {output_path}")
            
            # Step 2: Feature Engineering (if enabled)
            if self.run_feature_engineering:
                print("\n🔧 Step 2: Feature engineering...")
                
                if self.split_time:
                    print(f"  - Split time: {self.split_time}")
                else:
                    print(f"  - Auto-calculating split time at {self.train_ratio*100:.0f}% point")
                
                output_path = self.classification_data_path if self.save_classification_data else None
                
                classification_data, used_split_time, saved_path = engineer_features(
                    aggregated_sessions=aggregated_sessions,
                    sessionized_data=sessionized_data,
                    split_time=self.split_time,
                    output_path=output_path,
                    min_sessions=self.min_sessions,
                    max_recency_days=self.max_recency_days,
                    train_ratio=self.train_ratio
                )
                
                print(f"✅ Feature engineering completed")
                print(f"  - Split time used: {used_split_time.strftime('%Y-%m-%d %H:%M:%S')}")
                
                # Show data distribution
                pre_split_count = len(aggregated_sessions[aggregated_sessions["end_time"] < used_split_time])
                post_split_count = len(aggregated_sessions[aggregated_sessions["end_time"] >= used_split_time])
                total_count = len(aggregated_sessions)
                print(f"  - Sessions for features: {pre_split_count:,} ({pre_split_count/total_count*100:.1f}%)")
                print(f"  - Sessions for target: {post_split_count:,} ({post_split_count/total_count*100:.1f}%)")
                print(f"  - Customers in final dataset: {len(classification_data):,}")
                print(f"  - Features calculated: {len(classification_data.columns) - 2}")
                
                if saved_path:
                    print(f"  - Saved to: {saved_path}")
                    context["classification_path"] = str(saved_path)
                else:
                    context["classification_path"] = None

                context["classification_data"] = classification_data
                context["split_time"] = used_split_time
                self.latest_classification_data = classification_data
                self.latest_classification_path = (
                    str(saved_path) if saved_path else self.classification_data_path
                )
            else:
                self.latest_classification_data = None
                self.latest_classification_path = None
            
            print("\n" + "="*80)
            print("✅ ALL PROCESSING COMPLETED SUCCESSFULLY!")
            print("="*80)
            
            context["success"] = True
            return context
            
        except DataFormatError as e:
            print(f"\n❌ Data format error: {str(e)}")
            return context
        except FileNotFoundError as e:
            print(f"\n❌ File not found: {str(e)}")
            return context
        except Exception as e:
            print(f"\n❌ Unexpected error: {str(e)}")
            import traceback
            traceback.print_exc()
            return context
    
    def run_modeling_workflow(self, classification_data=None, classification_path=None):
        """Launch modeling workflows if the user opts in."""
        print("\n" + "="*80)
        print("📈 ADVANCED MODELING & SEGMENTATION")
        print("="*80)
        print("Run predictive pipelines (churn, CLV) and segmentation on engineered features.")
        
        default_choice = bool(classification_data is not None or classification_path)
        if not self._prompt_yes_no("Proceed to modeling workflows?", default=default_choice):
            print("⏭️  Skipping modeling stage.")
            return
        
        default_path = classification_path or self.latest_classification_path
        if default_path:
            print(f"\nUsing dataset: {default_path}")
        else:
            print("\nNo recent classification dataset detected. You can provide a compatible CSV path manually.")
        
        try:
            launch_modeling(
                default_dataset_path=default_path,
                classification_data=classification_data
            )
        except ImportError as err:
            print(f"\n❌ Modeling dependencies missing: {err}")
            print("Install required packages (e.g., scikit-learn, xgboost, lightgbm, catboost, hdbscan) and retry.")
        except Exception as err:
            print(f"\n❌ Modeling workflow failed: {err}")
            import traceback
            traceback.print_exc()
    
    def run(self):
        """Run the interactive CLI."""
        try:
            # Display welcome
            self.display_welcome_message()
            
            # Get input file
            if not self.get_input_file():
                print("\n👋 Exiting...")
                return
            
            # Validate data
            if not self.validate_data():
                print("\n👋 Exiting due to validation errors...")
                return
            
            # Get session timeout
            if not self.get_session_timeout():
                print("\n👋 Exiting...")
                return
            
            # Get feature engineering options
            if not self.get_feature_engineering_options():
                print("\n👋 Exiting...")
                return
            
            # Get save options
            self.get_save_options()
            
            # Process data
            process_context = self.process_data()
            if not process_context.get("success"):
                print("\n👋 Exiting due to processing errors...")
                return
            
            # Optional modeling workflows
            self.run_modeling_workflow(
                classification_data=process_context.get("classification_data"),
                classification_path=process_context.get("classification_path")
            )
            
            # Exit message
            print("\n" + "="*80)
            print("👋 Thank you for using Customer Analytics Platform!")
            print("="*80)
            print("\n")
            
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted by user. Goodbye!")
            sys.exit(0)
        except Exception as e:
            print(f"\n❌ Unexpected error: {str(e)}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


def main():
    """Main entry point for interactive CLI."""
    cli = CustomerAnalyticsCLI()
    cli.run()


if __name__ == "__main__":
    main()

