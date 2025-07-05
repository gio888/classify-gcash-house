#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GnuCash Transaction Classifier - Monthly Processing CLI
Automated workflow for processing monthly house expenses.
"""

import asyncio
import argparse
import sys
import os
from pathlib import Path
import re
from datetime import datetime
import csv

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from classifier import ClassifierFactory
except ImportError as e:
    print("❌ Error: Could not import classifier module.")
    print(f"   Details: {e}")
    print()
    print("💡 Quick fix:")
    print("   1. Make sure you're in the project root directory:")
    print("      cd /Users/gio/Code/classify-gcash-house")
    print()
    print("   2. Install dependencies:")
    print("      pip install -r requirements.txt")
    print("      # or:")
    print("      pip3 install -r requirements.txt")
    print()
    print("   3. Try again:")
    print("      ./classify_transactions.py --auto-house")
    sys.exit(1)


class TransactionProcessor:
    def __init__(self):
        self.house_expenses_folder = "/Users/gio/Library/CloudStorage/GoogleDrive-gbacareza@gmail.com/My Drive/Money/House Expenses"
        self.chart_of_accounts = "chart-of-accounts.txt"
        
    def find_newest_csv(self):
        """Find the newest CSV file that doesn't start with 'For Import'."""
        try:
            folder_path = Path(self.house_expenses_folder)
            if not folder_path.exists():
                return None, "Google Drive folder not found"
            
            # Find all CSV files that don't start with "For Import"
            csv_files = []
            for file in folder_path.glob("*.csv"):
                if not file.name.startswith("For Import"):
                    csv_files.append(file)
            
            if not csv_files:
                return None, "No CSV files found (excluding 'For Import' files)"
            
            # Sort by modification time, newest first
            csv_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            newest_file = csv_files[0]
            
            return newest_file, None
            
        except Exception as e:
            return None, f"Error scanning folder: {str(e)}"
    
    def extract_date_from_filename(self, filename):
        """Extract date from filename to determine output month."""
        # Look for date patterns in filename
        date_patterns = [
            r"(\d{4})-(\d{2})-(\d{2})",  # YYYY-MM-DD
            r"(\d{4})-(\d{2})",          # YYYY-MM
            r"(\d{2})-(\d{2})-(\d{4})",  # MM-DD-YYYY
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, filename)
            if match:
                groups = match.groups()
                if len(groups) == 3:
                    try:
                        if len(groups[0]) == 4:  # YYYY-MM-DD
                            return datetime(int(groups[0]), int(groups[1]), int(groups[2]))
                        else:  # MM-DD-YYYY
                            return datetime(int(groups[2]), int(groups[0]), int(groups[1]))
                    except ValueError:
                        continue
                elif len(groups) == 2:  # YYYY-MM
                    try:
                        return datetime(int(groups[0]), int(groups[1]), 1)
                    except ValueError:
                        continue
        
        # Fallback to current date
        return datetime.now()
    
    def generate_output_filename(self, input_file):
        """Generate output filename based on input file date."""
        date_obj = self.extract_date_from_filename(input_file.name)
        return f"For Import House Kitty Transactions - {date_obj.strftime('%Y-%m')}.csv"
    
    def get_file_info(self, file_path):
        """Get basic information about the CSV file."""
        try:
            with open(file_path, 'r') as f:
                reader = csv.reader(f)
                header = next(reader)
                transaction_count = sum(1 for _ in reader)
            
            file_size = file_path.stat().st_size / (1024 * 1024)  # MB
            return {
                'transaction_count': transaction_count,
                'file_size': file_size,
                'header': header
            }
        except Exception as e:
            return None
    
    def confirm_processing(self, input_file, output_file, file_info):
        """Ask user for confirmation before processing."""
        print(f"\n📄 FOUND FILE TO PROCESS:")
        print(f"   Input:  {input_file.name}")
        print(f"   Size:   {file_info['file_size']:.2f} MB")
        print(f"   Count:  {file_info['transaction_count']:,} transactions")
        print(f"   Output: {output_file}")
        print()
        
        while True:
            response = input("🤔 Process this file? (y/n): ").lower().strip()
            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no']:
                return False
            else:
                print("Please enter 'y' or 'n'")
    
    async def process_file(self, input_file, output_file):
        """Process the CSV file through the classifier."""
        print(f"\n⚙️  PROCESSING TRANSACTIONS...")
        print("=" * 50)
        
        try:
            # Create classifier
            print("🏭 Creating classifier...")
            classifier = await ClassifierFactory.create_minimal_classifier(
                chart_of_accounts_path=self.chart_of_accounts
            )
            
            # Process the file
            print("📊 Classifying transactions...")
            start_time = asyncio.get_event_loop().time()
            
            batch_result = await classifier.classify_batch(
                source_file=str(input_file),
                output_file=str(output_file)
            )
            
            processing_time = asyncio.get_event_loop().time() - start_time
            
            if batch_result.is_err():
                return False, f"Processing failed: {batch_result.error}"
            
            result = batch_result.value
            
            # Display results
            print(f"\n✅ PROCESSING COMPLETE!")
            print("=" * 50)
            print(f"📈 Total Transactions: {result.total_transactions:,}")
            print(f"✅ Successful Classifications: {result.successful_classifications:,}")
            print(f"❌ Failed Classifications: {result.failed_classifications:,}")
            print(f"📊 Success Rate: {result.success_rate:.1f}%")
            print(f"⏱️  Processing Time: {processing_time:.2f} seconds")
            
            if result.needs_review_count > 0:
                print(f"⚠️  Transactions Needing Review: {result.needs_review_count:,}")
            
            print(f"\n📁 Output saved to: {output_file}")
            print(f"🎯 Ready for GnuCash import!")
            
            return True, None
            
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"
    
    async def run_auto_house(self):
        """Run the automated house expenses workflow."""
        print("🏠 GnuCash Transaction Classifier - House Expenses")
        print("=" * 60)
        
        # Find newest CSV file
        print("🔍 Searching for newest CSV file...")
        input_file, error = self.find_newest_csv()
        
        if error:
            print(f"❌ {error}")
            return False
        
        # Get file information
        file_info = self.get_file_info(input_file)
        if not file_info:
            print("❌ Could not read file information")
            return False
        
        # Generate output filename
        output_filename = self.generate_output_filename(input_file)
        output_file = input_file.parent / output_filename
        
        # Check if output file already exists
        if output_file.exists():
            print(f"⚠️  Output file already exists: {output_filename}")
            while True:
                response = input("🤔 Overwrite existing file? (y/n): ").lower().strip()
                if response in ['y', 'yes']:
                    break
                elif response in ['n', 'no']:
                    print("❌ Cancelled by user")
                    return False
                else:
                    print("Please enter 'y' or 'n'")
        
        # Ask for confirmation
        if not self.confirm_processing(input_file, output_filename, file_info):
            print("❌ Cancelled by user")
            return False
        
        # Process the file
        success, error = await self.process_file(input_file, output_file)
        
        if not success:
            print(f"❌ {error}")
            return False
        
        print(f"\n🎉 Monthly processing complete!")
        print(f"📂 Import file ready: {output_filename}")
        
        return True


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="GnuCash Transaction Classifier - Monthly Processing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Monthly Usage:
  ./classify_transactions.py --auto-house
  
This will:
  1. Find the newest CSV file in your Google Drive folder
  2. Ask for confirmation before processing
  3. Classify all transactions using the rule engine
  4. Generate a "For Import" file ready for GnuCash import
        """
    )
    
    parser.add_argument(
        "--auto-house",
        action="store_true",
        help="Automatically process house expenses (main monthly workflow)"
    )
    
    args = parser.parse_args()
    
    if not args.auto_house:
        parser.print_help()
        return 1
    
    # Check prerequisites
    if not Path("chart-of-accounts.txt").exists():
        print("❌ Error: chart-of-accounts.txt not found")
        print("💡 Make sure you're running from the project root directory")
        return 1
    
    # Run the processor
    processor = TransactionProcessor()
    
    try:
        success = asyncio.run(processor.run_auto_house())
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n❌ Cancelled by user")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())