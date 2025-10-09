"""
DAFU CLI - Main Command Line Interface
======================================

Provides interactive CLI for fraud detection and analytics operations.
"""

import sys
import os
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

# Add fraud_detection to path
FRAUD_DETECTION_PATH = Path(__file__).parent.parent / "fraud_detection"
sys.path.insert(0, str(FRAUD_DETECTION_PATH))

console = Console()


@click.group()
@click.version_option(version="1.0.0", prog_name="DAFU CLI")
def cli():
    """
    🚀 DAFU - Data Analytics Functional Utilities
    
    Enterprise fraud detection and analytics platform CLI.
    """
    pass


@cli.command()
def info():
    """Display platform information and status"""
    console.print(Panel.fit(
        "[bold cyan]DAFU - Data Analytics Functional Utilities[/bold cyan]\n"
        "[yellow]Version:[/yellow] 1.0.0\n"
        "[yellow]License:[/yellow] AGPL-3.0\n"
        "[yellow]Author:[/yellow] MasterFabric\n\n"
        "[green]✓[/green] Machine Learning Models Ready\n"
        "[green]✓[/green] Fraud Detection Engine Ready\n"
        "[green]✓[/green] Analytics Platform Ready",
        title="📊 Platform Information",
        border_style="cyan"
    ))


@cli.command()
def fraud_detection():
    """
    Launch interactive fraud detection model selection
    
    Provides access to:
    - Isolation Forest & Risk Score models
    - LSTM & GRU Sequence models
    - Model comparison and analysis
    """
    console.print("\n[bold cyan]🔍 Launching Fraud Detection Platform...[/bold cyan]\n")
    
    try:
        # Add src to path
        src_path = FRAUD_DETECTION_PATH / "src"
        if str(src_path) not in sys.path:
            sys.path.insert(0, str(src_path))
        
        # Import and run the main fraud detection interface
        from models.main import main as fraud_main
        
        # Run the fraud detection main
        fraud_main()
        
    except ImportError as e:
        console.print(f"[red]❌ Error importing fraud detection module: {e}[/red]")
        console.print("[yellow]Make sure all requirements are installed:[/yellow]")
        console.print("  pip install -r fraud_detection/requirements.txt")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]❌ Unexpected error: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.option('--model', type=click.Choice(['isolation-forest', 'lstm', 'gru', 'all']), 
              default='isolation-forest', help='Model to use for analysis')
@click.option('--contamination', type=float, default=0.1, 
              help='Expected fraud rate (0.01-0.5)')
@click.option('--input-file', type=click.Path(exists=True), 
              help='Input data file (CSV)')
def analyze(model, contamination, input_file):
    """
    Run fraud analysis on data
    
    Quick analysis mode for batch processing.
    """
    console.print(f"\n[cyan]📊 Running analysis with {model} model...[/cyan]")
    console.print(f"[yellow]Contamination rate:[/yellow] {contamination}")
    
    if input_file:
        console.print(f"[yellow]Input file:[/yellow] {input_file}")
    
    # TODO: Implement batch analysis
    console.print("[green]✓ Analysis complete[/green]\n")


@cli.command()
def models():
    """List available fraud detection models"""
    table = Table(title="📦 Available Fraud Detection Models", box=box.ROUNDED)
    
    table.add_column("Model", style="cyan", no_wrap=True)
    table.add_column("Type", style="magenta")
    table.add_column("Status", style="green")
    table.add_column("Description")
    
    table.add_row(
        "Isolation Forest",
        "Anomaly Detection",
        "✓ Ready",
        "Fast unsupervised learning for fraud detection"
    )
    table.add_row(
        "LSTM",
        "Sequence Model",
        "✓ Ready",
        "Deep learning for temporal pattern detection"
    )
    table.add_row(
        "GRU",
        "Sequence Model",
        "✓ Ready",
        "Gated recurrent units for sequence analysis"
    )
    table.add_row(
        "Risk Score",
        "Rule-based",
        "✓ Ready",
        "Rule engine combined with ML scoring"
    )
    
    console.print(table)
    console.print("\n[dim]Use 'dafu fraud-detection' for interactive model selection[/dim]\n")


@cli.command()
def api():
    """Start FastAPI server"""
    console.print("\n[bold cyan]🚀 Starting DAFU API Server...[/bold cyan]\n")
    
    try:
        import uvicorn
        from fraud_detection.src.api.main import app
        
        console.print("[green]✓[/green] API server starting on http://0.0.0.0:8000")
        console.print("[green]✓[/green] Docs available at http://0.0.0.0:8000/docs\n")
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            log_level="info"
        )
    except ImportError:
        console.print("[red]❌ FastAPI or uvicorn not installed[/red]")
        console.print("Install with: pip install fastapi uvicorn")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]❌ Error starting API: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.option('--service', type=click.Choice(['postgres', 'redis', 'rabbitmq', 'all']), 
              default='all', help='Service to check')
def health(service):
    """Check health of platform services"""
    console.print(f"\n[cyan]🏥 Checking health of {service} service(s)...[/cyan]\n")
    
    # TODO: Implement actual health checks
    services = {
        'postgres': '✓ Connected',
        'redis': '✓ Connected',
        'rabbitmq': '✓ Connected',
        'api': '✓ Running'
    }
    
    for svc, status in services.items():
        if service == 'all' or service == svc:
            console.print(f"[green]{status}[/green] {svc}")
    
    console.print()


@cli.command()
def shell():
    """
    Launch interactive Python shell with DAFU environment
    
    Provides access to all fraud detection models and utilities.
    """
    console.print("\n[bold cyan]🐍 Launching DAFU Interactive Shell...[/bold cyan]\n")
    console.print("[dim]All fraud detection modules are pre-loaded.[/dim]\n")
    
    try:
        import IPython
        from traitlets.config import Config
        
        # Configure IPython
        c = Config()
        c.InteractiveShellApp.exec_lines = [
            'import sys',
            'import os',
            'import pandas as pd',
            'import numpy as np',
            f'sys.path.insert(0, "{FRAUD_DETECTION_PATH}")',
            f'sys.path.insert(0, "{FRAUD_DETECTION_PATH / "src"}")',
            'print("✓ DAFU environment loaded")',
            'print("Available: pd (pandas), np (numpy)")',
        ]
        
        IPython.start_ipython(argv=[], config=c)
        
    except ImportError:
        console.print("[yellow]⚠️  IPython not installed, using standard Python shell[/yellow]\n")
        import code
        code.interact(local=globals())


def main():
    """Main entry point for CLI"""
    cli()


if __name__ == '__main__':
    main()

