import csv
import re
import os
from django.core.management.base import BaseCommand
from django.db import transaction
from schools.models import School, Facility


class Command(BaseCommand):
    help = 'Import schools from CSV file and clear all existing school data'

    def add_arguments(self, parser):
        parser.add_argument(
            'csv_file',
            type=str,
            help='Path to the CSV file to import'
        )

    def extract_pin_code(self, address):
        """Extract pin code from address text"""
        # Look for patterns like - 600013 or 600013 or Tamil Nadu 600013
        match = re.search(r'[-]?\s*(\d{6})', address)
        if match:
            return match.group(1)
        return "600001"  # Default Chennai pin code

    def extract_board_from_syllabus(self, syllabus):
        """Extract board code from syllabus name by checking for key terms"""
        if not syllabus or not syllabus.strip():
            return 'CBSE'  # Default if empty
        
        syllabus_upper = syllabus.upper()
        
        # Check for key terms (order matters - check more specific first)
        if 'MATRICULATION' in syllabus_upper:
            return 'State'
        elif 'CBSE' in syllabus_upper:
            return 'CBSE'
        elif 'IB' in syllabus_upper:
            return 'IB'
        elif 'IGCSE' in syllabus_upper:
            return 'IGCSE'
        elif 'ICSE' in syllabus_upper:
            return 'ICSE'
        else:
            return 'CBSE'  # Default to CBSE

    def get_curriculum_website(self, board):
        """Get curriculum website based on board"""
        websites = {
            'CBSE': 'https://www.cbse.gov.in',
            'ICSE': 'https://www.cisce.org',
            'IB': 'https://www.ibo.org',
            'IGCSE': 'https://www.cambridgeinternational.org'
        }
        return websites.get(board, '')

    def infer_co_ed_type(self, name):
        """Infer co-ed type from school name"""
        if not name:
            return 'C'  # Default to Co-ed
        
        name_lower = name.lower()
        if 'boys' in name_lower or 'boy' in name_lower:
            return 'B'
        elif 'girls' in name_lower or 'girl' in name_lower:
            return 'G'
        else:
            return 'C'  # Default to Co-ed
    
    def clean_address(self, address):
        """Clean address by removing phone numbers and special characters"""
        # Remove phone numbers (patterns like � 096770 15266 or - 082207 66633)
        address = re.sub(r'[�–—]\s*\d{10,11}', '', address)
        address = re.sub(r'[-]\s*\d{10,11}', '', address)
        # Clean up extra spaces
        address = re.sub(r'\s+', ' ', address).strip()
        return address

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        
        if not os.path.exists(csv_file):
            self.stdout.write(self.style.ERROR(f'CSV file not found: {csv_file}'))
            return

        # Clear all existing schools
        self.stdout.write('Clearing all existing schools...')
        School.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('All existing schools deleted.'))

        # Read and import CSV
        self.stdout.write(f'Reading CSV file: {csv_file}')
        schools_created = 0
        errors = []

        try:
            # Try different encodings
            encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
            file_handle = None
            reader = None
            
            for encoding in encodings:
                try:
                    file_handle = open(csv_file, 'r', encoding=encoding)
                    test_reader = csv.DictReader(file_handle)
                    # Try reading first row to test encoding
                    next(test_reader)
                    file_handle.seek(0)  # Reset to beginning
                    # Create reader and strip BOM from fieldnames
                    reader = csv.DictReader(file_handle)
                    # Strip BOM from fieldnames (handle both UTF-8 BOM \ufeff and latin-1 BOM ï»¿)
                    if reader.fieldnames:
                        reader.fieldnames = [
                            name.lstrip('\ufeff').lstrip('ï»¿').strip() if name else name 
                            for name in reader.fieldnames
                        ]
                        # Remove None entries
                        reader.fieldnames = [name for name in reader.fieldnames if name]
                    self.stdout.write(f'Using encoding: {encoding}')
                    break
                except (UnicodeDecodeError, StopIteration):
                    if file_handle:
                        file_handle.close()
                        file_handle = None
                    continue
            
            if not reader or not file_handle:
                self.stdout.write(self.style.ERROR('Could not read CSV file with any encoding'))
                return
            
            # Process rows without atomic transaction to allow partial success
            for row_num, row in enumerate(reader, start=2):  # Start at 2 because row 1 is header
                try:
                    school_name = row.get('School Name', '').strip()
                    syllabus = row.get('Syllabus', '').strip()
                    address = row.get('Address', '').strip()
                    website = row.get('Website', '').strip()
                    google_maps_link = row.get('Google Maps Direction', '').strip()

                    if not school_name:
                        errors.append(f'Row {row_num}: Missing school name')
                        continue

                    # Extract board from syllabus
                    board = self.extract_board_from_syllabus(syllabus)
                    
                    # Infer co_ed_type from school name
                    co_ed_type = self.infer_co_ed_type(school_name)
                    
                    # Clean and extract pin code from address
                    cleaned_address = self.clean_address(address)
                    pin_code = self.extract_pin_code(address)
                    
                    # Ensure all fields are strings and properly truncated
                    final_name = str(school_name)[:200] if school_name else 'Unknown School'
                    final_location = str(cleaned_address)[:200] if cleaned_address else ''
                    final_pin_code = str(pin_code)[:10] if pin_code else ''
                    final_syllabus = str(syllabus)[:100] if syllabus else ''
                    final_board = str(board)[:50] if board else 'CBSE'
                    
                    # Ensure board is a valid choice
                    valid_boards = ['CBSE', 'ICSE', 'IB', 'IGCSE', 'State']
                    if final_board not in valid_boards:
                        final_board = 'CBSE'
                    
                    # URLs - truncate google_maps_link to 200 chars (DB constraint from migration)
                    # Note: The migration created it as varchar(200) instead of unlimited URLField
                    final_website = str(website) if website else ''
                    final_curriculum_website = str(self.get_curriculum_website(board)) if board else ''
                    final_google_maps_link = str(google_maps_link)[:200] if google_maps_link else ''  # Truncate to 200 chars
                    
                    # Double-check all string lengths
                    assert len(final_name) <= 200, f"Name too long: {len(final_name)}"
                    assert len(final_location) <= 200, f"Location too long: {len(final_location)}"
                    assert len(final_pin_code) <= 10, f"Pin code too long: {len(final_pin_code)}"
                    assert len(final_syllabus) <= 100, f"Syllabus too long: {len(final_syllabus)}"
                    assert len(final_board) <= 50, f"Board too long: {len(final_board)}"
                    
                    # Only set fields that are available in CSV, leave others empty/default
                    # CSV has: School Name, Syllabus, Address, Website, Google Maps Direction
                    school = School(
                        name=final_name,
                        location=final_location,
                        pin_code=final_pin_code,
                        board=final_board,
                        grades_offered='',  # Not in CSV - leave empty
                        co_ed_type=co_ed_type,  # Inferred from school name
                        distance=0.0,  # Not in CSV - set to 0
                        bus_availability=False,  # Required field, default to False
                        syllabus=final_syllabus,
                        website=final_website,
                        curriculum_website=final_curriculum_website,
                        google_maps_link=final_google_maps_link,
                        rating=0.0,  # Not in CSV - set to 0
                        fees_by_grade='',  # Not in CSV - leave empty (will show "No data")
                    )
                    school.save()
                    schools_created += 1
                    
                    if schools_created % 50 == 0:
                        self.stdout.write(f'Imported {schools_created} schools...')

                except Exception as e:
                    error_msg = str(e)
                    # Add more context for debugging
                    debug_info = []
                    if 'school_name' in locals():
                        debug_info.append(f'Name len: {len(final_name) if "final_name" in locals() else len(school_name)}')
                    if 'cleaned_address' in locals():
                        debug_info.append(f'Location len: {len(final_location) if "final_location" in locals() else len(cleaned_address)}')
                    if 'syllabus' in locals():
                        debug_info.append(f'Syllabus len: {len(final_syllabus) if "final_syllabus" in locals() else len(syllabus)}')
                    if 'board' in locals():
                        debug_info.append(f'Board: {final_board if "final_board" in locals() else board}')
                    
                    if debug_info:
                        error_msg += f' | {" | ".join(debug_info)}'
                    errors.append(f'Row {row_num}: {error_msg}')
                    if len(errors) <= 10:  # Only print first 10 errors to avoid spam
                        self.stdout.write(self.style.WARNING(f'Error processing row {row_num}: {error_msg}'))
            
            # Close file handle
            if file_handle:
                file_handle.close()

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error reading CSV file: {str(e)}'))
            if file_handle:
                file_handle.close()
            return

        # Summary
        self.stdout.write(self.style.SUCCESS(f'\nSuccessfully imported {schools_created} schools!'))
        
        if errors:
            self.stdout.write(self.style.WARNING(f'\n{len(errors)} errors occurred:'))
            for error in errors[:10]:  # Show first 10 errors
                self.stdout.write(self.style.WARNING(f'  - {error}'))
            if len(errors) > 10:
                self.stdout.write(self.style.WARNING(f'  ... and {len(errors) - 10} more errors'))
