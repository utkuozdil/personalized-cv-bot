import json
import textwrap

def get_resume_prompt(prompt: str, history: list, context: str = "") -> list:
    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful assistant answering questions about a candidate's resume.\n"
                "Use the provided resume context to answer clearly and accurately.\n\n"
                f"Resume context:\n{context.strip()}"
            )
        }
    ]

    # Add past messages
    if history:
        messages.extend(history)

    return messages

def get_main_rag_content(name, resume_text, question):
    return (
        "You are a helpful assistant reading a resume. "
        f"The candidate's name is {name}. "
        "Based on the text below, answer the question clearly using the candidate's name.\n\n"
        f"Resume:\n{resume_text}\n\n"
        f"Question: {question}"
    )

def get_rerank_prompt(question, context):
    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful assistant selecting the most relevant resume chunks for a question. "
                "Given a question and some numbered text chunks, return a JSON list of the best chunk indexes. "
                "Choose no more than 3 chunks. Format: {\"chunks\": [0, 2]}"
            )
        },
        {
            "role": "user",
            "content": f"Question: {question}\n\nChunks:\n{context}"
        }
    ]
    return messages


    return [
        {
            "role": "system",
            "content": (
                "You're a friendly and professional AI resume reviewer.\n"
                "Given the resume analysis data, generate a personalized first message.\n"
                "Summarize key impressions and scores clearly, mention strengths and suggestions casually.\n"
                "End with an inviting phrase like: 'Ready when you are to dive deeper!'"
            )
        },
        {
            "role": "user",
            "content": json.dumps({
                "summary": summary,
                "score": score,
                "category_scores": category_scores,
                "feedback": feedback
            }, indent=2)
        }
    ]

def get_combined_first_message_prompt(resume_text):
    prompt_content = textwrap.dedent(f"""
        Here is the candidate's resume:

        \"\"\"{resume_text}\"\"\"

        Please analyze it and respond in the following structure:

        👋 **Greeting**  
        Welcome the user and explain that you've reviewed their resume.

        📝 **Summary of Candidate**  
        Summarize their experience and background in 2–3 sentences.

        🎯 **Suggested Job Roles**  
        List 2–3 job roles or titles that align with their skills and experience.

        🛠️ **Resume Improvement Tips**  
        Provide 3 tailored suggestions to make their resume more effective for the most relevant job role.

        📌 **Style Guidelines**
        - Use a friendly, supportive tone.
        - Format with emojis and bullet points for clarity.
        - Keep it concise and relevant to job seekers.
        - Do NOT repeat the resume text.
    """)

    return [
        {
            "role": "system",
            "content": (
                "You are a helpful, friendly, and professional AI career assistant. "
                "You analyze resumes and provide clear, structured, and motivational feedback for job seekers."
            )
        },
        {
            "role": "user",
            "content": prompt_content
        }
    ]

