import os
import sys
import pytest
from dotenv import load_dotenv

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Load environment variables from .env file
load_dotenv()

@pytest.fixture(scope="session")
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'

@pytest.fixture(scope="session")
def test_bucket_name():
    """Return the test bucket name."""
    return "test-bucket"

@pytest.fixture(scope="session")
def test_table_name():
    """Return the test DynamoDB table name."""
    return "test-table"

@pytest.fixture(scope="session")
def sample_resume_text():
    """Return a sample resume text for testing."""
    return """
    John Doe
    Senior Software Engineer
    john.doe@example.com
    
    Experience:
    - Company A (2020-2023)
      - Led development of cloud-native applications
      - Implemented microservices architecture
    
    Skills:
    - Python, AWS, Docker
    - Microservices, REST APIs
    """

@pytest.fixture(scope="session")
def sample_chat_messages():
    """Return sample chat messages for testing."""
    return [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Tell me about my experience."},
        {"role": "assistant", "content": "Based on your resume..."}
    ] 