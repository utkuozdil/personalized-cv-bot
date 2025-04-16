from decimal import Decimal


def clean_decimals(obj, to_decimal=True):
    """
    Clean decimal values in an object.
    
    Args:
        obj: The object to clean
        to_decimal: If True, convert float/int to Decimal (for DynamoDB).
                   If False, convert Decimal to float (for JSON responses).
    """
    if isinstance(obj, dict):
        return {k: clean_decimals(v, to_decimal) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_decimals(i, to_decimal) for i in obj]
    elif to_decimal and isinstance(obj, (int, float)):
        return Decimal(str(obj))
    elif not to_decimal and isinstance(obj, Decimal):
        return float(obj)
    return obj