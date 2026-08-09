"""
matcher.py
-----------
Core "Diagnosis Algorithm" / Searching Algorithm module.

Takes free-text or comma separated symptoms typed by the user,
normalizes them, and scores every disease record in the database
by how many of its symptom keywords overlap with the user's input.

This implements:
    - Symptoms -> Input Data
    - Disease Search -> Searching Algorithm
    - Decision Making -> Conditional Statements
    - Disease Classification -> Data Classification (grouped by dosha)
"""

import re
from database import get_connection

# Minimum overlap ratio (against the disease's own symptom list) required
# for a disease to be considered a match. Tunable "rule" for classification.
MATCH_THRESHOLD = 0.25


def normalize_symptoms(raw_text):
    """
    Convert free text like 'I have Headache, Nausea and light Sensitivity'
    into a clean list of lowercase keyword tokens/phrases.
    """
    if not raw_text:
        return []

    text = raw_text.lower()
    # split on commas, 'and', semicolons, newlines
    parts = re.split(r",|;|\band\b|\n", text)
    cleaned = []
    for p in parts:
        p = p.strip()
        p = re.sub(r"[^a-z0-9\s]", "", p)
        p = re.sub(r"\s+", " ", p).strip()
        if p:
            cleaned.append(p)
    return cleaned


def validate_input(raw_text):
    """
    Basic input validation (step 3 of the working: 'System validates input').
    Returns (is_valid, error_message)
    """
    if raw_text is None or not raw_text.strip():
        return False, "Please enter at least one symptom."

    if len(raw_text.strip()) < 3:
        return False, "Please enter a valid symptom description (too short)."

    if not re.search(r"[a-zA-Z]", raw_text):
        return False, "Symptoms must contain valid text, not just numbers/symbols."

    tokens = normalize_symptoms(raw_text)
    if not tokens:
        return False, "Could not understand the entered symptoms. Please rephrase."

    return True, None


def _score_disease(user_tokens, disease_symptoms_field):
    """
    Compute an overlap score between the user's entered symptom tokens
    and a disease's stored symptom keyword list.
    Returns (score_ratio, matched_keywords)
    """
    disease_tokens = [s.strip() for s in disease_symptoms_field.lower().split(",") if s.strip()]
    if not disease_tokens:
        return 0.0, []

    matched = set()
    for d_kw in disease_tokens:
        for u_kw in user_tokens:
            # match if either keyword is contained in the other
            # (handles partial phrases like 'headache' vs 'severe headache')
            if d_kw in u_kw or u_kw in d_kw:
                matched.add(d_kw)
                break

    score = len(matched) / len(disease_tokens)
    return score, sorted(matched)


def find_matching_diseases(raw_symptom_text):
    """
    Main search/classification function.
    Returns a list of dicts, each containing the disease row plus
    match_score and matched_keywords, sorted by best match first.
    Only diseases scoring >= MATCH_THRESHOLD are returned.
    """
    user_tokens = normalize_symptoms(raw_symptom_text)
    if not user_tokens:
        return []

    conn = get_connection()
    diseases = conn.execute("SELECT * FROM diseases").fetchall()
    conn.close()

    results = []
    for d in diseases:
        score, matched = _score_disease(user_tokens, d["symptoms"])
        if score >= MATCH_THRESHOLD:
            row = dict(d)
            row["match_score"] = round(score * 100, 1)
            row["matched_keywords"] = matched
            results.append(row)

    results.sort(key=lambda r: r["match_score"], reverse=True)
    return results
