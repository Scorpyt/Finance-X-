"""
Validation Utilities for Finance-X Models
Ensures data integrity and constraint enforcement
"""

from typing import Dict


class ValidationError(Exception):
    """Raised when validation fails"""
    pass


def validate_probability(value: float, name: str = "probability") -> float:
    """
    Validate probability value is between 0.0 and 1.0
    
    Args:
        value: Probability value to validate
        name: Name of the field (for error messages)
    
    Returns:
        Validated probability value
    
    Raises:
        ValidationError: If value is not in [0.0, 1.0]
    """
    if not 0.0 <= value <= 1.0:
        raise ValidationError(f"{name} must be between 0.0 and 1.0, got {value}")
    return value


def validate_price(value: float, name: str = "price") -> float:
    """
    Validate price is positive
    
    Args:
        value: Price value to validate
        name: Name of the field (for error messages)
    
    Returns:
        Validated price value
    
    Raises:
        ValidationError: If value is not positive
    """
    if value <= 0:
        raise ValidationError(f"{name} must be positive, got {value}")
    return value


def validate_probability_distribution(dist: Dict[str, float], tolerance: float = 1e-6) -> bool:
    """
    Validate probability distribution sums to 1.0
    
    Args:
        dist: Dictionary of probabilities
        tolerance: Acceptable deviation from 1.0
    
    Returns:
        True if valid
    
    Raises:
        ValidationError: If distribution doesn't sum to 1.0
    """
    total = sum(dist.values())
    if abs(total - 1.0) > tolerance:
        raise ValidationError(
            f"Probability distribution must sum to 1.0, got {total:.6f}. "
            f"Distribution: {dist}"
        )
    return True


def validate_risk_score(score: float) -> float:
    """
    Validate risk score is between 0.0 and 100.0
    
    Args:
        score: Risk score to validate
    
    Returns:
        Validated risk score
    
    Raises:
        ValidationError: If score is not in [0.0, 100.0]
    """
    if not 0.0 <= score <= 100.0:
        raise ValidationError(f"Risk score must be between 0.0 and 100.0, got {score}")
    return score


def validate_percentage(value: float, name: str = "percentage") -> float:
    """
    Validate percentage value (can be negative for losses)
    
    Args:
        value: Percentage value to validate
        name: Name of the field (for error messages)
    
    Returns:
        Validated percentage value
    
    Raises:
        ValidationError: If value is unreasonable (< -100 or > 1000)
    """
    if value < -100 or value > 1000:
        raise ValidationError(
            f"{name} seems unreasonable: {value}%. "
            f"Expected range: -100% to 1000%"
        )
    return value


def validate_quantity(value: float, name: str = "quantity") -> float:
    """
    Validate quantity is non-negative
    
    Args:
        value: Quantity value to validate
        name: Name of the field (for error messages)
    
    Returns:
        Validated quantity value
    
    Raises:
        ValidationError: If value is negative
    """
    if value < 0:
        raise ValidationError(f"{name} cannot be negative, got {value}")
    return value
