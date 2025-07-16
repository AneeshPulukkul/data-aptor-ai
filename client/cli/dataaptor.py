import os
import click
import requests
from tabulate import tabulate
import json
from pathlib import Path
import sys

# Add the root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Configuration
API_URL = os.environ.get("DATAAPTOR_API_URL", "http://localhost:8000")
CONFIG_DIR = Path.home() / ".dataaptor"
CONFIG_FILE = CONFIG_DIR / "config.json"

# Ensure config directory exists
CONFIG_DIR.mkdir(parents=True, exist_ok=True)

# Load configuration
def load_config():
    """Load configuration from file"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {
        "api_url": API_URL,
        "output_format": "table",
        "verbose": False
    }

# Save configuration
def save_config(config):
    """Save configuration to file"""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

# Configuration context
class ConfigContext:
    """Configuration context for the CLI"""
    def __init__(self):
        self.config = load_config()
    
    def get(self, key, default=None):
        """Get configuration value"""
        return self.config.get(key, default)
    
    def set(self, key, value):
        """Set configuration value"""
        self.config[key] = value
        save_config(self.config)

# Pass configuration to commands
pass_config = click.make_pass_decorator(ConfigContext, ensure=True)

# CLI group
@click.group()
@click.option('--api-url', help='API URL for DataAptor AI services')
@click.option('--verbose/--no-verbose', default=False, help='Enable verbose output')
@click.option('--output', type=click.Choice(['table', 'json', 'csv']), help='Output format')
@pass_config
def cli(config, api_url, verbose, output):
    """DataAptor AI CLI - A tool for assessing AI readiness of datasets"""
    if api_url:
        config.set('api_url', api_url)
    if verbose is not None:
        config.set('verbose', verbose)
    if output:
        config.set('output_format', output)

# Upload command
@cli.command()
@click.argument('file_path', type=click.Path(exists=True))
@pass_config
def upload(config, file_path):
    """Upload a dataset file for assessment"""
    click.echo(f"Uploading {file_path}...")
    
    # Get the API URL
    api_url = config.get('api_url')
    
    try:
        # Open the file and prepare for upload
        with open(file_path, 'rb') as f:
            file_name = os.path.basename(file_path)
            files = {'file': (file_name, f)}
            
            # Upload the file
            response = requests.post(f"{api_url}/api/ingestion/upload", files=files)
            
            # Check if the upload was successful
            if response.status_code == 200:
                dataset = response.json()
                dataset_id = dataset['id']
                
                if config.get('output_format') == 'json':
                    click.echo(json.dumps(dataset, indent=2))
                else:
                    click.echo(f"Upload successful! Dataset ID: {dataset_id}")
                    click.echo("\nDataset Details:")
                    
                    # Format metadata for display
                    metadata_str = json.dumps(dataset['metadata'], indent=2)
                    if len(metadata_str) > 500 and not config.get('verbose'):
                        metadata_str = metadata_str[:500] + "... (use --verbose to see all)"
                    
                    # Create a table with dataset details
                    table = [
                        ["ID", dataset_id],
                        ["Name", dataset['name']],
                        ["Type", dataset['file_type']],
                        ["Size", f"{dataset['file_size'] / 1024:.2f} KB"],
                        ["Created", dataset['created_at']],
                        ["Metadata", metadata_str]
                    ]
                    
                    click.echo(tabulate(table, tablefmt="fancy_grid"))
                    
                    # Prompt for next steps
                    click.echo("\nNext Steps:")
                    click.echo(f"- Run 'dataaptor assess {dataset_id}' to assess this dataset")
                    click.echo(f"- Run 'dataaptor list' to see all uploaded datasets")
            else:
                click.echo(f"Error: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        click.echo(f"Error connecting to API: {str(e)}")
    except Exception as e:
        click.echo(f"Error: {str(e)}")

# Assess command
@cli.command()
@click.argument('dataset_id', type=int)
@click.option('--modules', '-m', help='Comma-separated list of assessment modules to run (e.g., quality,accessibility,governance)')
@click.option('--wait/--no-wait', default=True, help='Wait for assessment completion')
@pass_config
def assess(config, dataset_id, modules, wait):
    """Trigger assessment for a dataset"""
    click.echo(f"Triggering assessment for dataset {dataset_id}...")
    
    # Get the API URL
    api_url = config.get('api_url')
    
    try:
        # Prepare request data
        data = {'dataset_id': dataset_id}
        if modules:
            data['modules'] = [m.strip() for m in modules.split(',')]
        
        # Trigger assessment
        response = requests.post(f"{api_url}/api/assessment/trigger", json=data)
        
        # Check if the request was successful
        if response.status_code == 200:
            result = response.json()
            assessment_id = result['assessment_id']
            
            click.echo(f"Assessment triggered successfully. Assessment ID: {assessment_id}")
            
            if wait:
                click.echo("Waiting for assessment to complete...")
                
                # Poll for assessment completion
                completed = False
                while not completed:
                    # Check assessment status
                    status_response = requests.get(f"{api_url}/api/assessment/{assessment_id}/status")
                    
                    if status_response.status_code == 200:
                        status = status_response.json()
                        
                        if status['status'] == 'completed':
                            completed = True
                            click.echo("Assessment completed!")
                            
                            # Display assessment summary
                            click.echo("\nAssessment Summary:")
                            summary = [
                                ["Overall Score", f"{status['overall_score']:.2f}/10.0"],
                                ["Started", status['started_at']],
                                ["Completed", status['completed_at']],
                                ["Duration", f"{status['duration_seconds']:.2f} seconds"]
                            ]
                            click.echo(tabulate(summary, tablefmt="fancy_grid"))
                            
                            click.echo("\nModule Scores:")
                            module_scores = [[m['name'], f"{m['score']:.2f}/10.0"] for m in status['module_scores']]
                            click.echo(tabulate(module_scores, headers=["Module", "Score"], tablefmt="fancy_grid"))
                            
                            # Suggest next steps
                            click.echo("\nNext Steps:")
                            click.echo(f"- Run 'dataaptor report {assessment_id}' to view the full assessment report")
                            click.echo(f"- Run 'dataaptor export {assessment_id}' to export the assessment report")
                        elif status['status'] == 'failed':
                            completed = True
                            click.echo(f"Assessment failed: {status.get('error', 'Unknown error')}")
                        else:
                            # Assessment still in progress
                            progress = status.get('progress', {})
                            progress_pct = progress.get('percentage', 0)
                            current_module = progress.get('current_module', 'Unknown')
                            
                            click.echo(f"\rProgress: {progress_pct:.1f}% (Current module: {current_module})", nl=False)
                            
                            # Wait before checking again
                            import time
                            time.sleep(2)
                    else:
                        click.echo(f"\nError checking status: {status_response.status_code} - {status_response.text}")
                        break
            else:
                click.echo(f"\nUse 'dataaptor status {assessment_id}' to check assessment status")
        else:
            click.echo(f"Error: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        click.echo(f"Error connecting to API: {str(e)}")
    except Exception as e:
        click.echo(f"Error: {str(e)}")

# Check assessment status command
@cli.command()
@click.argument('assessment_id', type=int)
@pass_config
def status(config, assessment_id):
    """Check the status of an assessment"""
    click.echo(f"Checking status for assessment {assessment_id}...")
    
    # Get the API URL
    api_url = config.get('api_url')
    
    try:
        # Check assessment status
        response = requests.get(f"{api_url}/api/assessment/{assessment_id}/status")
        
        # Check if the request was successful
        if response.status_code == 200:
            status = response.json()
            
            if config.get('output_format') == 'json':
                click.echo(json.dumps(status, indent=2))
            else:
                # Display status
                status_str = status['status'].upper()
                
                # Color the status
                from colorama import Fore, Style
                if status['status'] == 'completed':
                    status_str = f"{Fore.GREEN}{status_str}{Style.RESET_ALL}"
                elif status['status'] == 'failed':
                    status_str = f"{Fore.RED}{status_str}{Style.RESET_ALL}"
                elif status['status'] == 'in_progress':
                    status_str = f"{Fore.YELLOW}{status_str}{Style.RESET_ALL}"
                
                # Display assessment summary
                click.echo("\nAssessment Summary:")
                summary = [
                    ["ID", assessment_id],
                    ["Status", status_str],
                    ["Dataset ID", status['dataset_id']]
                ]
                
                # Add timing information if available
                if 'started_at' in status:
                    summary.append(["Started", status['started_at']])
                if 'completed_at' in status and status['status'] == 'completed':
                    summary.append(["Completed", status['completed_at']])
                    summary.append(["Duration", f"{status['duration_seconds']:.2f} seconds"])
                
                # Add overall score if completed
                if status['status'] == 'completed' and 'overall_score' in status:
                    summary.append(["Overall Score", f"{status['overall_score']:.2f}/10.0"])
                
                click.echo(tabulate(summary, tablefmt="fancy_grid"))
                
                # Show progress if in progress
                if status['status'] == 'in_progress' and 'progress' in status:
                    progress = status['progress']
                    click.echo("\nProgress:")
                    progress_table = [
                        ["Percentage", f"{progress.get('percentage', 0):.1f}%"],
                        ["Current Module", progress.get('current_module', 'Unknown')],
                        ["Modules Completed", progress.get('modules_completed', 0)],
                        ["Total Modules", progress.get('total_modules', 0)]
                    ]
                    click.echo(tabulate(progress_table, tablefmt="fancy_grid"))
                
                # Show module scores if completed
                if status['status'] == 'completed' and 'module_scores' in status:
                    click.echo("\nModule Scores:")
                    module_scores = [[m['name'], f"{m['score']:.2f}/10.0"] for m in status['module_scores']]
                    click.echo(tabulate(module_scores, headers=["Module", "Score"], tablefmt="fancy_grid"))
                
                # Show error if failed
                if status['status'] == 'failed' and 'error' in status:
                    click.echo(f"\nError: {status['error']}")
        else:
            click.echo(f"Error: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        click.echo(f"Error connecting to API: {str(e)}")
    except Exception as e:
        click.echo(f"Error: {str(e)}")

# Get assessment report command
@cli.command()
@click.argument('assessment_id', type=int)
@pass_config
def report(config, assessment_id):
    """View the detailed assessment report"""
    click.echo(f"Retrieving report for assessment {assessment_id}...")
    
    # Get the API URL
    api_url = config.get('api_url')
    
    try:
        # Get the assessment report
        response = requests.get(f"{api_url}/api/assessment/{assessment_id}/report")
        
        # Check if the request was successful
        if response.status_code == 200:
            report = response.json()
            
            if config.get('output_format') == 'json':
                click.echo(json.dumps(report, indent=2))
            else:
                # Display report summary
                click.echo("\nAssessment Report Summary:")
                summary = [
                    ["Assessment ID", assessment_id],
                    ["Dataset", report['dataset_name']],
                    ["Dataset ID", report['dataset_id']],
                    ["Overall Score", f"{report['overall_score']:.2f}/10.0"],
                    ["Date", report['created_at']]
                ]
                click.echo(tabulate(summary, tablefmt="fancy_grid"))
                
                # Display module scores
                click.echo("\nModule Scores:")
                module_scores = [[m['name'], f"{m['score']:.2f}/10.0"] for m in report['module_scores']]
                click.echo(tabulate(module_scores, headers=["Module", "Score"], tablefmt="fancy_grid"))
                
                # Display findings
                if 'findings' in report and report['findings']:
                    click.echo("\nKey Findings:")
                    for finding in report['findings']:
                        click.echo(f"- {finding}")
                
                # Display recommendations
                if 'recommendations' in report and report['recommendations']:
                    click.echo("\nRecommendations:")
                    for recommendation in report['recommendations']:
                        click.echo(f"- {recommendation}")
                
                # Suggest export
                click.echo("\nTo export this report, run:")
                click.echo(f"dataaptor export {assessment_id} --format [pdf|html|json|csv]")
        else:
            click.echo(f"Error: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        click.echo(f"Error connecting to API: {str(e)}")
    except Exception as e:
        click.echo(f"Error: {str(e)}")

# Export assessment report command
@cli.command()
@click.argument('assessment_id', type=int)
@click.option('--format', '-f', type=click.Choice(['pdf', 'html', 'json', 'csv']), default='pdf', help='Export format')
@click.option('--output', '-o', help='Output file path (defaults to ./report_<assessment_id>.<format>)')
@pass_config
def export(config, assessment_id, format, output):
    """Export the assessment report to a file"""
    # Default output path if not specified
    if not output:
        output = f"./report_{assessment_id}.{format}"
    
    click.echo(f"Exporting report for assessment {assessment_id} to {output}...")
    
    # Get the API URL
    api_url = config.get('api_url')
    
    try:
        # Request the report export
        response = requests.get(f"{api_url}/api/assessment/{assessment_id}/export?format={format}")
        
        # Check if the request was successful
        if response.status_code == 200:
            # Write the report to the output file
            with open(output, 'wb') as f:
                f.write(response.content)
            
            click.echo(f"Report exported successfully to {output}")
        else:
            click.echo(f"Error: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        click.echo(f"Error connecting to API: {str(e)}")
    except Exception as e:
        click.echo(f"Error: {str(e)}")

# List assessments command
@cli.command()
@click.option('--dataset-id', type=int, help='Filter by dataset ID')
@click.option('--page', default=1, help='Page number')
@click.option('--limit', default=10, help='Number of items per page')
@pass_config
def assessments(config, dataset_id, page, limit):
    """List all assessments"""
    click.echo("Listing assessments...")
    
    # Get the API URL
    api_url = config.get('api_url')
    
    try:
        # Calculate skip value for pagination
        skip = (page - 1) * limit
        
        # Build URL with query parameters
        url = f"{api_url}/api/assessment/list?skip={skip}&limit={limit}"
        if dataset_id:
            url += f"&dataset_id={dataset_id}"
        
        # Get the list of assessments
        response = requests.get(url)
        
        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()
            assessments = data['assessments']
            total = data['total']
            
            if config.get('output_format') == 'json':
                click.echo(json.dumps(data, indent=2))
            elif config.get('output_format') == 'csv':
                # Output as CSV
                headers = ["ID", "Dataset ID", "Status", "Overall Score", "Created"]
                rows = [
                    [a['id'], a['dataset_id'], a['status'], 
                     f"{a.get('overall_score', 'N/A') if a.get('overall_score') is not None else 'N/A'}", 
                     a['created_at']] 
                    for a in assessments
                ]
                click.echo(','.join(headers))
                for row in rows:
                    click.echo(','.join([str(cell) for cell in row]))
            else:
                # Output as table
                if assessments:
                    from colorama import Fore, Style
                    
                    headers = ["ID", "Dataset ID", "Status", "Overall Score", "Created"]
                    rows = []
                    
                    for a in assessments:
                        # Color the status
                        status = a['status'].upper()
                        if a['status'] == 'completed':
                            status = f"{Fore.GREEN}{status}{Style.RESET_ALL}"
                        elif a['status'] == 'failed':
                            status = f"{Fore.RED}{status}{Style.RESET_ALL}"
                        elif a['status'] == 'in_progress':
                            status = f"{Fore.YELLOW}{status}{Style.RESET_ALL}"
                        
                        # Format score
                        score = a.get('overall_score')
                        score_str = f"{score:.2f}/10.0" if score is not None else "N/A"
                        
                        rows.append([a['id'], a['dataset_id'], status, score_str, a['created_at']])
                    
                    click.echo(tabulate(rows, headers=headers, tablefmt="fancy_grid"))
                    
                    # Show pagination info
                    click.echo(f"\nShowing {len(assessments)} of {total} assessments (Page {page})")
                    
                    if total > skip + limit:
                        click.echo(f"Use --page {page + 1} to see the next page")
                else:
                    click.echo("No assessments found.")
        else:
            click.echo(f"Error: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        click.echo(f"Error connecting to API: {str(e)}")
    except Exception as e:
        click.echo(f"Error: {str(e)}")

# List command
@cli.command()
@click.option('--page', default=1, help='Page number')
@click.option('--limit', default=10, help='Number of items per page')
@pass_config
def list(config, page, limit):
    """List all uploaded datasets"""
    click.echo("Listing datasets...")
    
    # Get the API URL
    api_url = config.get('api_url')
    
    try:
        # Calculate skip value for pagination
        skip = (page - 1) * limit
        
        # Get the list of datasets
        response = requests.get(f"{api_url}/api/ingestion/datasets?skip={skip}&limit={limit}")
        
        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()
            datasets = data['datasets']
            total = data['total']
            
            if config.get('output_format') == 'json':
                click.echo(json.dumps(data, indent=2))
            elif config.get('output_format') == 'csv':
                # Output as CSV
                headers = ["ID", "Name", "Type", "Size (KB)", "Created"]
                rows = [[d['id'], d['name'], d['file_type'], f"{d['file_size'] / 1024:.2f}", d['created_at']] for d in datasets]
                click.echo(','.join(headers))
                for row in rows:
                    click.echo(','.join([str(cell) for cell in row]))
            else:
                # Output as table
                if datasets:
                    headers = ["ID", "Name", "Type", "Size (KB)", "Created"]
                    rows = [[d['id'], d['name'], d['file_type'], f"{d['file_size'] / 1024:.2f}", d['created_at']] for d in datasets]
                    click.echo(tabulate(rows, headers=headers, tablefmt="fancy_grid"))
                    
                    # Show pagination info
                    click.echo(f"\nShowing {len(datasets)} of {total} datasets (Page {page})")
                    
                    if total > skip + limit:
                        click.echo(f"Use --page {page + 1} to see the next page")
                else:
                    click.echo("No datasets found.")
        else:
            click.echo(f"Error: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        click.echo(f"Error connecting to API: {str(e)}")
    except Exception as e:
        click.echo(f"Error: {str(e)}")

# Get dataset details command
@cli.command()
@click.argument('dataset_id', type=int)
@pass_config
def info(config, dataset_id):
    """Get details of a specific dataset"""
    click.echo(f"Getting details for dataset {dataset_id}...")
    
    # Get the API URL
    api_url = config.get('api_url')
    
    try:
        # Get the dataset details
        response = requests.get(f"{api_url}/api/ingestion/datasets/{dataset_id}")
        
        # Check if the request was successful
        if response.status_code == 200:
            dataset = response.json()
            
            if config.get('output_format') == 'json':
                click.echo(json.dumps(dataset, indent=2))
            else:
                # Format metadata for display
                metadata_str = json.dumps(dataset['metadata'], indent=2)
                if len(metadata_str) > 500 and not config.get('verbose'):
                    metadata_str = metadata_str[:500] + "... (use --verbose to see all)"
                
                # Create a table with dataset details
                table = [
                    ["ID", dataset_id],
                    ["Name", dataset['name']],
                    ["Type", dataset['file_type']],
                    ["Size", f"{dataset['file_size'] / 1024:.2f} KB"],
                    ["Created", dataset['created_at']],
                    ["Metadata", metadata_str]
                ]
                
                click.echo(tabulate(table, tablefmt="fancy_grid"))
        else:
            click.echo(f"Error: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        click.echo(f"Error connecting to API: {str(e)}")
    except Exception as e:
        click.echo(f"Error: {str(e)}")

# Delete dataset command
@cli.command()
@click.argument('dataset_id', type=int)
@click.option('--force/--no-force', default=False, help='Force deletion without confirmation')
@pass_config
def delete(config, dataset_id, force):
    """Delete a dataset"""
    # Get the API URL
    api_url = config.get('api_url')
    
    # Confirm deletion
    if not force and not click.confirm(f"Are you sure you want to delete dataset {dataset_id}?"):
        click.echo("Deletion cancelled.")
        return
    
    click.echo(f"Deleting dataset {dataset_id}...")
    
    try:
        # Delete the dataset
        response = requests.delete(f"{api_url}/api/ingestion/datasets/{dataset_id}")
        
        # Check if the request was successful
        if response.status_code == 200:
            click.echo("Dataset deleted successfully.")
        else:
            click.echo(f"Error: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        click.echo(f"Error connecting to API: {str(e)}")
    except Exception as e:
        click.echo(f"Error: {str(e)}")

# Config command
@cli.command()
@click.option('--get', help='Get configuration value')
@click.option('--set', 'set_key', help='Set configuration key')
@click.option('--value', help='Value to set')
@click.option('--list/--no-list', 'list_config', default=False, help='List all configuration values')
@pass_config
def config(config, get, set_key, value, list_config):
    """View or modify configuration"""
    if get:
        # Get configuration value
        click.echo(f"{get}: {config.get(get, 'Not set')}")
    elif set_key and value:
        # Set configuration value
        config.set(set_key, value)
        click.echo(f"Set {set_key} to {value}")
    elif list_config:
        # List all configuration values
        for key, value in config.config.items():
            click.echo(f"{key}: {value}")
    else:
        # Show help if no options provided
        ctx = click.get_current_context()
        click.echo(ctx.get_help())

if __name__ == '__main__':
    cli()
