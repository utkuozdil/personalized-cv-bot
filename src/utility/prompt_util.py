import json

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

def get_summary_prompt(resume_text):
    messages = [
        {
            "role": "system",
            "content": (
                "You are a professional resume reviewer. "
                "Summarize the resume below in 3–5 sentences. "
                "Highlight key experiences, skills, and overall profile of the candidate."
            )
        },
        {
            "role": "user",
            "content": f"Resume:\n{resume_text}"
        }
    ]
    return messages

def get_score_and_feedback_prompt(resume_text):
    messages = [
        {
            "role": "system",
            "content": (
                "You are a professional resume reviewer. "
                "Your task is to analyze a resume and return a detailed review in JSON format.\n\n"
                "Include:\n"
                "1. name (if found)\n"
                "2. overall_score (1–10)\n"
                "3. category_scores: clarity, experience, impact, skills\n"
                "4. feedback: strengths, red_flags, improvements\n\n"
                "Respond only with valid JSON like:\n"
                "{\n"
                "  \"name\": \"John Doe\",\n"
                "  \"overall_score\": 8.5,\n"
                "  \"category_scores\": {\n"
                "    \"clarity\": 9,\n"
                "    \"experience\": 8,\n"
                "    \"impact\": 7,\n"
                "    \"skills\": 8\n"
                "  },\n"
                "  \"feedback\": {\n"
                "    \"strengths\": \"...\",\n"
                "    \"red_flags\": \"...\",\n"
                "    \"improvements\": \"...\"\n"
                "  }\n"
                "}"
            )
        },
        {
            "role": "user",
            "content": f"Resume:\n{resume_text}"
        }
    ]
    return messages

def get_first_message_prompt(summary, score, category_scores, feedback):
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
