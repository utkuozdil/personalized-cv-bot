from dotenv import load_dotenv
import pytest
import os
from src.integrations.openai import OpenAIIntegration
from src.utility.prompt_util import get_summary_prompt

load_dotenv()

data = """
Muammer Utku Ozdil
Senior Software Engineer
Ankara, Turkey +90 542 344 14 86 utkuozdil@gmail.com [LinkedIn or GitHub URL]
Professional Summary
Results-driven Senior Software Engineer with over 8 years of experience designing and implementing scalable, cloud-native
solutions. Proven expertise in Python, AWS, and serverless technologies, with a strong ability to solve complex technical
problems, drive innovation, and deliver business value across remote, cross-functional teams.
Skills
Languages: Python, Java, JavaScript
Cloud: AWS (Lambda, API Gateway, S3, RDS, IoT Core, DynamoDB)
Databases: PostgreSQL, DB2, DynamoDB
Tools & Frameworks: React, Spring, Serverless Framework, CloudFormation, Terraform, Docker, Jenkins
Soft Skills: Cross-functional collaboration, stakeholder communication, remote team experience
Experience
Senior Software Engineer | Staircase Remote
Feb 2021 Aug 2024
- Accelerated mortgage processing by reducing bottlenecks through scalable, cloud-native APIs built with Python and AWS,
resulting in improved customer satisfaction and reduced costs.
- Eliminated delays in third-party integration by standardizing data exchange across 20+ partners, reducing onboarding time
and ensuring seamless communication across XML, JSON, and HTML formats.
- Increased operational efficiency by consolidating fragmented systems into a unified mortgage boarding platform that surfaced
enriched loan data for faster decision-making.
- Enabled faster partner integration without requiring custom APIs by implementing a configuration-based onboarding solution
using AWS CloudFormation and proxy APIs.
Software Engineer | Arcelik Ankara
Apr 2020 Feb 2021
- Solved real-time communication issues between IoT devices and mobile apps by introducing a cloud-native messaging
ecosystem using Java, Python, and AWS, improving system responsiveness.
Software Engineer | Central Bank of the Republic of Turkey Ankara
Dec 2017 Apr 2020
- Streamlined accounting processes by building reliable internal applications using Java 8, Spring, and React, reducing task
complexity and improving data accuracy.
- Boosted data processing efficiency by utilizing Java Stream API to replace legacy batch operations, cutting execution time
and system load.
Software Engineer | Ming Software Ankara
Aug 2015 Nov 2017
- Delivered a centralized web platform for law firms using Java and PostgreSQL, streamlining legal workflows, automating
manual processes, and improving operational efficiency.
Education
Bachelor's Degree in Computer Science
Hacettepe University Ankara
2010 2015"""

@pytest.fixture(scope="module")
def openai_integration():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OPENAI_API_KEY not set in environment.")
    return OpenAIIntegration()

def test_streaming_mode(openai_integration):
    summary_messages = get_summary_prompt(data)
    
    try:
        # Use streaming mode
        result = openai_integration.stream_to_string(summary_messages, stream=False)
        
        print("\n[✅] Streaming result:\n", result)
        
        assert isinstance(result, str)
        assert len(result) > 10  # Shouldn't be empty
    except Exception as e:
        print("\n[❌] Error occurred:", str(e))
        raise