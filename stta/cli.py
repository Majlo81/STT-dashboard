"""
Command-line interface using Typer.

Commands:
- ingest: Read CSV files and create clean Parquet
- compute: Compute metrics from clean data
- dashboard: Launch Streamlit dashboard
- export-report: Export PDF report for specific call
- oneclick: Run full pipeline (ingest + compute + dashboard)
"""

import typer
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from loguru import logger
import yaml
import pandas as pd

from . import __version__
from .utils.logging import setup_logging
from .io.reader import CSVReader, load_speaker_mapping
from .io.writer import write_parquet, read_parquet
from .schemas.calls import validate_calls_df
from .schemas.utterances import validate_utterances_df
from .metrics.timeline import TimelineCalculator
from .metrics.registry import register_core_metrics, get_global_registry

app = typer.Typer(
    name="stta",
    help="STT Analytics Platform - CLI",
    add_completion=False
)
console = Console()


def load_config(config_path: Path = None) -> dict:
    """Load configuration from YAML."""
    if config_path is None:
        config_path = Path("config/default.yml")
    
    if not config_path.exists():
        console.print(f"[red]Config file not found: {config_path}[/red]")
        raise typer.Exit(1)
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    return config


@app.command()
def ingest(
    input_dir: Path = typer.Option("data/raw", "--input", "-i", help="Input directory with CSV files"),
    output_dir: Path = typer.Option("data/clean", "--output", "-o", help="Output directory for Parquet files"),
    config_file: Optional[Path] = typer.Option(None, "--config", "-c", help="Config file path"),
):
    """
    Ingest CSV files and create clean Parquet data.
    """
    console.print(f"[bold blue]STT Analytics Platform v{__version__}[/bold blue]")
    console.print("[bold]Ingestion Pipeline[/bold]\n")
    
    # Setup logging
    log_path = Path("artifacts/run.log")
    setup_logging(log_file=log_path, level="INFO")
    
    # Load config
    config = load_config(config_file)
    
    # Load speaker mapping
    speaker_mapping = load_speaker_mapping(Path("config/speakers.yml"))
    
    # Create reader
    reader = CSVReader(
        encodings=config['parsing']['encodings_try'],
        delimiter=config['parsing']['delimiter'],
        speaker_mapping=speaker_mapping
    )
    
    # Find CSV files
    csv_files = list(input_dir.glob("*.csv"))
    
    if not csv_files:
        console.print(f"[yellow]No CSV files found in {input_dir}[/yellow]")
        return
    
    console.print(f"Found {len(csv_files)} CSV file(s)\n")
    
    # Process files
    all_calls = []
    all_utterances = []
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Processing files...", total=len(csv_files))
        
        for csv_file in csv_files:
            try:
                progress.update(task, description=f"Processing {csv_file.name}")
                
                calls_df, utterances_df = reader.read_csv_file(
                    csv_file,
                    config['parsing']
                )
                
                all_calls.append(calls_df)
                all_utterances.append(utterances_df)
                
                progress.advance(task)
                
            except Exception as e:
                logger.error(f"Failed to process {csv_file}: {e}")
                console.print(f"[red]✗ {csv_file.name}: {e}[/red]")
                continue
    
    # Combine DataFrames
    calls_combined = pd.concat(all_calls, ignore_index=True)
    utterances_combined = pd.concat(all_utterances, ignore_index=True)
    
    console.print(f"\n[green]✓[/green] Processed {len(calls_combined)} call(s)")
    console.print(f"[green]✓[/green] Extracted {len(utterances_combined)} utterance(s)")
    
    # Validate schemas
    console.print("\nValidating schemas...")
    try:
        calls_combined = validate_calls_df(calls_combined)
        utterances_combined = validate_utterances_df(utterances_combined)
        console.print("[green]✓[/green] Schema validation passed")
    except Exception as e:
        console.print(f"[red]✗ Schema validation failed: {e}[/red]")
        logger.error(f"Schema validation error: {e}")
        raise typer.Exit(1)
    
    # Write Parquet
    output_dir.mkdir(parents=True, exist_ok=True)
    
    console.print("\nWriting Parquet files...")
    write_parquet(calls_combined, output_dir / "calls.parquet")
    write_parquet(utterances_combined, output_dir / "utterances.parquet")
    
    console.print("[green]✓[/green] Parquet files written")
    console.print(f"\n[bold green]Ingestion complete![/bold green]")
    console.print(f"Output: {output_dir}")


@app.command()
def compute(
    data_dir: Path = typer.Option("data/clean", "--data", "-d", help="Directory with clean Parquet files"),
):
    """
    Compute metrics from clean data.
    """
    console.print(f"[bold blue]STT Analytics Platform v{__version__}[/bold blue]")
    console.print("[bold]Metrics Computation[/bold]\n")
    
    # Setup logging
    log_path = Path("artifacts/run.log")
    setup_logging(log_file=log_path, level="INFO")
    
    # Register metrics
    register_core_metrics()
    registry = get_global_registry()
    
    # Read data
    console.print("Loading data...")
    calls_df = read_parquet(data_dir / "calls.parquet")
    utterances_df = read_parquet(data_dir / "utterances.parquet")
    
    console.print(f"[green]✓[/green] Loaded {len(calls_df)} calls")
    console.print(f"[green]✓[/green] Loaded {len(utterances_df)} utterances\n")
    
    # Compute metrics per call
    call_metrics_list = []
    speaker_metrics_list = []
    quality_metrics_list = []
    text_stats_list = []
    filler_words_list = []
    interaction_metrics_list = []
    
    calc = TimelineCalculator()
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Computing metrics...", total=len(calls_df))
        
        for _, call_row in calls_df.iterrows():
            call_id = call_row['call_id']
            progress.update(task, description=f"Computing metrics for {call_id}")
            
            # Get utterances for this call
            call_utts = utterances_df[utterances_df['call_id'] == call_id]
            
            # Compute timeline
            timeline_stats = calc.compute_timeline_stats(call_utts)
            
            # Compute core metrics
            call_metrics = registry.compute(
                'call_metrics',
                call_id=call_id,
                utterances_df=call_utts,
                timeline_stats=timeline_stats
            )
            call_metrics_list.append(call_metrics)
            
            speaker_metrics = registry.compute(
                'speaker_metrics',
                call_id=call_id,
                utterances_df=call_utts,
                timeline_stats=timeline_stats
            )
            speaker_metrics_list.extend(speaker_metrics)
            
            quality_metrics = registry.compute(
                'quality_metrics',
                call_id=call_id,
                utterances_df=call_utts,
                call_duration_meta=call_row.get('call_duration_meta'),
                timeline_stats=timeline_stats
            )
            quality_metrics_list.append(quality_metrics)
            
            # Compute new advanced metrics
            text_stats = registry.compute(
                'text_statistics',
                utterances_df=call_utts,
                call_id=call_id
            )
            text_stats_list.append(text_stats)
            
            filler_words = registry.compute(
                'filler_words',
                utterances_df=call_utts,
                call_id=call_id
            )
            filler_words_list.append(filler_words)
            
            interaction_metrics = registry.compute(
                'interaction_metrics',
                utterances_df=call_utts,
                call_id=call_id
            )
            interaction_metrics_list.append(interaction_metrics)
            
            progress.advance(task)
    
    # Create DataFrames
    call_metrics_df = pd.DataFrame(call_metrics_list)
    speaker_metrics_df = pd.DataFrame(speaker_metrics_list)
    quality_metrics_df = pd.DataFrame(quality_metrics_list)
    text_stats_df = pd.DataFrame(text_stats_list)
    filler_words_df = pd.DataFrame(filler_words_list)
    interaction_metrics_df = pd.DataFrame(interaction_metrics_list)
    
    console.print(f"\n[green]✓[/green] Computed call metrics: {len(call_metrics_df)} records")
    console.print(f"[green]✓[/green] Computed speaker metrics: {len(speaker_metrics_df)} records")
    console.print(f"[green]✓[/green] Computed quality metrics: {len(quality_metrics_df)} records")
    console.print(f"[green]✓[/green] Computed text statistics: {len(text_stats_df)} records")
    console.print(f"[green]✓[/green] Computed filler words: {len(filler_words_df)} records")
    console.print(f"[green]✓[/green] Computed interaction metrics: {len(interaction_metrics_df)} records")
    
    # Write metrics
    console.print("\nWriting metrics...")
    write_parquet(call_metrics_df, data_dir / "call_metrics.parquet")
    write_parquet(speaker_metrics_df, data_dir / "speaker_metrics.parquet")
    write_parquet(quality_metrics_df, data_dir / "quality_metrics.parquet")
    write_parquet(text_stats_df, data_dir / "text_statistics.parquet")
    write_parquet(filler_words_df, data_dir / "filler_words.parquet")
    write_parquet(interaction_metrics_df, data_dir / "interaction_metrics.parquet")
    
    console.print("[green]✓[/green] Metrics written")
    console.print(f"\n[bold green]Computation complete![/bold green]")


@app.command()
def dashboard(
    data_dir: Path = typer.Option("data/clean", "--data", "-d", help="Directory with Parquet files"),
    port: int = typer.Option(8501, "--port", "-p", help="Streamlit port"),
):
    """
    Launch Streamlit dashboard.
    """
    import subprocess
    
    console.print(f"[bold blue]Launching Dashboard...[/bold blue]\n")
    console.print(f"Data directory: {data_dir}")
    console.print(f"Port: {port}\n")
    
    # Launch Streamlit
    cmd = [
        "streamlit", "run",
        "stta/dashboard/app.py",
        "--",
        "--data", str(data_dir),
        "--server.port", str(port)
    ]
    
    subprocess.run(cmd)


@app.command()
def version():
    """Show version information."""
    console.print(f"[bold]STT Analytics Platform[/bold]")
    console.print(f"Version: {__version__}")


if __name__ == "__main__":
    app()
