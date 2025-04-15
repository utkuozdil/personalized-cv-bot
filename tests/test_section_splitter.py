import pytest
from dotenv import load_dotenv

from src.utility.section_classifier import split_by_section

# Load environment variables (for OpenAI API key, etc.)
load_dotenv()


@pytest.fixture
def extracted_text():
    with open("tests/test_extracted.txt", "r") as f:
        return f.read()

def test_split_by_section(extracted_text):
    sections = split_by_section(extracted_text)

    # Print all detected sections
    for section, content in sections.items():
        print(f"\n[{section}]\n{content[:300]}...\n")

    # ✅ Assert known sections were found
    assert any(s in sections for s in ["Education", "Skills", "Work Experience"]), "Expected section not found."
    assert len(sections) > 1, "Too few sections parsed."

    # ✅ Specific fuzzy match test: "Kills" → "Skills"
    matched_skills = "Skills" in sections
    assert matched_skills, "'Kills' was not correctly classified as 'Skills'"
