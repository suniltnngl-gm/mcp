import argparse
from pathlib import Path
from datetime import date
import logging

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from devflow_tracker.project_scanner import scan_workspace
from devflow_tracker.data_store import save_workspace_status, load_workspace_status
from devflow_tracker.models import WorkspaceStatus


def main():
    parser = argparse.ArgumentParser(description="DevFlow Tracker: Central Progress Tracking System.")
    parser.add_argument(
        "--scan", 
        action="store_true", 
        help="Scan specified project directories and update the central status."
    )
    parser.add_argument(
        "--projects", 
        nargs='+', 
        help="List of project directories to scan (absolute paths)."
    )
    parser.add_argument(
        "--report", 
        action="store_true", 
        help="Generate and display a progress report."
    )
    parser.add_argument(
        "--output-file", 
        type=str, 
        default="progress_data.json", 
        help="File to save/load workspace status (default: progress_data.json)"
    )

    args = parser.parse_args()

    output_path = Path(args.output_file)

    if args.scan:
        if not args.projects:
            logger.error("Error: --projects must be specified when --scan is used.")
            return
        
        project_paths = [Path(p) for p in args.projects]
        logger.info(f"Scanning projects: {[str(p) for p in project_paths]}...")
        workspace_status = scan_workspace(project_paths)
        save_workspace_status(workspace_status, output_path)
        logger.info(f"Scan complete. Status saved to {output_path}")
    
    if args.report:
        workspace_status = load_workspace_status(output_path)
        if not workspace_status:
            logger.warning(f"No workspace status found at {output_path}. Please run --scan first.")
            return
        
        print("\n--- DevFlow Tracker Progress Report ---")
        print(f"Last Scanned: {workspace_status.last_scanned}")
        print(f"Overall Health: {workspace_status.overall_health}")
        print("\nProjects:")
        for project in workspace_status.projects:
            print(f"  - {project.project_name}:")
            print(f"    Status: {project.overall_status}")
            print(f"    Completion: {project.completion_percentage:.2f}%")
            if project.markdown_documents:
                print(f"    Markdown Docs: {len(project.markdown_documents)}")
                for doc in project.markdown_documents:
                    if doc.metadata:
                        print(f"      - {Path(doc.file_path).name} (Status: {doc.metadata.status}, Confidence: {doc.metadata.confidence_level})")
                    else:
                        print(f"      - {Path(doc.file_path).name} (No metadata)")
                    if doc.checklists:
                        completed_items = sum(1 for item in doc.checklists if item.completed)
                        print(f"        Checklist: {completed_items}/{len(doc.checklists)} completed")
            else:
                print("    No Markdown documents found.")
        print("---------------------------------------")


if __name__ == "__main__":
    main()
