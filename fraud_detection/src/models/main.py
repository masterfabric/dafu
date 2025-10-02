"""
Main Entry Point for Fraud Detection Models

This module provides a unified interface for selecting and running different
fraud detection models including Isolation Forest, Risk Score, LSTM, and GRU.

Author: Enterprise Fraud Detection Platform
Version: 1.0.0
"""

import os
import sys
import logging
from typing import Optional

# Add the parent directory to the path to import the models
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

# Lazy imports - only import when needed to speed up startup
IsolationForestFraudDetector = None
SequenceFraudDetector = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FraudDetectionMain:
    """
    Main controller class for fraud detection model selection and execution.
    
    This class provides a unified interface for choosing between different
    fraud detection approaches and routing to the appropriate model implementation.
    """
    
    def __init__(self):
        """Initialize the main fraud detection controller."""
        self.selected_model = None
        self.model_instance = None
        
    def display_welcome_message(self) -> None:
        """Display welcome message and system information."""
        print("\n" + "="*80)
        print("🔍 ENTERPRISE FRAUD DETECTION PLATFORM")
        print("="*80)
        print("Advanced Machine Learning Models for Fraud Detection")
        print("Version: 1.0.0")
        print("="*80)
        print("\nThis platform offers multiple fraud detection approaches:")
        print("• Traditional ML: Isolation Forest with Risk Score analysis")
        print("• Deep Learning: LSTM and GRU sequence-based models")
        print("• Both supervised and unsupervised learning modes")
        print("• Real-time streaming and batch processing capabilities")
        print("="*80)
        print("\n⚡ Fast startup - models load only when selected!")
    
    def display_model_options(self) -> None:
        """Display available model options to the user."""
        print("\n" + "="*60)
        print("🎯 SELECT FRAUD DETECTION MODEL")
        print("="*60)
        print("Choose the type of fraud detection model you want to use:")
        print()
        print("1. 🔍 ISOLATION FOREST & RISK SCORE")
        print("   • Traditional machine learning approach")
        print("   • Excellent for tabular data with numerical features")
        print("   • Supports both supervised and unsupervised learning")
        print("   • Risk score based anomaly detection")
        print("   • Fast training and prediction")
        print()
        print("2. 🧠 SEQUENCE MODELS (LSTM & GRU)")
        print("   • Deep learning approach for sequential data")
        print("   • Captures temporal patterns and dependencies")
        print("   • Autoencoder architecture for anomaly detection")
        print("   • Best for time-series and transaction sequences")
        print("   • More complex but potentially more accurate")
        print()
        print("3. ℹ️  MODEL COMPARISON")
        print("   • Compare different models on the same dataset")
        print("   • Get recommendations based on your data")
        print()
        print("4. ❓ HELP & INFORMATION")
        print("   • Detailed information about each model")
        print("   • Data requirements and recommendations")
        print()
        print("5. 🚪 EXIT")
        print("   • Exit the application")
        print("="*60)
    
    def get_model_choice(self) -> str:
        """Get user's model choice with validation."""
        while True:
            try:
                choice = input("\nEnter your choice (1-5): ").strip()
                
                if choice in ['1', '2', '3', '4', '5']:
                    return choice
                else:
                    print("❌ Please enter a valid choice (1-5)")
                    
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                sys.exit(0)
            except Exception as e:
                print(f"❌ Error: {str(e)}")
                print("Please try again.")
    
    def show_model_information(self) -> None:
        """Display detailed information about each model type."""
        print("\n" + "="*80)
        print("📚 MODEL INFORMATION & RECOMMENDATIONS")
        print("="*80)
        
        print("\n🔍 ISOLATION FOREST & RISK SCORE:")
        print("-" * 50)
        print("• Algorithm: Isolation Forest (Ensemble of Decision Trees)")
        print("• Best for: Tabular data with numerical features")
        print("• Data requirements:")
        print("  - At least 2 numerical features")
        print("  - Minimum 100 samples for reliable results")
        print("  - Can handle missing values and categorical data")
        print("• Advantages:")
        print("  - Fast training and prediction")
        print("  - No need for labeled data (unsupervised)")
        print("  - Interpretable results")
        print("  - Handles high-dimensional data well")
        print("• Use cases:")
        print("  - Credit card fraud detection")
        print("  - Insurance claim fraud")
        print("  - Network intrusion detection")
        print("  - General anomaly detection")
        
        print("\n🧠 SEQUENCE MODELS (LSTM & GRU):")
        print("-" * 50)
        print("• Algorithms: LSTM (Long Short-Term Memory) & GRU (Gated Recurrent Unit)")
        print("• Best for: Sequential data with temporal patterns")
        print("• Data requirements:")
        print("  - Sequential data (time-series, transaction sequences)")
        print("  - Minimum 1000 samples for reliable training")
        print("  - Consistent sequence length")
        print("  - Numerical features work best")
        print("• Advantages:")
        print("  - Captures complex temporal dependencies")
        print("  - Can learn from sequence patterns")
        print("  - State-of-the-art performance on sequential data")
        print("  - Autoencoder architecture for anomaly detection")
        print("• Use cases:")
        print("  - Transaction sequence fraud detection")
        print("  - User behavior analysis")
        print("  - Time-series anomaly detection")
        print("  - Pattern-based fraud detection")
        
        print("\n💡 RECOMMENDATIONS:")
        print("-" * 50)
        print("• Choose Isolation Forest if:")
        print("  - You have tabular data with numerical features")
        print("  - You need fast results")
        print("  - You have limited computational resources")
        print("  - You want interpretable results")
        print()
        print("• Choose Sequence Models if:")
        print("  - You have sequential/temporal data")
        print("  - You need to capture complex patterns")
        print("  - You have sufficient computational resources")
        print("  - You have large datasets (>1000 samples)")
        print()
        print("• Choose Model Comparison if:")
        print("  - You're unsure which model to use")
        print("  - You want to evaluate multiple approaches")
        print("  - You have time to run multiple models")
        
        print("\n" + "="*80)
    
    def compare_models(self) -> None:
        """Provide model comparison and recommendations."""
        print("\n" + "="*80)
        print("⚖️  MODEL COMPARISON & RECOMMENDATIONS")
        print("="*80)
        
        print("\n📊 COMPARISON TABLE:")
        print("-" * 80)
        print(f"{'Feature':<25} {'Isolation Forest':<20} {'Sequence Models':<20}")
        print("-" * 80)
        print(f"{'Training Speed':<25} {'Fast':<20} {'Slow':<20}")
        print(f"{'Prediction Speed':<25} {'Very Fast':<20} {'Fast':<20}")
        print(f"{'Memory Usage':<25} {'Low':<20} {'High':<20}")
        print(f"{'Data Requirements':<25} {'Low':<20} {'High':<20}")
        print(f"{'Interpretability':<25} {'High':<20} {'Low':<20}")
        print(f"{'Temporal Patterns':<25} {'No':<20} {'Yes':<20}")
        print(f"{'Handles Missing Data':<25} {'Yes':<20} {'Limited':<20}")
        print(f"{'Unsupervised Learning':<25} {'Yes':<20} {'Yes':<20}")
        print(f"{'Best for Small Data':<25} {'Yes':<20} {'No':<20}")
        print(f"{'Best for Large Data':<25} {'Yes':<20} {'Yes':<20}")
        print("-" * 80)
        
        print("\n🎯 DECISION TREE:")
        print("-" * 50)
        print("1. Is your data sequential/temporal?")
        print("   → YES: Choose Sequence Models (LSTM/GRU)")
        print("   → NO: Continue to question 2")
        print()
        print("2. Do you need fast results?")
        print("   → YES: Choose Isolation Forest")
        print("   → NO: Continue to question 3")
        print()
        print("3. Do you have >1000 samples?")
        print("   → YES: Choose Sequence Models for better accuracy")
        print("   → NO: Choose Isolation Forest")
        print()
        print("4. Do you need interpretable results?")
        print("   → YES: Choose Isolation Forest")
        print("   → NO: Choose Sequence Models")
        
        print("\n💡 QUICK RECOMMENDATIONS:")
        print("-" * 50)
        print("• For beginners: Start with Isolation Forest")
        print("• For time-series data: Use Sequence Models")
        print("• For real-time systems: Use Isolation Forest")
        print("• For research/experimentation: Try both and compare")
        print("• For production with limited resources: Use Isolation Forest")
        print("• For maximum accuracy on sequential data: Use Sequence Models")
        
        print("\n" + "="*80)
    
    def _show_return_options(self) -> None:
        """Show return options after displaying information."""
        print("\n" + "="*60)
        print("🔄 WHAT WOULD YOU LIKE TO DO NEXT?")
        print("="*60)
        print("1. 🏠 Return to Main Menu")
        print("2. 🚪 Exit Application")
        print("="*60)
        
        while True:
            try:
                choice = input("\nEnter your choice (1-2): ").strip()
                
                if choice == '1':
                    print("\n🔄 Returning to main menu...")
                    return  # This will continue the main loop
                elif choice == '2':
                    print("\n👋 Thank you for using the Fraud Detection Platform!")
                    print("Goodbye!")
                    sys.exit(0)
                else:
                    print("❌ Please enter '1' or '2'")
                    
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                sys.exit(0)
            except Exception as e:
                print(f"❌ Error: {str(e)}")
                print("Please try again.")
    
    def initialize_model(self, choice: str) -> None:
        """Initialize the selected model instance."""
        global IsolationForestFraudDetector, SequenceFraudDetector
        
        if choice == '1':
            # Lazy import for Isolation Forest
            if IsolationForestFraudDetector is None:
                print("📦 Loading Isolation Forest model...")
                from models.anomaly_detection import IsolationForestFraudDetector
            
            # Isolation Forest & Risk Score
            self.selected_model = "Isolation Forest & Risk Score"
            self.model_instance = IsolationForestFraudDetector(random_state=42)
            print(f"\n✅ Initialized {self.selected_model}")
            
        elif choice == '2':
            # Lazy import for Sequence Models
            if SequenceFraudDetector is None:
                print("📦 Loading Sequence Models...")
                from models.sequence_models import SequenceFraudDetector
            
            # Sequence Models (LSTM & GRU)
            self.selected_model = "Sequence Models (LSTM & GRU)"
            self.model_instance = SequenceFraudDetector(random_state=42)
            print(f"\n✅ Initialized {self.selected_model}")
            
        else:
            raise ValueError(f"Invalid model choice: {choice}")
    
    def run_model(self) -> None:
        """Run the selected model's main function."""
        if self.model_instance is None:
            raise ValueError("No model instance available. Please select a model first.")
        
        try:
            print(f"\n🚀 Starting {self.selected_model}...")
            print("="*60)
            
            # Call the model's main function
            if hasattr(self.model_instance, 'main'):
                self.model_instance.main()
            else:
                # Fallback to the main function from the module
                if self.selected_model == "Isolation Forest & Risk Score":
                    print("📦 Loading Isolation Forest main function...")
                    from models.anomaly_detection import main as anomaly_main
                    anomaly_main()
                elif self.selected_model == "Sequence Models (LSTM & GRU)":
                    print("📦 Loading Sequence Models main function...")
                    from models.sequence_models import main as sequence_main
                    sequence_main()
                    
        except Exception as e:
            logger.error(f"Error running {self.selected_model}: {str(e)}")
            print(f"\n❌ Error running {self.selected_model}: {str(e)}")
            print("Please check the logs for more details.")
            raise
    
    def run(self) -> None:
        """Main execution loop."""
        try:
            # Display welcome message
            self.display_welcome_message()
            
            while True:
                # Display model options
                self.display_model_options()
                
                # Get user choice
                choice = self.get_model_choice()
                
                # Handle the choice
                if choice == '1':
                    # Isolation Forest & Risk Score
                    self.initialize_model('1')
                    self.run_model()
                    break
                    
                elif choice == '2':
                    # Sequence Models (LSTM & GRU)
                    self.initialize_model('2')
                    self.run_model()
                    break
                    
                elif choice == '3':
                    # Model comparison
                    self.compare_models()
                    self._show_return_options()
                    continue
                    
                elif choice == '4':
                    # Help & Information
                    self.show_model_information()
                    self._show_return_options()
                    continue
                    
                elif choice == '5':
                    # Exit
                    print("\n👋 Thank you for using the Fraud Detection Platform!")
                    print("Goodbye!")
                    break
                    
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
        except Exception as e:
            logger.error(f"Unexpected error in main execution: {str(e)}")
            print(f"\n❌ Unexpected error: {str(e)}")
            print("Please check the logs for more details.")


def main():
    """
    Main function to run the fraud detection platform.
    """
    # Create and run the main controller
    controller = FraudDetectionMain()
    controller.run()


if __name__ == "__main__":
    main()
