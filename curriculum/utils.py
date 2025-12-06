"""Utility functions for curriculum Wikipedia integration"""
try:
    import wikipedia
    WIKIPEDIA_AVAILABLE = True
except ImportError:
    WIKIPEDIA_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

from typing import Dict, Optional
import re
from django.core.cache import cache


def clean_html(text: str) -> str:
    """Remove HTML tags from text"""
    if not text:
        return ""
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Clean up whitespace
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def get_wikipedia_data(page_title: Optional[str] = None, search_term: Optional[str] = None) -> Optional[Dict]:
    """
    Fetch data from Wikipedia with caching
    
    Args:
        page_title: Exact Wikipedia page title
        search_term: Search term to find Wikipedia page
    
    Returns:
        Dictionary with Wikipedia data or None if not found
    """
    if not WIKIPEDIA_AVAILABLE:
        return None
    
    # Create cache key
    cache_key = f"wikipedia_{page_title or search_term or 'none'}"
    
    # Try to get from cache first
    cached_data = cache.get(cache_key)
    if cached_data is not None:
        return cached_data
    
    try:
        # Set language to English
        wikipedia.set_lang("en")
        
        # Try to get the page
        if page_title:
            try:
                page = wikipedia.page(page_title, auto_suggest=False)
            except wikipedia.DisambiguationError as e:
                # If disambiguation, try first option
                page = wikipedia.page(e.options[0])
            except wikipedia.PageError:
                return None
        elif search_term:
            # Search for the page
            search_results = wikipedia.search(search_term, results=1)
            if not search_results:
                return None
            try:
                page = wikipedia.page(search_results[0], auto_suggest=False)
            except (wikipedia.DisambiguationError, wikipedia.PageError):
                return None
        else:
            return None
        
        # Extract summary
        summary = page.summary
        # Limit summary length
        if len(summary) > 500:
            summary = summary[:500] + "..."
        
        # Get full content (first few sections)
        content = page.content
        # Get first few paragraphs
        paragraphs = content.split('\n\n')[:5]
        full_content = '\n\n'.join([p for p in paragraphs if p.strip() and not p.startswith('==')])
        
        # Limit full content
        if len(full_content) > 2000:
            full_content = full_content[:2000] + "..."
        
        # Get images if available
        images = page.images[:3] if page.images else []
        
        result = {
            'title': page.title,
            'url': page.url,
            'summary': clean_html(summary),
            'content': clean_html(full_content),
            'images': images,
            'page_url': page.url,
        }
        
        # Cache for 24 hours (86400 seconds)
        cache.set(cache_key, result, 86400)
        return result
    
    except Exception as e:
        print(f"Error fetching Wikipedia data: {e}")
        return None


def search_wikipedia_page_title(curriculum_name: str, abbreviation: str = "") -> Optional[str]:
    """
    Search for Wikipedia page title for a curriculum
    
    Args:
        curriculum_name: Full name of curriculum
        abbreviation: Abbreviation (e.g., IB, IGCSE)
    
    Returns:
        Wikipedia page title or None
    """
    if not WIKIPEDIA_AVAILABLE:
        return None
    
    try:
        wikipedia.set_lang("en")
        
        # Try with full name first
        search_term = curriculum_name
        if abbreviation:
            # Also try with abbreviation
            search_terms = [f"{curriculum_name} ({abbreviation})", abbreviation, curriculum_name]
        else:
            search_terms = [curriculum_name]
        
        for term in search_terms:
            try:
                results = wikipedia.search(term, results=1)
                if results:
                    page = wikipedia.page(results[0], auto_suggest=False)
                    return page.title
            except:
                continue
        
        return None
    except Exception as e:
        print(f"Error searching Wikipedia: {e}")
        return None

