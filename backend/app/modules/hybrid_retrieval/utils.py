"""Utility functions for hybrid retrieval."""

import re
from typing import List, Dict, Any, Optional, Set
from datetime import datetime
from app.core.logging import setup_logging

logger = setup_logging()


def normalize_text(text: str) -> str:
    """Normalize text for comparison.
    
    Args:
        text: Text to normalize
        
    Returns:
        Normalized text
    """
    # Convert to lowercase
    text = text.lower()
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters (keep alphanumeric and spaces)
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    
    return text.strip()


def extract_keywords(text: str, min_length: int = 3) -> List[str]:
    """Extract keywords from text.
    
    Args:
        text: Text to extract keywords from
        min_length: Minimum keyword length
        
    Returns:
        List of keywords
    """
    # Tokenize
    words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
    
    # Filter by length and remove common stop words
    stop_words = {
        'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
        'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
        'should', 'may', 'might', 'must', 'shall', 'can', 'need', 'dare',
        'how', 'what', 'where', 'when', 'why', 'who', 'which', 'that',
        'this', 'these', 'those', 'it', 'its', 'they', 'them', 'their',
        'for', 'of', 'with', 'at', 'by', 'from', 'in', 'on', 'to', 'into',
        'through', 'during', 'before', 'after', 'above', 'below', 'between',
        'under', 'again', 'further', 'then', 'once', 'and', 'or', 'but', 'if'
    }
    
    keywords = [word for word in words if len(word) >= min_length and word not in stop_words]
    
    # Remove duplicates while preserving order
    seen = set()
    unique_keywords = []
    for word in keywords:
        if word not in seen:
            seen.add(word)
            unique_keywords.append(word)
    
    return unique_keywords


def calculate_text_similarity(text1: str, text2: str) -> float:
    """Calculate similarity between two texts using Jaccard similarity.
    
    Args:
        text1: First text
        text2: Second text
        
    Returns:
        Similarity score (0-1)
    """
    # Extract keywords
    keywords1 = set(extract_keywords(text1))
    keywords2 = set(extract_keywords(text2))
    
    if not keywords1 or not keywords2:
        return 0.0
    
    # Calculate Jaccard similarity
    intersection = len(keywords1 & keywords2)
    union = len(keywords1 | keywords2)
    
    return intersection / union if union > 0 else 0.0


def format_timestamp(timestamp: Optional[str]) -> str:
    """Format timestamp for display.
    
    Args:
        timestamp: ISO format timestamp
        
    Returns:
        Formatted timestamp string
    """
    if not timestamp:
        return "N/A"
    
    try:
        dt = datetime.fromisoformat(timestamp)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return timestamp


def truncate_text(text: str, max_length: int = 200, suffix: str = "...") -> str:
    """Truncate text to maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def merge_dicts(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    """Merge multiple dictionaries.
    
    Args:
        *dicts: Dictionaries to merge
        
    Returns:
        Merged dictionary
    """
    result = {}
    for d in dicts:
        result.update(d)
    return result


def flatten_dict(d: Dict[str, Any], parent_key: str = "", sep: str = ".") -> Dict[str, Any]:
    """Flatten nested dictionary.
    
    Args:
        d: Dictionary to flatten
        parent_key: Parent key for nested items
        sep: Separator for keys
        
    Returns:
        Flattened dictionary
    """
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safely divide two numbers.
    
    Args:
        numerator: Numerator
        denominator: Denominator
        default: Default value if division fails
        
    Returns:
        Division result or default
    """
    try:
        if denominator == 0:
            return default
        return numerator / denominator
    except:
        return default


def calculate_percentile(values: List[float], percentile: float) -> float:
    """Calculate percentile of values.
    
    Args:
        values: List of values
        percentile: Percentile to calculate (0-100)
        
    Returns:
        Percentile value
    """
    if not values:
        return 0.0
    
    sorted_values = sorted(values)
    n = len(sorted_values)
    
    if percentile <= 0:
        return sorted_values[0]
    elif percentile >= 100:
        return sorted_values[-1]
    
    index = (percentile / 100) * (n - 1)
    lower = int(index)
    upper = lower + 1
    
    if upper >= n:
        return sorted_values[lower]
    
    weight = index - lower
    return sorted_values[lower] * (1 - weight) + sorted_values[upper] * weight


def format_duration_ms(duration_ms: float) -> str:
    """Format duration in milliseconds to human-readable string.
    
    Args:
        duration_ms: Duration in milliseconds
        
    Returns:
        Formatted duration string
    """
    if duration_ms < 1000:
        return f"{duration_ms:.2f}ms"
    elif duration_ms < 60000:
        return f"{duration_ms / 1000:.2f}s"
    else:
        minutes = duration_ms / 60000
        return f"{minutes:.2f}min"


def validate_query(query: str) -> bool:
    """Validate query string.
    
    Args:
        query: Query to validate
        
    Returns:
        True if valid
    """
    if not query or not query.strip():
        return False
    
    if len(query) < 3:
        return False
    
    if len(query) > 1000:
        return False
    
    return True


def sanitize_query(query: str) -> str:
    """Sanitize query string.
    
    Args:
        query: Query to sanitize
        
    Returns:
        Sanitized query
    """
    # Remove potentially harmful characters
    query = re.sub(r'[<>"\']', '', query)
    
    # Trim whitespace
    query = query.strip()
    
    return query


def extract_entity_ids(query_analysis: Optional[Any]) -> List[str]:
    """Extract entity IDs from query analysis.
    
    Args:
        query_analysis: Query analysis result
        
    Returns:
        List of entity IDs
    """
    if not query_analysis:
        return []
    
    entity_ids = []
    for entity in query_analysis.detected_entities:
        if entity.entity_id:
            entity_ids.append(entity.entity_id)
    
    return entity_ids


def build_filter_dict(
    equipment: Optional[str] = None,
    document_type: Optional[str] = None,
    entity_type: Optional[str] = None,
    department: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """Build filter dictionary from parameters.
    
    Args:
        equipment: Equipment filter
        document_type: Document type filter
        entity_type: Entity type filter
        department: Department filter
        **kwargs: Additional filters
        
    Returns:
        Filter dictionary
    """
    filters = {}
    
    if equipment:
        filters['equipment'] = equipment
    if document_type:
        filters['document_type'] = document_type
    if entity_type:
        filters['entity_type'] = entity_type
    if department:
        filters['department'] = department
    
    filters.update(kwargs)
    
    return filters


def log_retrieval_step(step: str, duration_ms: float, details: Optional[Dict[str, Any]] = None):
    """Log retrieval step with timing.
    
    Args:
        step: Step name
        duration_ms: Duration in milliseconds
        details: Additional details
    """
    message = f"{step} completed in {format_duration_ms(duration_ms)}"
    
    if details:
        message += f" - {details}"
    
    logger.info(message)


def calculate_confidence_interval(
    values: List[float],
    confidence: float = 0.95
) -> tuple:
    """Calculate confidence interval for values.
    
    Args:
        values: List of values
        confidence: Confidence level (0-1)
        
    Returns:
        Tuple of (lower_bound, upper_bound)
    """
    if not values:
        return (0.0, 0.0)
    
    import statistics
    
    mean = statistics.mean(values)
    stdev = statistics.stdev(values) if len(values) > 1 else 0
    
    # Simple approximation using standard deviation
    # For production, use proper statistical methods
    z_score = 1.96  # For 95% confidence
    margin_of_error = z_score * (stdev / (len(values) ** 0.5))
    
    lower = max(0, mean - margin_of_error)
    upper = min(1, mean + margin_of_error)
    
    return (lower, upper)
