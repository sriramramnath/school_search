from django.db import models


class Curriculum(models.Model):
    """Curriculum information (IGCSE, IB, CBSE, etc.)"""
    name = models.CharField(max_length=100)
    abbreviation = models.CharField(max_length=20, blank=True, help_text="e.g., IB, IGCSE")
    description = models.TextField(blank=True)
    subjects = models.TextField(help_text="Comma-separated list of subjects")
    exams = models.TextField(blank=True, help_text="Information about exams")
    info = models.TextField(blank=True, help_text="Additional information")
    website = models.URLField(blank=True)
    wikipedia_page = models.CharField(max_length=200, blank=True, help_text="Wikipedia page title (optional, auto-detected if blank)")
    
    def __str__(self):
        return self.name or self.abbreviation
    
    def get_subjects_list(self):
        """Return subjects as a list"""
        return [s.strip() for s in self.subjects.split(',') if s.strip()]
    
    def get_absolute_url(self):
        """Get absolute URL for curriculum detail page"""
        from django.urls import reverse
        return reverse('curriculum_detail', args=[str(self.id)])
    
    class Meta:
        verbose_name_plural = "Curricula"
