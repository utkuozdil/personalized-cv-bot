import difflib
import re
import functools
from src.integrations.openai import OpenAIIntegration
from src.utility.embed_utils import cosine_similarity

SECTION_LABELS = {
    "Work Experience": "This section describes the candidate's previous job experience, roles, and responsibilities.",
    "Education": "This section covers the candidate's educational background, including degrees and institutions.",
    "Skills": "This section lists the candidate's technical and soft skills.",
    "Projects": "This section describes specific projects the candidate worked on.",
    "Certifications": "This section includes any certifications or licenses the candidate holds.",
    "Summary": "This is a brief overview or summary of the candidate's profile.",
    "Languages": "This section mentions the languages the candidate can speak or write.",
    "Publications": "This section includes any academic or professional publications."
}

RULE_KEYWORDS = {
    "education": "Education",
    "skills": "Skills",
    "certifications": "Certifications",
    "projects": "Projects",
    "experience": "Work Experience",
    "employment": "Work Experience",
    "summary": "Summary",
    "profile": "Summary",
    "languages": "Languages",
    "publications": "Publications"
}

openai_integration = OpenAIIntegration()

@functools.lru_cache(maxsize=1)
def get_canonical_embeddings():
    print("Generating descriptive section embeddings...")
    return {
        label: openai_integration.embed_query(desc.lower())
        for label, desc in SECTION_LABELS.items()
    }

def normalize_extracted_header(line: str) -> str:
    if re.fullmatch(r"[A-Z ]{4,}", line.strip()):
        return line.replace(" ", "").title()
    return line.strip()

def llm_fallback_classify(header: str) -> str:
    system_prompt = (
        "You are a resume parser. "
        "Given a section title, classify it into one of the following canonical categories:\n"
        "Work Experience, Education, Skills, Projects, Certifications, Summary, Languages, Publications.\n"
        "If it doesn't clearly match, return 'Other'."
    )

    user_prompt = f"What resume section does the heading '{header}' most likely belong to?"

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    result = ""
    for token, _ in openai_integration.chat(messages):
        result += token

    label = result.strip()
    return label if label in SECTION_LABELS else "Other"

@functools.lru_cache(maxsize=128)
def classify_section(header: str, threshold: float = 0.3) -> str:
    header_clean = normalize_extracted_header(header)
    header_lower = header_clean.lower()

    # Step 1: Fuzzy match
    close = difflib.get_close_matches(header_lower, RULE_KEYWORDS.keys(), n=1, cutoff=0.6)
    if close:
        matched = RULE_KEYWORDS[close[0]]
        print(f"[Fuzzy Match] '{header}' → '{matched}'")
        return matched

    # Step 2: Embedding match
    header_vec = openai_integration.embed_text(header_clean.lower())
    canonical_vecs = get_canonical_embeddings()

    scored = [(title, cosine_similarity(header_vec, vec)) for title, vec in canonical_vecs.items()]
    scored.sort(key=lambda x: x[1], reverse=True)

    best_title, score = scored[0]
    print(f"[Embedding Match] '{header}' → '{best_title}' (score={score:.2f})")

    if score >= threshold:
        return best_title

    # Step 3: LLM fallback
    print(f"[LLM Fallback Triggered] for '{header}'")
    return llm_fallback_classify(header_clean)

def split_by_section(text: str) -> dict:
    sections = {}
    current = "Other"
    buffer = []

    for line in text.splitlines():
        stripped = normalize_extracted_header(line)
        if not stripped:
            continue

        # More flexible header detection
        if len(stripped) < 60 and re.fullmatch(r"[A-Za-z0-9\s\-:&]+", stripped) and not stripped.endswith("."):
            classified = classify_section(stripped)
            print(f"[Header] '{stripped}' → '{classified}'")
            if buffer:
                sections[current] = "\n".join(buffer).strip()
                buffer = []
            current = classified
        else:
            buffer.append(stripped)

    if buffer:
        sections[current] = "\n".join(buffer).strip()

    return sections
