import pytest
from src.utility.text_divider import chunk_text

def test_chunk_text_basic():
    # Test data
    text = "This is a test sentence. This is another test sentence."
    
    # Test the method
    chunks = chunk_text(text, max_words=4, overlap=0)
    
    # Verify the result
    assert len(chunks) == 3
    assert chunks[0] == "This is a test"
    assert chunks[1] == "sentence. This is another"
    assert chunks[2] == "test sentence."

def test_chunk_text_with_overlap():
    # Test data
    text = "This is a test sentence. This is another test sentence."
    
    # Test the method with small max_words to force multiple chunks
    chunks = chunk_text(text, max_words=4, overlap=2)
    
    # Verify the result
    assert len(chunks) == 3
    assert "This is a test" in chunks[0]
    assert "test sentence. This" in chunks[1]
    assert "another test sentence" in chunks[2]

def test_chunk_text_empty():
    # Test empty text
    text = ""
    
    # Test the method
    chunks = chunk_text(text, max_words=4, overlap=0)
    
    # Verify the result
    assert len(chunks) == 0

def test_chunk_text_single_line():
    # Test single line text
    text = "This is a single line of text that should be chunked."
    
    # Test the method with small max_words to force multiple chunks
    chunks = chunk_text(text, max_words=4, overlap=0)
    
    # Verify the result
    assert len(chunks) == 3
    assert "This is a single" in chunks[0]
    assert "line of text that" in chunks[1]
    assert "should be chunked." in chunks[2]

def test_chunk_text_multiple_lines():
    # Test multiple lines text
    text = """First line of text.
    Second line of text.
    Third line of text."""
    
    # Test the method with small max_words to force multiple chunks
    chunks = chunk_text(text, max_words=4, overlap=0)
    
    # Verify the result
    assert len(chunks) == 3
    assert "First line" in chunks[0]
    assert "Second line" in chunks[1]
    assert "Third line" in chunks[2]

def test_chunk_text_with_bullet_points():
    # Test text with bullet points
    text = """• First bullet point
    • Second bullet point
    • Third bullet point"""
    
    # Test the method with small max_words to force multiple chunks
    chunks = chunk_text(text, max_words=4, overlap=0)
    
    # Verify the result
    assert len(chunks) == 3
    assert "First bullet" in chunks[0]
    assert "Second bullet" in chunks[1]
    assert "Third bullet" in chunks[2]

def test_chunk_text_large_overlap():
    # Test with large overlap
    text = "This is a test sentence with multiple words."
    
    # Test the method with small max_words to force multiple chunks
    chunks = chunk_text(text, max_words=4, overlap=3)
    
    # Verify the result
    assert len(chunks) == 2
    assert "This is a test" in chunks[0]
    assert "test sentence with multiple words" in chunks[1] 