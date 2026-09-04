import re

KNOWN_SKILLS_CATALOG = [
    # Frontend
    "React", "JavaScript", "TypeScript", "HTML", "CSS", "Tailwind CSS", "Vue.js", "Angular", "Next.js", "Redux", "Bootstrap",
    # Backend
    "Python", "Django", "Django REST Framework", "Flask", "Node.js", "Express.js", "Java", "Spring Boot", "C#", ".NET", "Go", "Ruby", "PHP",
    # Database
    "MySQL", "PostgreSQL", "MongoDB", "SQLite", "Redis", "Elasticsearch", "SQL",
    # DevOps & Tools
    "Git", "GitHub", "Docker", "Kubernetes", "AWS", "Azure", "GCP", "CI/CD", "Linux", "Nginx", "Jest", "Pytest", "Postman",
    # Soft Skills
    "Agile", "Scrum", "Communication", "Problem Solving", "Teamwork", "Leadership"
]

def extract_skills_from_jd(text):
    """
    Rule-based skill extraction from job description text.
    Finds keywords from catalog or standardized regex rules.
    """
    if not text:
        return []
    
    extracted = set()
    text_lower = text.lower()

    for skill in KNOWN_SKILLS_CATALOG:
        # Match word boundaries to prevent substring false positives (e.g., 'Go' matching 'Google')
        pattern = r'\b' + re.escape(skill.lower()) + r'\b'
        if re.search(pattern, text_lower):
            extracted.add(skill)

    # Secondary extraction of tech terms
    tech_patterns = [
        (r'\brest\b|\brestful\b', 'REST APIs'),
        (r'\bgraphql\b', 'GraphQL'),
        (r'\bmicroservices\b', 'Microservices'),
        (r'\bunit testing\b', 'Unit Testing'),
    ]
    for pat, name in tech_patterns:
        if re.search(pat, text_lower):
            extracted.add(name)

    return sorted(list(extracted))

def calculate_job_match_score(job_data, user_profile, user_skills):
    """
    Transparent 5-Factor Weighted Match Engine:
    1. Technical Skills (50%)
    2. Experience (20%)
    3. Education (10%)
    4. Responsibilities (10%)
    5. Location & Work Mode (10%)
    """
    jd_text = job_data.get('description', '')
    req_skills_raw = job_data.get('required_skills_text', '')
    
    # Standardize job required skills set
    job_skills = set()
    if req_skills_raw:
        for sk in req_skills_raw.split(','):
            sk_clean = sk.strip()
            if sk_clean:
                job_skills.add(sk_clean.lower())

    # Fallback to extraction if text list empty
    if not job_skills and jd_text:
        extracted = extract_skills_from_jd(jd_text)
        job_skills = {sk.lower() for sk in extracted}

    user_skills_map = {us.skill.name.lower(): us.skill.name for us in user_skills}
    user_skills_lower = set(user_skills_map.keys())

    # Factor 1: Technical Skills Match (50 points)
    matching_skills = []
    missing_skills = []

    if job_skills:
        for js_lower in job_skills:
            if js_lower in user_skills_lower:
                matching_skills.append(user_skills_map.get(js_lower, js_lower.title()))
            else:
                missing_skills.append(js_lower.title())
        
        match_ratio = len(matching_skills) / len(job_skills)
        skills_score = round(match_ratio * 50, 1)
    else:
        # Default generous baseline if no job skills detected
        skills_score = 40.0
        matching_skills = list(user_skills_map.values())[:5]

    # Factor 2: Experience Alignment (20 points)
    req_exp = float(job_data.get('experience_required', 1.0) or 1.0)
    user_exp = float(user_profile.experience_years if user_profile else 1.0)
    
    if user_exp >= req_exp:
        exp_score = 20.0
    else:
        exp_score = round((user_exp / max(req_exp, 1.0)) * 20.0, 1)

    # Factor 3: Education Alignment (10 points)
    edu_hierarchy = {
        'Doctorate': 4,
        'MTech': 3,
        'Masters': 3,
        'MCA_MSc': 3,
        'BTech': 2,
        'BCA_BSc': 2,
        'Bachelors': 2,
        'SelfTaught': 1
    }
    user_edu = user_profile.education_level if user_profile else 'BTech'
    job_edu = job_data.get('education', 'B.Tech')

    user_edu_val = edu_hierarchy.get(user_edu, 2)
    job_edu_val = 2 # Default engineering bachelor's assumption if unspecified
    if 'm.tech' in str(job_edu).lower() or 'mtech' in str(job_edu).lower() or 'master' in str(job_edu).lower():
        job_edu_val = 3
    elif 'phd' in str(job_edu).lower() or 'doctor' in str(job_edu).lower():
        job_edu_val = 4

    edu_score = 10.0 if user_edu_val >= job_edu_val else 7.0

    # Factor 4: Responsibilities Alignment (10 points)
    resp_score = 7.0  # Base responsibility score
    matching_responsibilities = []
    
    # Common action verbs to highlight alignment
    action_keywords = ['design', 'build', 'develop', 'test', 'deploy', 'collaborate', 'maintain', 'optimize', 'api']
    found_verbs = [v for v in action_keywords if v in jd_text.lower()]
    if len(found_verbs) >= 4:
        resp_score = 10.0
        matching_responsibilities.append("Strong alignment with core software development & API building responsibilities.")
        matching_responsibilities.append("Experience matching key duties: " + ", ".join(found_verbs[:4]).title())
    else:
        resp_score = 8.0
        matching_responsibilities.append("General alignment with engineering responsibilities.")

    # Factor 5: Location & Work Mode (10 points)
    work_mode = job_data.get('work_mode', 'Remote')
    job_loc = job_data.get('location', 'Remote')
    user_loc = user_profile.location if user_profile else 'Remote'

    if work_mode == 'Remote' or 'remote' in str(job_loc).lower() or 'remote' in str(user_loc).lower():
        loc_score = 10.0
    elif user_loc.lower() in job_loc.lower() or job_loc.lower() in user_loc.lower():
        loc_score = 10.0
    else:
        loc_score = 6.0

    # Total Overall JobMatch Score
    overall_score = round(skills_score + exp_score + edu_score + resp_score + loc_score, 1)
    overall_score = min(100.0, max(0.0, overall_score))

    # Recommendation classification
    if overall_score >= 80:
        match_level = "Strong Match"
        recommendation = "High match rate. Strongly recommended to tailor your resume and apply immediately."
    elif overall_score >= 60:
        match_level = "Moderate Match"
        recommendation = "Good fit. Review missing technical skills and address them in your cover letter."
    elif overall_score >= 40:
        match_level = "Low Match"
        recommendation = "Consider reviewing requirements. Strengthening key priority missing skills will boost your candidate rank."
    else:
        match_level = "Poor Match"
        recommendation = "Significant skill and experience gap identified for this specific role."

    return {
        'overall_match_score': overall_score,
        'match_level': match_level,
        'recommendation': recommendation,
        'factor_breakdown': {
            'technical_skills_score': skills_score,
            'technical_skills_max': 50,
            'experience_score': exp_score,
            'experience_max': 20,
            'education_score': edu_score,
            'education_max': 10,
            'responsibilities_score': resp_score,
            'responsibilities_max': 10,
            'location_score': loc_score,
            'location_max': 10
        },
        'matching_skills': matching_skills,
        'missing_skills': missing_skills,
        'matching_responsibilities': matching_responsibilities,
        'explanation': f"JobFlow Score derived from 5 factor weights: Technical Skills ({skills_score}/50), Experience ({exp_score}/20), Education ({edu_score}/10), Responsibilities ({resp_score}/10), Location/Mode ({loc_score}/10)."
    }
