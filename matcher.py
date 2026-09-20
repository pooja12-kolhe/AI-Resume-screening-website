import re

from .skill_extractor import SKILLS


# ==========================================
# SKILL ALIASES
# ==========================================

SKILL_ALIASES = {

    "rest api": [
        "rest api",
        "restful api"
    ],

    "restful api": [
        "rest api",
        "restful api"
    ],

    "javascript": [
        "javascript",
        "js"
    ],

    "typescript": [
        "typescript",
        "ts"
    ],

    "node.js": [
        "node.js",
        "nodejs",
        "node"
    ],

    "express.js": [
        "express.js",
        "express"
    ],

    "postgresql": [
        "postgresql",
        "postgres"
    ],

    "sql": [
        "sql",
        "mysql",
        "postgresql"
    ],

    "machine learning": [
        "machine learning",
        "ml"
    ],

    "artificial intelligence": [
        "artificial intelligence",
        "ai"
    ],

    "scikit-learn": [
        "scikit-learn",
        "sklearn"
    ],
}


# ==========================================
# SKILL WEIGHTS
# ==========================================

HIGH_WEIGHT = 3
MEDIUM_WEIGHT = 2
LOW_WEIGHT = 1


CORE_SKILLS = [

    "python",
    "java",
    "c",
    "c++",
    "javascript",
    "typescript",
    "django",
    "flask",
    "react",
    "angular",
    "node.js",
    "machine learning",
    "deep learning",
    "artificial intelligence",
    "data science",
    "data analysis",

]


TECHNICAL_SKILLS = [

    "sql",
    "mysql",
    "postgresql",
    "mongodb",
    "sqlite",
    "rest api",
    "restful api",
    "express.js",
    "pandas",
    "numpy",
    "scikit-learn",

]


TOOL_SKILLS = [

    "git",
    "github",
    "postman",
    "vs code",
    "html",
    "css",
    "bootstrap",

]


# ==========================================
# IMPORTANT KEYWORDS
# ==========================================

IMPORTANT_KEYWORDS = [

    "developer",
    "software developer",
    "software engineer",
    "engineer",
    "programmer",

    "data analyst",
    "data scientist",
    "data analysis",

    "machine learning",
    "artificial intelligence",

    "web developer",
    "backend",
    "frontend",
    "full stack",

    "database",
    "api",
    "rest api",

    "project",
    "development",

]


# ==========================================
# CHECK SKILL
# ==========================================

def contains_skill(text, skill):

    """
    Check whether a skill exists as a complete
    word or phrase.
    """

    pattern = (
        r'(?<!\w)'
        + re.escape(skill)
        + r'(?!\w)'
    )

    return bool(
        re.search(
            pattern,
            text,
            re.IGNORECASE
        )
    )


# ==========================================
# GET SKILL WEIGHT
# ==========================================

def get_skill_weight(skill):

    """
    Assign importance to each skill.
    """

    skill_lower = skill.lower()

    if skill_lower in CORE_SKILLS:
        return HIGH_WEIGHT

    if skill_lower in TECHNICAL_SKILLS:
        return MEDIUM_WEIGHT

    if skill_lower in TOOL_SKILLS:
        return LOW_WEIGHT

    return MEDIUM_WEIGHT


# ==========================================
# EXTRACT JOB SKILLS
# ==========================================

def extract_job_skills(job_description):

    detected_skills = []

    job_text = job_description.lower()

    for skill in SKILLS:

        if contains_skill(job_text, skill):

            detected_skills.append(skill)

    return detected_skills


# ==========================================
# EXTRACT IMPORTANT KEYWORDS
# ==========================================

def extract_keywords(text):

    """
    Extract important job-related keywords.
    """

    detected_keywords = []

    text_lower = text.lower()

    for keyword in IMPORTANT_KEYWORDS:

        if contains_skill(text_lower, keyword):

            detected_keywords.append(keyword)

    return detected_keywords


# ==========================================
# CALCULATE KEYWORD MATCH
# ==========================================

def calculate_keyword_match(
    resume_text,
    job_description
):

    """
    Compare important keywords from the
    job description with the resume.
    """

    job_keywords = extract_keywords(
        job_description
    )

    resume_text_lower = resume_text.lower()

    matched_keywords = []

    missing_keywords = []

    for keyword in job_keywords:

        if contains_skill(
            resume_text_lower,
            keyword
        ):

            matched_keywords.append(keyword)

        else:

            missing_keywords.append(keyword)

    if len(job_keywords) > 0:

        keyword_score = round(
            (
                len(matched_keywords)
                / len(job_keywords)
            ) * 100
        )

    else:

        keyword_score = 0

    return {
        "score": keyword_score,
        "matched_keywords": matched_keywords,
        "missing_keywords": missing_keywords,
    }


# ==========================================
# CALCULATE SKILL MATCH
# ==========================================

def calculate_skill_match(
    resume_skills,
    job_description
):

    resume_skill_list = [

        skill.strip().lower()

        for skill in resume_skills.split(",")

        if skill.strip()

    ]

    required_skills = extract_job_skills(
        job_description
    )

    matched_skills = []

    missing_skills = []

    earned_weight = 0

    total_weight = 0


    for required_skill in required_skills:

        required_lower = required_skill.lower()

        weight = get_skill_weight(
            required_skill
        )

        total_weight += weight


        # ------------------------------
        # Exact match
        # ------------------------------

        if required_lower in resume_skill_list:

            matched_skills.append(
                required_skill
            )

            earned_weight += weight

            continue


        # ------------------------------
        # Related match
        # ------------------------------

        aliases = SKILL_ALIASES.get(
            required_lower,
            [required_lower]
        )

        related_match = False

        for resume_skill in resume_skill_list:

            if resume_skill in aliases:

                related_match = True

                break


        if related_match:

            matched_skills.append(
                f"{required_skill} (related)"
            )

            # Related skill receives 80%
            earned_weight += weight * 0.8

        else:

            missing_skills.append(
                required_skill
            )


    # ------------------------------
    # Skill score
    # ------------------------------

    if total_weight > 0:

        skill_score = round(
            (
                earned_weight
                / total_weight
            ) * 100
        )

    else:

        skill_score = 0


    skill_score = min(
        skill_score,
        100
    )


    return {
        "score": skill_score,
        "required_skills": required_skills,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
    }


# ==========================================
# FINAL MATCH CALCULATION
# ==========================================

def calculate_match(
    resume_skills,
    job_description,
    resume_text=""
):

    """
    Calculate the final candidate-job
    compatibility score.

    Skill Match  = 70%
    Keyword Match = 30%
    """

    # --------------------------------------
    # Skill matching
    # --------------------------------------

    skill_result = calculate_skill_match(
        resume_skills,
        job_description
    )

    skill_score = skill_result["score"]


    # --------------------------------------
    # Keyword matching
    # --------------------------------------

    keyword_result = calculate_keyword_match(
        resume_text,
        job_description
    )

    keyword_score = keyword_result["score"]


    # --------------------------------------
    # Final weighted score
    # --------------------------------------

    if resume_text.strip():

        final_score = round(
            (
                skill_score * 0.70
            )
            +
            (
                keyword_score * 0.30
            )
        )

    else:

        # Backward compatibility
        final_score = skill_score


    final_score = min(
        final_score,
        100
    )


    # ======================================
    # RECOMMENDATION
    # ======================================

    if final_score >= 75:

        recommendation = (
            "Strong match. The candidate has "
            "many of the important skills and "
            "keywords required for this position."
        )

    elif final_score >= 50:

        recommendation = (
            "Moderate match. The candidate has "
            "several relevant skills and keywords "
            "but is missing some requirements."
        )

    else:

        recommendation = (
            "Low match. The candidate is missing "
            "several important skills or keywords "
            "required for this position."
        )


    # ======================================
    # RETURN RESULT
    # ======================================

    return {

        "score": final_score,

        "skill_score": skill_score,

        "keyword_score": keyword_score,

        "required_skills":
            skill_result["required_skills"],

        "matched_skills":
            skill_result["matched_skills"],

        "missing_skills":
            skill_result["missing_skills"],

        "matched_keywords":
            keyword_result["matched_keywords"],

        "missing_keywords":
            keyword_result["missing_keywords"],

        "recommendation":
            recommendation,

    }