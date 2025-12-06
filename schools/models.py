from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Facility(models.Model):
    """Facilities available at schools (AC, Canteen, Library, etc.)"""
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, blank=True, help_text="Icon name or emoji")
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Facilities"


class School(models.Model):
    """School model with all relevant information"""
    
    BOARD_CHOICES = [
        ('IGCSE', 'IGCSE'),
        ('CBSE', 'CBSE'),
        ('IB', 'International Baccalaureate'),
        ('ICSE', 'ICSE'),
        ('State', 'State Board'),
    ]
    
    CO_ED_CHOICES = [
        ('B', 'Boys'),
        ('G', 'Girls'),
        ('C', 'Co-ed'),
    ]
    
    name = models.CharField(max_length=200, db_index=True)
    location = models.CharField(max_length=200, db_index=True)
    pin_code = models.CharField(max_length=10, db_index=True)
    board = models.CharField(max_length=50, choices=BOARD_CHOICES, db_index=True)
    grades_offered = models.CharField(max_length=100, db_index=True, help_text="Comma-separated grades (e.g., '1,2,3,4,5,6,7,8,9,10,11,12')")
    co_ed_type = models.CharField(max_length=1, choices=CO_ED_CHOICES, default='C')
    distance = models.DecimalField(max_digits=5, decimal_places=2, db_index=True, help_text="Distance in km")
    bus_availability = models.BooleanField(default=False, db_index=True)
    syllabus = models.CharField(max_length=100)
    website = models.URLField(blank=True)
    curriculum_website = models.URLField(blank=True)
    rating = models.DecimalField(
        max_digits=3, 
        decimal_places=1, 
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        default=0.0,
        db_index=True
    )
    image = models.ImageField(upload_to='schools/', blank=True, null=True)
    
    # Fees stored as JSON-like string or separate model
    # For simplicity, storing as text field with format: "grade:fee,grade:fee"
    fees_by_grade = models.TextField(
        blank=True, 
        help_text="Format: '12:400000,11:380000' for grade 12: ₹400000, grade 11: ₹380000"
    )
    
    facilities = models.ManyToManyField(Facility, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    def get_fee_for_grade(self, grade=12):
        """Get fee for a specific grade (defaults to grade 12)"""
        if not self.fees_by_grade:
            return None
        fee_dict = {}
        for item in self.fees_by_grade.split(','):
            if ':' in item:
                g, f = item.split(':')
                fee_dict[g.strip()] = int(f.strip())
        return fee_dict.get(str(grade))
    
    def get_default_fee(self):
        """Get default fee (preferably grade 12, otherwise first available)"""
        if not self.fees_by_grade:
            return None
        fee_dict = {}
        for item in self.fees_by_grade.split(','):
            if ':' in item:
                g, f = item.split(':')
                fee_dict[g.strip()] = int(f.strip())
        # Try grade 12 first, then any available
        if fee_dict:
            return fee_dict.get('12') or list(fee_dict.values())[0]
        return None
    
    class Meta:
        ordering = ['-rating', 'name']


class Review(models.Model):
    """Reviews for schools"""
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 to 5 stars"
    )
    comment = models.TextField(blank=True)
    reviewer_name = models.CharField(max_length=100)
    verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.reviewer_name} - {self.school.name} - {self.rating}★"
    
    class Meta:
        ordering = ['-created_at']
