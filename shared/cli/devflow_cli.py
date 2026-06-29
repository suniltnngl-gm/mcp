#!/usr/bin/env python3
"""
DevFlow CLI

This script provides a unified command-line interface for the DevFlow tools.
"""

import argparse
import subprocess

def generate_kb(args):
    """Generate the knowledge base."""
    print("Generating the knowledge base...")
    subprocess.run(["python", "/media/sunil-kr/storage/workspace/scripts/repo_knowledgebase.py"])

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="DevFlow CLI")
    subparsers = parser.add_subparsers()

    # generate-kb command
    parser_generate_kb = subparsers.add_parser("generate-kb", help="Generate the knowledge base.")
    parser_generate_kb.set_defaults(func=generate_kb)

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
