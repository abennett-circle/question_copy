#!/usr/bin/env python3
# Last Updated: 2025-08-22
# Running this script will fill the unanswered questionnaire with the best matches from the reference questionnaire
"""
Question Copy Script - Command-line version of tester.ipynb

This script processes questionnaires by matching questions and generating a combined output.
It replicates the functionality of tester.ipynb but as a runnable Python script.

PREREQUISITES:
    1. Create a config.env file with your API credentials:
       cp config.env.template config.env
       # Edit config.env with your actual CHATAI_BASE_URL and CHATAI_API_KEY

    2. Install required dependencies:
       pip install -r requirements.txt

Usage:
    python question_copy.py <reference_file> <unanswered_file> [options]

Required Arguments:
    reference_file      Path to the reference questionnaire file (CSV/Excel)
    unanswered_file     Path to the unanswered questionnaire file (CSV/Excel)

Optional Arguments:
    --ref-question-col      Reference questionnaire question column (default: "Question")
    --ref-answer-col        Reference questionnaire answer column (default: "Answer") 
    --unans-question-col    Unanswered questionnaire question column (default: "Question")
    --unans-answer-col      Unanswered questionnaire answer column (default: "Answer")
    --output               Output file name (default: "combined_questionnaire.csv")
    --skip-config-check    Skip config file validation (for testing purposes)
    --help                 Show this help message

Examples:
    python question_copy.py data/ref.csv data/unans.csv
    python question_copy.py data/ref.xlsx data/unans.xlsx --output results.csv
    python question_copy.py ref.csv unans.csv --ref-question-col "Question - Full" --ref-answer-col "Answer - Full"
    python question_copy.py data/ref.csv data/unans.csv --skip-config-check  # Skip config validation
"""

################################### IMPORTS #############################################
import sys
import argparse
import os
from dotenv import load_dotenv
from src.Questionnaire_Filler import Questionnaire_Filler
################################### IMPORTS #############################################

# Add the current directory to the Python path
sys.path.insert(0, '.')

def validate_config():
    """Validate that the config.env file exists and contains required variables."""
    
    # List of possible config file locations
    config_paths = ['config.env', '../config.env', './config.env']
    config_found = False
    
    # Try to find and load config file
    for config_path in config_paths:
        if os.path.exists(config_path):
            load_dotenv(config_path)
            config_found = True
            print(f"✅ Found config file: {config_path}")
            break
    
    # If the config file is not found, return False and alert user
    if not config_found:
        print("❌ Config file not found!")
        print("💡 Please create a config.env file with your API credentials.")
        print("   You can copy config.env.template and update it with your values:")
        print("   cp config.env.template config.env")
        print("   # Then edit config.env with your actual API URL and key")
        return False
    
    # Check required environment variables
    required_vars = ['CHATAI_BASE_URL', 'CHATAI_API_KEY']
    missing_vars = []

    # If the config file is found, check the required environment variables for warnings
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
        elif value in ['https://urlgoesheretest12345abcdefg.com', 'K3yg0e5here']:
            # Check for template placeholder values
            print(f"⚠️  Warning: {var} appears to contain a template value")
            print(f"   Current value: {value}")
            print("   Please update config.env with your actual credentials")
            missing_vars.append(var)
        else:
            # Mask sensitive values in output
            if 'KEY' in var:
                masked_value = value[:8] + '...' + value[-4:] if len(value) > 12 else '***masked***'
                print(f"✅ {var}: {masked_value}")
            else:
                print(f"✅ {var}: {value}")
    
    # If the required environment variables are missing, return False and alert user
    if missing_vars:
        print(f"❌ Missing or invalid required environment variables: {', '.join(missing_vars)}")
        print("💡 Please update your config.env file with valid values")
        return False
    
    # If the required environment variables are present, return True
    return True


def main():
    """Main function to process questionnaires with command-line arguments."""
    
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description="Process questionnaires by matching questions and generating combined output",
        formatter_class=argparse.RawDescriptionHelpFormatter,
                epilog="""
                 Examples:
                 %(prog)s data/reference.csv data/unanswered.csv
                 %(prog)s data/ref.xlsx data/unans.xlsx --output results.csv
                 %(prog)s ref.csv unans.csv --ref-question-col "Question - Full" --ref-answer-col "Answer - Full"
                         """
    )
    
    # Required arguments
    parser.add_argument('reference_file', 
                       help='Path to the reference questionnaire file (CSV/Excel)')
    parser.add_argument('unanswered_file',
                       help='Path to the unanswered questionnaire file (CSV/Excel)')
    
    # Optional arguments with defaults
    parser.add_argument('--ref-question-col', 
                       default='Question',
                       help='Reference questionnaire question column (default: "Question")')
    parser.add_argument('--ref-answer-col',
                       default='Answer', 
                       help='Reference questionnaire answer column (default: "Answer")')
    parser.add_argument('--unans-question-col',
                       default='Question',
                       help='Unanswered questionnaire question column (default: "Question")')
    parser.add_argument('--unans-answer-col',
                       default='Answer',
                       help='Unanswered questionnaire answer column (default: "Answer")')
    parser.add_argument('--output',
                       default='combined_questionnaire.csv',
                       help='Output file name (default: "combined_questionnaire.csv")')
    parser.add_argument('--skip-config-check',
                       action='store_true',
                       help='Skip config file validation (for testing purposes)')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Validate config file and environment variables (unless skipped)
    if not args.skip_config_check:
        print("🔧 Validating configuration...")
        if not validate_config():
            sys.exit(1)
        print()
    else:
        print("⚠️  Skipping config validation (--skip-config-check enabled)")
        print()
    
    # Validate input files exist
    if not os.path.exists(args.reference_file):
        print(f"❌ Error: Reference file '{args.reference_file}' not found!")
        sys.exit(1)
        
    if not os.path.exists(args.unanswered_file):
        print(f"❌ Error: Unanswered file '{args.unanswered_file}' not found!")
        sys.exit(1)
    
    # Alert user of the files being processed
    print("🚀 Starting questionnaire processing...")
    print(f"📋 Reference file: {args.reference_file}")
    print(f"📋 Unanswered file: {args.unanswered_file}")
    print(f"📊 Output file: {args.output}")
    print()
    
    try:
        # Initialize the questionnaire filler
        print("🔧 Initializing Questionnaire Filler...")
        filler = Questionnaire_Filler(
            reference_file_name=args.reference_file,
            reference_question_col=args.ref_question_col,
            reference_answer_col=args.ref_answer_col,
            unanswered_file_name=args.unanswered_file,
            unanswered_question_col=args.unans_question_col,
            unanswered_answer_col=args.unans_answer_col
        )
        
        # Fill the questionnaire with matched answers
        print("🔍 Processing question matches...")
        matches = filler._fill_best_matches()
        
        print(f"\n📊 Question Matching Results:")
        print("=" * 60)
        
        # Review and display the matches
        matched_count = 0
        unmatched_count = 0
        
        # Counts the matched and unmatched questions
        for match in matches:
            if match.get("no_match", False):
                unmatched_count += 1
            else:
                matched_count += 1
        
        # Summary
        total_questions = len(matches)
        print("=" * 60)
        print(f"📈 Summary:")
        print(f"   Total questions processed: {total_questions}")
        print(f"   Successfully matched: {matched_count}")
        print(f"   No matches found: {unmatched_count}")
        print(f"   Match rate: {(matched_count/total_questions)*100:.1f}%" if total_questions > 0 else "   Match rate: 0%")
        print()
        
        # Generate the combined questionnaire
        print("📝 Generating combined questionnaire...")
        filler.generate_combined_questionnaire(args.output)
        
        print("✅ Processing completed successfully!")
        print(f"📄 Results saved to: {args.output}")
    
    # Catch errors
    except FileNotFoundError as e:
        print(f"❌ File Error: {e}")
        sys.exit(1)
    except KeyError as e:
        print(f"❌ Column Error: {e}")
        print("💡 Tip: Check your column names with --ref-question-col, --ref-answer-col, etc.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        print("💡 Tip: Check your input files and column names")
        print("💡 Tip: Check your API Key and URL in the config.env file are correct. These regenerate every so often!")
        sys.exit(1)

# Main function to run the script
if __name__ == "__main__":
    main()