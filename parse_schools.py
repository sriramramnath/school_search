#!/usr/bin/env python3
"""
Script to parse school data from markdown files and generate JSON fixtures
"""
import json
import re
from datetime import datetime
import random

def extract_pin_code(text):
    """Extract pin code from address text"""
    # Look for patterns like - 600013 or 600013
    match = re.search(r'[-]?\s*(\d{6})', text)
    if match:
        return match.group(1)
    return "600001"  # Default Chennai pin code

def parse_school_file(filepath, board):
    """Parse a markdown file containing school information"""
    schools = []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = [line.rstrip('\n') for line in f.readlines()]
    
    if not lines:
        print(f"  Warning: {filepath} is empty or could not be read")
        return schools
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Skip empty lines
        if not line:
            i += 1
            continue
        
        # Check if this is a school name (not a field label)
        if line and line not in ['Address', 'State', 'District', 'Phone', 'Email', 'Website', ':']:
            # Start new school
            school_name = line
            i += 1
            
            # Initialize school data
            current_school = {
                'name': school_name,
                'board': board,
                'address': '',
                'state': 'Tamil Nadu',
                'district': 'Chennai',
                'phone': '',
                'email': '',
                'website': '',
                'pin_code': '600001'
            }
            
            # Parse fields
            while i < len(lines):
                line = lines[i].strip()
                
                if not line:
                    i += 1
                    continue
                
                # Check if we've hit the next school (a line that's not a field label and not ':')
                if line and line not in ['Address', 'State', 'District', 'Phone', 'Email', 'Website', ':']:
                    # This is the next school, break and process current school
                    break
                
                if line == 'Address':
                    i += 1  # Skip ':'
                    if i < len(lines) and lines[i].strip() == ':':
                        i += 1
                    
                    # Collect address lines
                    address_lines = []
                    while i < len(lines):
                        addr_line = lines[i].strip()
                        if not addr_line:
                            i += 1
                            continue
                        if addr_line in ['State', 'District', 'Phone', 'Email', 'Website', ':']:
                            break
                        address_lines.append(addr_line)
                        i += 1
                    
                    if address_lines:
                        address_text = ' '.join(address_lines)
                        current_school['address'] = address_text
                        current_school['pin_code'] = extract_pin_code(address_text)
                    continue
                
                elif line == 'State':
                    i += 1  # Skip ':'
                    if i < len(lines) and lines[i].strip() == ':':
                        i += 1
                    if i < len(lines):
                        current_school['state'] = lines[i].strip()
                    i += 1
                    continue
                
                elif line == 'District':
                    i += 1  # Skip ':'
                    if i < len(lines) and lines[i].strip() == ':':
                        i += 1
                    if i < len(lines):
                        current_school['district'] = lines[i].strip()
                    i += 1
                    continue
                
                elif line == 'Phone':
                    i += 1  # Skip ':'
                    if i < len(lines) and lines[i].strip() == ':':
                        i += 1
                    
                    phone_parts = []
                    while i < len(lines):
                        phone_line = lines[i].strip()
                        if not phone_line:
                            i += 1
                            continue
                        if phone_line in ['State', 'District', 'Address', 'Email', 'Website', ':']:
                            break
                        phone_parts.append(phone_line)
                        i += 1
                    
                    if phone_parts:
                        current_school['phone'] = ', '.join(phone_parts)
                    continue
                
                elif line == 'Email':
                    i += 1  # Skip ':'
                    if i < len(lines) and lines[i].strip() == ':':
                        i += 1
                    if i < len(lines):
                        current_school['email'] = lines[i].strip()
                    i += 1
                    continue
                
                elif line == 'Website':
                    i += 1  # Skip ':'
                    if i < len(lines) and lines[i].strip() == ':':
                        i += 1
                    if i < len(lines):
                        website = lines[i].strip()
                        if website and not website.startswith('http'):
                            website = 'https://' + website
                        current_school['website'] = website
                    i += 1
                    continue
                
                i += 1
            
            # Add school to list
            schools.append(current_school)
            continue
        
        i += 1
    
    return schools

def infer_co_ed_type(name):
    """Infer co-ed type from school name"""
    name_lower = name.lower()
    if 'boys' in name_lower or 'boy' in name_lower:
        return 'B'
    elif 'girls' in name_lower or 'girl' in name_lower:
        return 'G'
    else:
        return 'C'

def generate_fees_by_grade(board, name):
    """Generate reasonable fees based on board and school type"""
    # Base fees by board
    base_fees = {
        'CBSE': {'12': 350000, '11': 330000, '10': 320000},
        'ICSE': {'12': 380000, '11': 360000, '10': 350000},
        'IB': {'12': 650000, '11': 620000, '10': 600000}
    }
    
    fees = base_fees.get(board, base_fees['CBSE']).copy()
    
    # Adjust based on school name (international, global, etc.)
    name_lower = name.lower()
    if any(word in name_lower for word in ['international', 'global', 'world']):
        for grade in fees:
            fees[grade] = int(fees[grade] * 1.3)
    elif any(word in name_lower for word in ['public', 'army', 'kendriya']):
        for grade in fees:
            fees[grade] = int(fees[grade] * 0.9)
    
    # Add some variation
    variation = random.uniform(0.9, 1.1)
    for grade in fees:
        fees[grade] = int(fees[grade] * variation)
    
    return fees

def generate_rating(board, name):
    """Generate reasonable rating"""
    base_rating = 4.0
    
    # Adjust based on board
    if board == 'IB':
        base_rating = 4.5
    elif board == 'ICSE':
        base_rating = 4.3
    elif board == 'CBSE':
        base_rating = 4.2
    
    # Adjust based on school name
    name_lower = name.lower()
    if any(word in name_lower for word in ['international', 'global', 'world', 'academy']):
        base_rating += 0.2
    if any(word in name_lower for word in ['kendriya', 'army', 'public']):
        base_rating += 0.1
    
    # Add some variation
    rating = base_rating + random.uniform(-0.2, 0.3)
    return round(min(5.0, max(3.5, rating)), 1)

def generate_facilities(board, name):
    """Generate facilities list"""
    # All schools get basic facilities
    facilities = [2, 3, 4, 5]  # Canteen, Library, Sports, Computer Lab
    
    name_lower = name.lower()
    
    # Add AC for most schools
    if random.random() > 0.3:
        facilities.append(1)
    
    # Add Science Lab for most schools
    if random.random() > 0.2:
        facilities.append(6)
    
    # Premium schools get more
    if any(word in name_lower for word in ['international', 'global', 'world', 'academy', 'elite']):
        if random.random() > 0.5:
            facilities.append(7)  # Swimming Pool
        if random.random() > 0.4:
            facilities.append(8)  # Auditorium
    
    return sorted(list(set(facilities)))

def generate_distance():
    """Generate random distance"""
    return round(random.uniform(2.0, 25.0), 1)

def get_curriculum_website(board):
    """Get curriculum website based on board"""
    websites = {
        'CBSE': 'https://www.cbse.gov.in',
        'ICSE': 'https://www.cisce.org',
        'IB': 'https://www.ibo.org'
    }
    return websites.get(board, '')

def get_syllabus(board):
    """Get syllabus name based on board"""
    syllabi = {
        'CBSE': 'CBSE',
        'ICSE': 'ICSE',
        'IB': 'International Baccalaureate'
    }
    return syllabi.get(board, board)

def convert_to_fixture(schools):
    """Convert parsed schools to Django fixture format"""
    fixture = []
    pk = 1
    
    for school in schools:
        fees = generate_fees_by_grade(school['board'], school['name'])
        fees_str = ','.join([f"{grade}:{fee}" for grade, fee in fees.items()])
        
        # Generate grades offered (most schools offer 1-12, IB schools often start from 6)
        if school['board'] == 'IB':
            grades = "6,7,8,9,10,11,12"
        else:
            grades = "1,2,3,4,5,6,7,8,9,10,11,12"
        
        entry = {
            "model": "schools.school",
            "pk": pk,
            "fields": {
                "name": school['name'],
                "location": school['address'] or school['district'],
                "pin_code": school['pin_code'],
                "board": school['board'],
                "grades_offered": grades,
                "co_ed_type": infer_co_ed_type(school['name']),
                "distance": generate_distance(),
                "bus_availability": random.random() > 0.3,  # 70% have bus
                "syllabus": get_syllabus(school['board']),
                "website": school['website'] or "",
                "curriculum_website": get_curriculum_website(school['board']),
                "rating": generate_rating(school['board'], school['name']),
                "fees_by_grade": fees_str,
                "facilities": generate_facilities(school['board'], school['name']),
                "created_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                "updated_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
            }
        }
        fixture.append(entry)
        pk += 1
    
    return fixture

def main():
    """Main function to parse all files and generate fixture"""
    all_schools = []
    
    # Parse CBSE schools
    print("Parsing CBSE schools...")
    cbse_schools = parse_school_file('Schools_info/cbse.md', 'CBSE')
    print(f"Found {len(cbse_schools)} CBSE schools")
    all_schools.extend(cbse_schools)
    
    # Parse IB schools
    print("Parsing IB schools...")
    ib_schools = parse_school_file('Schools_info/Ib.md', 'IB')
    print(f"Found {len(ib_schools)} IB schools")
    all_schools.extend(ib_schools)
    
    # Parse ICSE schools
    print("Parsing ICSE schools...")
    icse_schools = parse_school_file('Schools_info/icse.md', 'ICSE')
    print(f"Found {len(icse_schools)} ICSE schools")
    all_schools.extend(icse_schools)
    
    print(f"\nTotal schools: {len(all_schools)}")
    
    # Convert to fixture format
    print("Converting to fixture format...")
    fixture = convert_to_fixture(all_schools)
    
    # Write to JSON file
    output_file = 'fixtures/schools.json'
    print(f"Writing to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(fixture, f, indent=4, ensure_ascii=False)
    
    print(f"Successfully generated fixture with {len(fixture)} schools!")
    print(f"\nBoard distribution:")
    board_counts = {}
    for school in fixture:
        board = school['fields']['board']
        board_counts[board] = board_counts.get(board, 0) + 1
    for board, count in board_counts.items():
        print(f"  {board}: {count}")

if __name__ == '__main__':
    main()



