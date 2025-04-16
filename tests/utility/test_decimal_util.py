import pytest
from decimal import Decimal
from src.utility.decimal_util import clean_decimals

def test_clean_decimals_dict_to_decimal():
    # Test data
    test_dict = {
        'int_value': 42,
        'float_value': 3.14,
        'string_value': 'test',
        'nested': {
            'int_value': 100,
            'float_value': 2.718
        }
    }
    
    # Test the method
    result = clean_decimals(test_dict, to_decimal=True)
    
    # Verify the result
    assert isinstance(result['int_value'], Decimal)
    assert isinstance(result['float_value'], Decimal)
    assert isinstance(result['string_value'], str)
    assert isinstance(result['nested']['int_value'], Decimal)
    assert isinstance(result['nested']['float_value'], Decimal)
    assert result['int_value'] == Decimal('42')
    assert result['float_value'] == Decimal('3.14')
    assert result['string_value'] == 'test'
    assert result['nested']['int_value'] == Decimal('100')
    assert result['nested']['float_value'] == Decimal('2.718')

def test_clean_decimals_dict_to_float():
    # Test data
    test_dict = {
        'decimal_value': Decimal('42.5'),
        'string_value': 'test',
        'nested': {
            'decimal_value': Decimal('100.75')
        }
    }
    
    # Test the method
    result = clean_decimals(test_dict, to_decimal=False)
    
    # Verify the result
    assert isinstance(result['decimal_value'], float)
    assert isinstance(result['string_value'], str)
    assert isinstance(result['nested']['decimal_value'], float)
    assert result['decimal_value'] == 42.5
    assert result['string_value'] == 'test'
    assert result['nested']['decimal_value'] == 100.75

def test_clean_decimals_list():
    # Test data
    test_list = [42, 3.14, 'test', {'value': Decimal('100.5')}]
    
    # Test the method
    result = clean_decimals(test_list, to_decimal=True)
    
    # Verify the result
    assert isinstance(result[0], Decimal)
    assert isinstance(result[1], Decimal)
    assert isinstance(result[2], str)
    assert isinstance(result[3]['value'], Decimal)
    assert result[0] == Decimal('42')
    assert result[1] == Decimal('3.14')
    assert result[2] == 'test'
    assert result[3]['value'] == Decimal('100.5')

def test_clean_decimals_primitive_values():
    # Test primitive values
    assert clean_decimals(42, to_decimal=True) == Decimal('42')
    assert clean_decimals(3.14, to_decimal=True) == Decimal('3.14')
    assert clean_decimals('test', to_decimal=True) == 'test'
    assert clean_decimals(Decimal('42.5'), to_decimal=False) == 42.5
    assert clean_decimals(None, to_decimal=True) is None 