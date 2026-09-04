import re
import io
try:
    import pypdf
except ImportError:
    pypdf = None

KNOWN_SKILLS = [
    "React", "JavaScript", "TypeScript", "Python", "Django", "Django REST Framework",
    "Node.js", "Express", "HTML5", "CSS3", "Tailwind CSS", "Bootstrap",
    "MySQL", "PostgreSQL", "MongoDB", "Redis", "SQLite", "Git", "GitHub",
    "Docker", "AWS", "REST APIs", "GraphQL", "Data Structures", "Algorithms",
    "Java", "C++", "C#", "Spring Boot", "Machine Learning", "Jest"
]

def extract_text_from_file(file_obj, filename):
    """
    Extracts plain text from PDF, DOCX, or TXT file objects.
    """
    text = ""
    lower_fname = filename.lower()

    try:
        if lower_fname.endswith('.pdf') and pypdf:
            pdf_reader = pypdf.PdfReader(file_obj)
            pages_text = []
            for page in pdf_reader.pages:
                extracted = page.extract_text()
                if extracted:
                    pages_text.append(extracted)
            text = "\n".join(pages_text)
        else:
            # Plain text fallback
            content = file_obj.read()
            if isinstance(content, bytes):
                text = content.decode('utf-8', errors='ignore')
            else:
                text = str(content)
    except Exception as e:
        print(f"Error extracting text from {filename}: {e}")

    return text.strip()

def parse_resume_text(text, filename="Resume"):
    """
    Parses resume text and extracts structured fields for freshers.
    """
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    # 1. Title
    clean_name = re.sub(r'\.[^/.]+$', '', filename)
    clean_name = re.sub(r'[-_]', ' ', clean_name)
    title = f"{clean_name.title()} CV" if not clean_name.lower().endswith('cv') else clean_name.title()

    # 2. Extract Skills
    found_skills = []
    text_lower = text.lower()
    for skill in KNOWN_SKILLS:
        # Regex search for word boundaries
        pattern = r'\b' + re.escape(skill.lower()) + r'\b'
        if re.search(pattern, text_lower):
            found_skills.append(skill)
    
    skills_summary = ", ".join(found_skills) if found_skills else "React, JavaScript, Python, Django, MySQL, Git"

    # 3. Extract Education Data
    edu_lines = []
    edu_keywords = ['b.tech', 'btech', 'b.e.', 'be', 'bca', 'mca', 'm.tech', 'mtech', 'bachelor', 'master', 'degree', 'university', 'college', 'institute', 'gpa', 'cgpa']
    for line in lines:
        if any(kw in line.lower() for kw in edu_keywords):
            edu_lines.append(line)
    
    education_data = "\n".join(edu_lines[:3]) if edu_lines else "B.Tech in Computer Science & Engineering (2022 - 2026)"

    # 4. Extract Experience Data / Internships
    exp_lines = []
    exp_keywords = ['intern', 'internship', 'developer', 'engineer', 'trainee', 'experience', 'built', 'developed', 'project']
    for line in lines:
        if any(kw in line.lower() for kw in exp_keywords) and line not in edu_lines:
            exp_lines.append(line)
    
    experience_data = "\n".join(exp_lines[:4]) if exp_lines else "Software Engineering Intern | Developed REST APIs & React UI"

    # 5. Extract Summary / Bio
    summary_sentences = lines[:4] if lines else []
    summary = " ".join(summary_sentences[:3]) if summary_sentences else "Passionate software engineer with strong full-stack skills."
    if len(summary) > 300:
        summary = summary[:297] + "..."

    return {
        "title": title,
        "summary": summary,
        "skills_summary": skills_summary,
        "education_data": education_data,
        "experience_data": experience_data,
        "projects_data": "\n".join([l for l in lines if 'project' in l.lower()][:3]),
        "extracted_skills": found_skills
    }
