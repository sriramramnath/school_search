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
    
    def parse_review_count(self, review_count_str):
        """Parse review count, handling formats like (122), 122, or empty"""
        if not review_count_str or not review_count_str.strip():
            return 0
        
        review_count_str = review_count_str.strip()
        # Remove brackets if present
        review_count_str = re.sub(r'[()]', '', review_count_str)
        
        try:
            return int(review_count_str)
        except ValueError:
            return 0
    
    def parse_rating(self, rating_str):
        """Parse rating from string, return 0.0 if empty or invalid"""
        if not rating_str or not rating_str.strip():
            return 0.0
        
        try:
            rating = float(rating_str.strip())
            # Ensure rating is between 0 and 5
            if rating < 0:
                return 0.0
            if rating > 5:
                return 5.0
            return rating
        except ValueError:
            return 0.0
    
    def combine_address_lines(self, line1, line2):
        """Combine two address lines, filtering out placeholder values"""
        parts = []
        
        # Clean and add first line
        if line1 and line1.strip() and line1.strip() not in ['·', 'Closed', 'Closes soon']:
            parts.append(line1.strip())
        
        # Clean and add second line
        if line2 and line2.strip() and line2.strip() not in ['·', 'Closed', 'Closes soon']:
            parts.append(line2.strip())
        
        combined = ', '.join(parts)
        # Clean up extra spaces
        combined = re.sub(r'\s+', ' ', combined).strip()
        return combined
    
    def clean_review_text(self, review_text):
        """Clean review text by removing extra quotes and whitespace"""
        if not review_text or not review_text.strip():
            return ''
        
        # Remove surrounding quotes (handles both single and triple quotes)
        cleaned = review_text.strip()
        # Remove triple quotes if present
        cleaned = re.sub(r'^["\']{3}(.*)["\']{3}$', r'\1', cleaned)
        # Remove single quotes if present
        cleaned = re.sub(r'^["\'](.*)["\']$', r'\1', cleaned)
        # Clean up extra spaces
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        return cleaned

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
                    # New CSV format columns
                    school_name = row.get('School Name', '').strip()
                    rating_str = row.get('Rating', '').strip()
                    review_count_str = row.get('Review Count', '').strip()
                    curriculum = row.get('Curriculum', '').strip()
                    address_line_1 = row.get('1st Address line', '').strip()
                    address_line_2 = row.get('2nd Address line', '').strip()
                    phone_number = row.get('Phone Number', '').strip()
                    website = row.get('Website', '').strip()
                    google_maps_link = row.get('Google Maps URL', '').strip()
                    top_review = row.get('Reviews', '').strip()
                    
                    # Fallback to old CSV format if new columns not found
                    if not school_name:
                        school_name = row.get('School Name', '').strip()
                    if not curriculum:
                        curriculum = row.get('Syllabus', '').strip()
                    if not google_maps_link:
                        google_maps_link = row.get('Google Maps Direction', '').strip()
                    
                    if not school_name:
                        errors.append(f'Row {row_num}: Missing school name')
                        continue

                    # Extract board from curriculum (same as syllabus)
                    board = self.extract_board_from_syllabus(curriculum)
                    
                    # Infer co_ed_type from school name
                    co_ed_type = self.infer_co_ed_type(school_name)
                    
                    # Combine address lines
                    combined_address = self.combine_address_lines(address_line_1, address_line_2)
                    
                    # Truncate combined address to fit location field (200 chars max)
                    if len(combined_address) > 200:
                        combined_address = combined_address[:197] + '...'
                    
                    # Extract pin code from combined address
                    pin_code = self.extract_pin_code(combined_address)
                    
                    # Parse rating and review count
                    rating = self.parse_rating(rating_str)
                    review_count = self.parse_review_count(review_count_str)
                    
                    # Ensure all fields are strings and properly truncated
                    final_name = str(school_name)[:200] if school_name else 'Unknown School'
                    final_location = str(combined_address)[:200] if combined_address else ''
                    final_pin_code = str(pin_code)[:10] if pin_code else '600001'
                    final_syllabus = str(curriculum)[:100] if curriculum else ''
                    final_board = str(board)[:50] if board else 'CBSE'
                    final_phone = str(phone_number)[:20] if phone_number else ''
                    final_address_line_1 = str(address_line_1)[:200] if address_line_1 else ''
                    final_address_line_2 = str(address_line_2)[:200] if address_line_2 else ''
                    final_top_review = self.clean_review_text(top_review)
                    
                    # Ensure board is a valid choice
                    valid_boards = ['CBSE', 'ICSE', 'IB', 'IGCSE', 'State']
                    if final_board not in valid_boards:
                        final_board = 'CBSE'
                    
                    # URLs - truncate to reasonable length (some databases may have constraints)
                    # URLField should handle long URLs, but truncate to 500 chars to be safe
                    final_website = str(website)[:500] if website else ''
                    final_curriculum_website = str(self.get_curriculum_website(board))[:500] if board else ''
                    final_google_maps_link = str(google_maps_link)[:500] if google_maps_link else ''
                    
                    # Double-check all string lengths and log if any are too long
                    field_lengths = {
                        'name': len(final_name),
                        'location': len(final_location),
                        'pin_code': len(final_pin_code),
                        'syllabus': len(final_syllabus),
                        'board': len(final_board),
                        'phone': len(final_phone),
                        'address_line_1': len(final_address_line_1),
                        'address_line_2': len(final_address_line_2),
                        'website': len(final_website),
                        'google_maps_link': len(final_google_maps_link),
                    }
                    
                    # Validate lengths
                    if field_lengths['name'] > 200:
                        raise ValueError(f"Name too long: {field_lengths['name']}")
                    if field_lengths['location'] > 200:
                        raise ValueError(f"Location too long: {field_lengths['location']}")
                    if field_lengths['pin_code'] > 10:
                        raise ValueError(f"Pin code too long: {field_lengths['pin_code']}")
                    if field_lengths['syllabus'] > 100:
                        raise ValueError(f"Syllabus too long: {field_lengths['syllabus']}")
                    if field_lengths['board'] > 50:
                        raise ValueError(f"Board too long: {field_lengths['board']}")
                    if field_lengths['phone'] > 20:
                        raise ValueError(f"Phone too long: {field_lengths['phone']}")
                    if field_lengths['address_line_1'] > 200:
                        raise ValueError(f"Address line 1 too long: {field_lengths['address_line_1']}")
                    if field_lengths['address_line_2'] > 200:
                        raise ValueError(f"Address line 2 too long: {field_lengths['address_line_2']}")
                    
                    # Create school with all fields (existing + new)
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
                        rating=rating,  # From Rating column
                        fees_by_grade='',  # Not in CSV - leave empty (will show "No data")
                        # New fields
                        phone_number=final_phone,
                        review_count=review_count,
                        address_line_1=final_address_line_1,
                        address_line_2=final_address_line_2,
                        top_review=final_top_review,
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
                    if 'final_location' in locals():
                        debug_info.append(f'Location len: {len(final_location)}')
                    if 'final_address_line_1' in locals():
                        debug_info.append(f'Addr1 len: {len(final_address_line_1)}')
                    if 'final_address_line_2' in locals():
                        debug_info.append(f'Addr2 len: {len(final_address_line_2)}')
                    if 'final_website' in locals():
                        debug_info.append(f'Website len: {len(final_website)}')
                    if 'final_google_maps_link' in locals():
                        debug_info.append(f'Maps len: {len(final_google_maps_link)}')
                    if 'final_syllabus' in locals():
                        debug_info.append(f'Syllabus len: {len(final_syllabus)}')
                    if 'final_board' in locals():
                        debug_info.append(f'Board: {final_board}')
                    
                    if debug_info:
                        error_msg += f' | {" | ".join(debug_info)}'
                    # Add field lengths if available
                    if 'field_lengths' in locals():
                        error_msg += f' | Field lengths: {field_lengths}'
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



