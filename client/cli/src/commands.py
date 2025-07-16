"""
DataAptor AI CLI - Commands module

This module provides command implementations for the DataAptor AI CLI.
"""

import os
import click
import time
from pathlib import Path
from tabulate import tabulate
from colorama import Fore, Style

from .api_client import DataAptorClient
from .utils import (
    format_table, format_json, format_csv, format_metadata,
    format_status, format_score, show_pagination_info
)


class DataAptorCommands:
    """Command implementations for the DataAptor AI CLI"""
    
    def __init__(self, config):
        """Initialize with configuration"""
        self.config = config
        self.api_client = DataAptorClient(config.get('api_url'))
    
    def upload_dataset(self, file_path):
        """Upload a dataset file"""
        try:
            dataset = self.api_client.upload_dataset(file_path)
            dataset_id = dataset['id']
            
            if self.config.get('output_format') == 'json':
                click.echo(format_json(dataset))
            else:
                click.echo(f"Upload successful! Dataset ID: {dataset_id}")
                click.echo("\nDataset Details:")
                
                # Format metadata for display
                metadata_str = format_metadata(
                    dataset['metadata'], 
                    max_length=500, 
                    verbose=self.config.get('verbose')
                )
                
                # Create a table with dataset details
                table = [
                    ["ID", dataset_id],
                    ["Name", dataset['name']],
                    ["Type", dataset['file_type']],
                    ["Size", f"{dataset['file_size'] / 1024:.2f} KB"],
                    ["Created", dataset['created_at']],
                    ["Metadata", metadata_str]
                ]
                
                click.echo(format_table(table))
                
                # Prompt for next steps
                click.echo("\nNext Steps:")
                click.echo(f"- Run 'dataaptor assess {dataset_id}' to assess this dataset")
                click.echo(f"- Run 'dataaptor list' to see all uploaded datasets")
                
            return dataset_id
        except Exception as e:
            click.echo(f"Error uploading dataset: {str(e)}")
            return None
    
    def list_datasets(self, page, limit):
        """List all uploaded datasets"""
        try:
            skip = (page - 1) * limit
            data = self.api_client.list_datasets(skip, limit)
            datasets = data['datasets']
            total = data['total']
            
            if self.config.get('output_format') == 'json':
                click.echo(format_json(data))
            elif self.config.get('output_format') == 'csv':
                headers = ["ID", "Name", "Type", "Size (KB)", "Created"]
                rows = [
                    [d['id'], d['name'], d['file_type'], f"{d['file_size'] / 1024:.2f}", d['created_at']]
                    for d in datasets
                ]
                click.echo(format_csv(rows, headers))
            else:
                if datasets:
                    headers = ["ID", "Name", "Type", "Size (KB)", "Created"]
                    rows = [
                        [d['id'], d['name'], d['file_type'], f"{d['file_size'] / 1024:.2f}", d['created_at']]
                        for d in datasets
                    ]
                    click.echo(format_table(rows, headers))
                    
                    show_pagination_info(datasets, total, page, limit, "dataaptor list")
                else:
                    click.echo("No datasets found.")
        except Exception as e:
            click.echo(f"Error listing datasets: {str(e)}")
    
    def trigger_assessment(self, dataset_id, modules=None, wait=True):
        """Trigger an assessment for a dataset"""
        try:
            # Convert modules string to list if provided
            modules_list = None
            if modules:
                modules_list = [m.strip() for m in modules.split(',')]
            
            # Trigger the assessment
            result = self.api_client.trigger_assessment(dataset_id, modules_list)
            assessment_id = result['assessment_id']
            
            click.echo(f"Assessment triggered successfully. Assessment ID: {assessment_id}")
            
            if wait:
                self._wait_for_assessment(assessment_id)
            else:
                click.echo(f"\nUse 'dataaptor status {assessment_id}' to check assessment status")
                
            return assessment_id
        except Exception as e:
            click.echo(f"Error triggering assessment: {str(e)}")
            return None
    
    def _wait_for_assessment(self, assessment_id):
        """Wait for an assessment to complete"""
        click.echo("Waiting for assessment to complete...")
        
        completed = False
        while not completed:
            try:
                # Check assessment status
                status = self.api_client.get_assessment_status(assessment_id)
                
                if status['status'] == 'completed':
                    completed = True
                    click.echo("Assessment completed!")
                    
                    # Display assessment summary
                    click.echo("\nAssessment Summary:")
                    summary = [
                        ["Overall Score", format_score(status['overall_score'])],
                        ["Started", status['started_at']],
                        ["Completed", status['completed_at']],
                        ["Duration", f"{status['duration_seconds']:.2f} seconds"]
                    ]
                    click.echo(format_table(summary))
                    
                    click.echo("\nModule Scores:")
                    module_scores = [
                        [m['name'], format_score(m['score'])]
                        for m in status['module_scores']
                    ]
                    click.echo(format_table(module_scores, ["Module", "Score"]))
                    
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
                    time.sleep(2)
            except Exception as e:
                click.echo(f"\nError checking status: {str(e)}")
                break
    
    def get_assessment_status(self, assessment_id):
        """Check the status of an assessment"""
        try:
            status = self.api_client.get_assessment_status(assessment_id)
            
            if self.config.get('output_format') == 'json':
                click.echo(format_json(status))
            else:
                # Display status with color
                status_str = format_status(status['status'])
                
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
                    summary.append(["Overall Score", format_score(status['overall_score'])])
                
                click.echo(format_table(summary))
                
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
                    click.echo(format_table(progress_table))
                
                # Show module scores if completed
                if status['status'] == 'completed' and 'module_scores' in status:
                    click.echo("\nModule Scores:")
                    module_scores = [
                        [m['name'], format_score(m['score'])]
                        for m in status['module_scores']
                    ]
                    click.echo(format_table(module_scores, ["Module", "Score"]))
                
                # Show error if failed
                if status['status'] == 'failed' and 'error' in status:
                    click.echo(f"\nError: {status['error']}")
        except Exception as e:
            click.echo(f"Error getting assessment status: {str(e)}")
    
    def get_assessment_report(self, assessment_id):
        """View the detailed assessment report"""
        try:
            report = self.api_client.get_assessment_report(assessment_id)
            
            if self.config.get('output_format') == 'json':
                click.echo(format_json(report))
            else:
                # Display report summary
                click.echo("\nAssessment Report Summary:")
                summary = [
                    ["Assessment ID", assessment_id],
                    ["Dataset", report['dataset_name']],
                    ["Dataset ID", report['dataset_id']],
                    ["Overall Score", format_score(report['overall_score'])],
                    ["Date", report['created_at']]
                ]
                click.echo(format_table(summary))
                
                # Display module scores
                click.echo("\nModule Scores:")
                module_scores = [
                    [m['name'], format_score(m['score'])]
                    for m in report['module_scores']
                ]
                click.echo(format_table(module_scores, ["Module", "Score"]))
                
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
        except Exception as e:
            click.echo(f"Error getting assessment report: {str(e)}")
    
    def export_assessment_report(self, assessment_id, format='pdf', output=None):
        """Export the assessment report to a file"""
        try:
            # Default output path if not specified
            if not output:
                output = f"./report_{assessment_id}.{format}"
            
            # Get the report content
            content = self.api_client.export_assessment_report(assessment_id, format)
            
            # Write the report to the output file
            with open(output, 'wb') as f:
                f.write(content)
            
            click.echo(f"Report exported successfully to {output}")
        except Exception as e:
            click.echo(f"Error exporting assessment report: {str(e)}")
    
    def list_assessments(self, dataset_id=None, page=1, limit=10):
        """List all assessments"""
        try:
            skip = (page - 1) * limit
            data = self.api_client.list_assessments(dataset_id, skip, limit)
            assessments = data['assessments']
            total = data['total']
            
            if self.config.get('output_format') == 'json':
                click.echo(format_json(data))
            elif self.config.get('output_format') == 'csv':
                headers = ["ID", "Dataset ID", "Status", "Overall Score", "Created"]
                rows = [
                    [
                        a['id'], 
                        a['dataset_id'], 
                        a['status'], 
                        format_score(a.get('overall_score')), 
                        a['created_at']
                    ] 
                    for a in assessments
                ]
                click.echo(format_csv(rows, headers))
            else:
                if assessments:
                    headers = ["ID", "Dataset ID", "Status", "Overall Score", "Created"]
                    rows = []
                    
                    for a in assessments:
                        # Format status with color
                        status = format_status(a['status'])
                        
                        # Format score
                        score = format_score(a.get('overall_score'))
                        
                        rows.append([a['id'], a['dataset_id'], status, score, a['created_at']])
                    
                    click.echo(format_table(rows, headers))
                    
                    show_pagination_info(
                        assessments, total, page, limit, 
                        f"dataaptor assessments{' --dataset-id ' + str(dataset_id) if dataset_id else ''}"
                    )
                else:
                    click.echo("No assessments found.")
        except Exception as e:
            click.echo(f"Error listing assessments: {str(e)}")
