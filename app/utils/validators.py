import re
from typing import Optional

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_phone(phone: str) -> bool:
    """
    Validate Australian phone number
    Accepts formats:
    - 0412345678 (mobile)
    - 0212345678 (landline)
    - +61412345678 (international mobile)
    - +61212345678 (international landline)
    """
    # Remove spaces, dashes, and parentheses
    phone = re.sub(r'[\s\-\(\)]', '', phone)
    
    # Check for valid Australian phone number patterns
    # Mobile: 04XX XXX XXX or +614XX XXX XXX
    # Landline: 0[2378] XXXX XXXX or +61[2378] XXXX XXXX
    mobile_pattern = r'^(\+61|0)4\d{8}$'
    landline_pattern = r'^(\+61|0)[2378]\d{8}$'
    
    return bool(re.match(mobile_pattern, phone) or re.match(landline_pattern, phone))

def validate_postcode(postcode: str) -> bool:
    """Validate Australian postcode (4 digits)"""
    pattern = r'^\d{4}$'
    return bool(re.match(pattern, postcode))

def validate_password_strength(password: str) -> tuple[bool, Optional[str]]:
    """
    Validate password strength
    
    Requirements:
    - At least 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    
    Returns:
        (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"
    
    return True, None

def format_phone_for_display(phone: str) -> str:
    """Format phone number for display"""
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', phone)
    
    # Handle Australian format
    if digits.startswith('61'):
        # International format: +61 4XX XXX XXX
        if len(digits) == 11 and digits[2] == '4':
            return f"+61 {digits[2:5]} {digits[5:8]} {digits[8:]}"
        # Landline: +61 2 XXXX XXXX
        elif len(digits) == 11:
            return f"+61 {digits[2]} {digits[3:7]} {digits[7:]}"
    elif digits.startswith('0'):
        # Mobile: 04XX XXX XXX
        if len(digits) == 10 and digits[1] == '4':
            return f"{digits[0:4]} {digits[4:7]} {digits[7:]}"
        # Landline: 02 XXXX XXXX
        elif len(digits) == 10:
            return f"{digits[0:2]} {digits[2:6]} {digits[6:]}"
    
    return phone  # Return as-is if format not recognized

def normalize_phone(phone: str) -> str:
    """Normalize phone number to consistent format for storage"""
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', phone)
    
    # Convert international format to local format
    if digits.startswith('61'):
        return '0' + digits[2:]
    
    return digits
