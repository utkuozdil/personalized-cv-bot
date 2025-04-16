import pytest
from src.utility.email_format_util import get_confirm_response, get_mail_template

def test_get_confirm_response():
    # Test data
    item = {
        'email': 'test@example.com'
    }

    # Test the method
    response = get_confirm_response(item)

    # Verify the result
    assert response['statusCode'] == 200
    assert 'text/html' in response['headers']['Content-Type']
    assert 'test@example.com' in response['body']

def test_get_mail_template():
    # Test data
    email = 'test@example.com'
    filename = 'test.pdf'
    confirm_link = 'https://example.com/confirm'

    # Test the method
    html = get_mail_template(email, filename, confirm_link)

    # Verify the result
    assert email in html
    assert filename in html
    assert confirm_link in html

def test_get_mail_template_special_characters():
    # Test data with special characters
    email = 'test+special@example.com'
    filename = 'resume (2024).pdf'
    confirm_link = 'https://example.com/confirm?token=abc123'

    # Test the method
    html = get_mail_template(email, filename, confirm_link)

    # Verify the result
    assert email in html
    assert filename in html
    assert confirm_link in html

def test_get_confirm_response_special_characters():
    # Test data with special characters
    item = {
        'email': 'test+special@example.com'
    }

    # Test the method
    response = get_confirm_response(item)

    # Verify the result
    assert response['statusCode'] == 200
    assert 'test+special@example.com' in response['body']

def test_get_mail_template_html_structure():
    # Test data
    email = 'test@example.com'
    filename = 'test.pdf'
    confirm_link = 'https://example.com/confirm'

    # Test the method
    html = get_mail_template(email, filename, confirm_link)

    # Verify HTML structure
    assert '<!DOCTYPE html>' in html
    assert '<html' in html
    assert '<head>' in html
    assert '<body>' in html
    assert '</html>' in html

def test_get_confirm_response_html_structure():
    # Test data
    item = {
        'email': 'test@example.com'
    }

    # Test the method
    response = get_confirm_response(item)

    # Verify HTML structure
    assert '<!DOCTYPE html>' in response['body']
    assert '<html' in response['body']
    assert '<head>' in response['body']
    assert '<body>' in response['body']
    assert '</html>' in response['body'] 