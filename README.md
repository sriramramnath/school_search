# School Search - Django Application

A Django web application for searching schools in India with a unique hand-drawn/notebook UI style. The application is designed primarily for mobile devices but is fully responsive for desktop use.

## Features

- **School Search & Filtering**: Comprehensive search with multiple filters including:
  - School name
  - Board (IGCSE, CBSE, IB, ICSE, State Board)
  - Grade level
  - Co-education type (Boys, Girls, Co-ed)
  - Location (Pin code) and distance
  - Bus availability
  - Fees range
  - Facilities
  - Review ratings

- **School Detail Pages**: Detailed information about each school including:
  - Ratings and reviews
  - Facilities
  - Fees by grade
  - Location and transport information
  - Website links

- **Curriculum Search**: Search and browse information about different curricula (IB, IGCSE, CBSE, ICSE)

- **User Profile**: Basic profile management (ready for future authentication)

- **Hand-drawn UI**: Unique notebook-style interface using Rough.js for hand-drawn effects

## Technology Stack

- **Backend**: Django 4.2+
- **Database**: SQLite (easily migratable to Supabase or MongoDB)
- **Frontend**: HTML5, CSS3, JavaScript
- **UI Library**: Rough.js for hand-drawn effects
- **Fonts**: Google Fonts (Kalam, Caveat)

## Installation

1. **Clone the repository** (or navigate to the project directory)

2. **Create and activate a virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**:
   ```bash
   python manage.py migrate
   ```

5. **Load sample data**:
   ```bash
   python manage.py loaddata fixtures/facilities.json
   python manage.py loaddata fixtures/schools.json
   python manage.py loaddata fixtures/reviews.json
   python manage.py loaddata fixtures/curricula.json
   ```

6. **Create a superuser** (optional, for admin access):
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server**:
   ```bash
   python manage.py runserver
   ```

8. **Access the application**:
   - Main site: http://127.0.0.1:8000/
   - Admin panel: http://127.0.0.1:8000/admin/

## Project Structure

```
School Search/
├── accounts/          # User profile app
├── curriculum/        # Curriculum search app
├── schools/           # Main school search app
├── schoolsearch/      # Django project settings
├── templates/         # HTML templates
├── static/           # CSS, JS, and images
│   ├── css/
│   └── js/
├── fixtures/         # Sample data JSON files
├── media/            # User uploads (school images)
└── manage.py         # Django management script
```

## Usage

### Searching Schools

1. Navigate to the **Search** page from the navigation bar
2. Use the filter panel on the left to refine your search:
   - Enter school name
   - Select board, grade, and co-ed type
   - Set location (pin code) and maximum distance
   - Filter by bus availability, fees range, facilities, and ratings
3. Results appear on the right side
4. Click on any school card to view detailed information

### Viewing School Details

- Click on any school card from the search results or home page
- View comprehensive information including:
  - Ratings and review breakdown
  - Individual reviews
  - Available facilities
  - Fees by grade level
  - Contact and website information

### Curriculum Search

- Navigate to **Curriculum** from the navigation bar
- Search for curriculum information (IB, IGCSE, CBSE, ICSE)
- View details about subjects, exams, and official websites

## Data Models

### School
- Basic information (name, location, pin code)
- Academic details (board, syllabus, grades offered)
- Fees (stored by grade)
- Facilities (many-to-many relationship)
- Ratings and reviews

### Facility
- Name and icon
- Linked to schools via many-to-many relationship

### Review
- Rating (1-5 stars)
- Comment
- Reviewer information
- Verification status

### Curriculum
- Name and abbreviation
- Description and subjects
- Exam information
- Official website

## Future Enhancements

- **Database Migration**: Ready to migrate to Supabase or MongoDB
- **User Authentication**: Full user account system
- **AI School Picker**: Coming soon feature for personalized recommendations
- **Favorites**: Save favorite schools
- **Advanced Filtering**: More sophisticated search algorithms
- **School Comparisons**: Compare multiple schools side-by-side

## Development Notes

- The application uses SQLite by default for easy local development
- Models are structured to be easily exportable to JSON for database migration
- The hand-drawn UI is implemented using Rough.js library
- Mobile-first responsive design with breakpoints for tablet and desktop
- All static files are served through Django's static file system

## License

This project is open source and available for educational purposes.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.








