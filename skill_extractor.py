SKILLS = [
    # Programming Languages
    "Python",
    "Java",
    "C",
    "C++",
    "JavaScript",
    "TypeScript",
    "PHP",

    # Web Development
    "HTML",
    "CSS",
    "Bootstrap",
    "React",
    "Angular",
    "Django",
    "Flask",
    "Node.js",
    "Express.js",

    # Databases
    "MySQL",
    "PostgreSQL",
    "MongoDB",
    "SQLite",
    "SQL",

    # AI / Data
    "Machine Learning",
    "Deep Learning",
    "Artificial Intelligence",
    "Data Science",
    "Data Analysis",
    "Pandas",
    "NumPy",
    "Scikit-learn",

    # Tools
    "Git",
    "GitHub",
    "Postman",
    "VS Code",

    # APIs
    "REST API",
    "RESTful API",
]
def extract_skills(text):
    detected_skills = []

    text_lower = text.lower()

    for skill in SKILLS:
        if skill.lower() in text_lower:
            detected_skills.append(skill)

    return detected_skills
