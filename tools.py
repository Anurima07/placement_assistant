def jd_analyzer(jd_text, user_skills):
    import re

    text = jd_text.lower()

    # -------- SPLIT JD AND USER PART --------
    if "i know" in text:
        jd_part, user_part = text.split("i know", 1)
    else:
        jd_part = text
        user_part = ""

    # -------- CLEAN JD PART --------
    jd_part = jd_part.replace("jd:", "").replace("d:", "")

    # -------- EXTRACT JD SKILLS --------
    jd_words = re.findall(r'\b[a-zA-Z]{2,}\b', jd_part)

    stopwords = {
        "and", "the", "for", "with", "you", "should",
        "apply", "required", "job", "role", "need",
        "to", "a", "of"
    }

    required_skills = list(set([w for w in jd_words if w not in stopwords]))

    # -------- EXTRACT USER SKILLS --------
    if user_part:
        user_words = re.findall(r'\b[a-zA-Z]{2,}\b', user_part)
        user_skills = list(set(user_words))
    else:
        user_skills = [s.lower().strip() for s in user_skills]

    # -------- MATCH --------
    matched = [s for s in user_skills if s in required_skills]
    missing = [s for s in required_skills if s not in user_skills]

    # -------- SCORE --------
    match_percent = int((len(matched) / len(required_skills)) * 100) if required_skills else 0

    # -------- RECOMMENDATION --------
    if match_percent >= 70:
        rec = "Apply"
    elif match_percent >= 40:
        rec = "Improve first"
    else:
        rec = "Not suitable"

    return {
        "match_percentage": match_percent,
        "matched_skills": matched,
        "missing_skills": missing,
        "recommendation": rec
    }