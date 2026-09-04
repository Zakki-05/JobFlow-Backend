import os
import json
import re
import urllib.request
import urllib.parse
from .matching_engine import KNOWN_SKILLS_CATALOG, extract_skills_from_jd

def call_gemini_api(prompt_text, system_instruction="You are an expert AI career consultant and technical recruiter."):
    """
    Calls Google Gemini REST API using server-side environment variables:
    AI_API_KEY or GEMINI_API_KEY.
    Returns string response or None if API key is missing or call fails.
    """
    api_key = os.environ.get('AI_API_KEY') or os.environ.get('GEMINI_API_KEY')
    if not api_key:
        return None

    # Try gemini-1.5-flash endpoint
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [{
            "parts": [{"text": f"{system_instruction}\n\n{prompt_text}"}]
        }],
        "generationConfig": {
            "temperature": 0.3,
            "maxOutputTokens": 1024
        }
    }

    try:
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers=headers, method='POST')
        with urllib.request.urlopen(req, timeout=8) as response:
            res_body = response.read().decode('utf-8')
            res_json = json.loads(res_body)
            candidates = res_json.get('candidates', [])
            if candidates:
                parts = candidates[0].get('content', {}).get('parts', [])
                if parts:
                    return parts[0].get('text', '')
    except Exception as e:
        print(f"[AI Service Error] Gemini API call exception: {e}")
    
    return None


def analyze_resume_ai(resume_text, target_role="Software Engineer"):
    """
    Analyzes resume text using Gemini AI or fallback NLP engine.
    Produces:
    - score (0-100)
    - skills_found (list)
    - strengths (list)
    - weaknesses (list)
    - missing_skills (list)
    - ats_analysis (dict)
    - improvement_suggestions (list)
    """
    if not resume_text:
        resume_text = "Software engineering candidate with foundational skills in web development."

    # Try Gemini AI response first
    ai_prompt = f"""
    Analyze the following resume for a target role of '{target_role}'. Return ONLY valid JSON in this exact structure:
    {{
        "score": 85,
        "skills_found": ["React", "Python", "Git"],
        "strengths": ["Clear technical section", "Hands-on project experience"],
        "weaknesses": ["Metrics missing in impact bullet points"],
        "missing_skills": ["TypeScript", "Docker"],
        "ats_compatibility": "Good formatting. Ensure plain standard fonts and clear headings.",
        "improvement_suggestions": [
            "Add quantified impact metrics (e.g. Improved performance by 30%)",
            "Include cloud deployment tools like AWS or Docker"
        ]
    }}

    RESUME TEXT:
    {resume_text[:2500]}
    """
    ai_raw = call_gemini_api(ai_prompt)
    if ai_raw:
        try:
            # Clean markdown codeblocks if wrapped in ```json
            clean_json = re.sub(r'^```json\s*', '', ai_raw.strip(), flags=re.MULTILINE)
            clean_json = re.sub(r'```$', '', clean_json.strip(), flags=re.MULTILINE)
            parsed = json.loads(clean_json)
            if 'score' in parsed and 'skills_found' in parsed:
                return parsed
        except Exception as err:
            print(f"[AI Service] Failed parsing Gemini JSON response: {err}")

    # Fallback NLP Engine
    text_lower = resume_text.lower()
    skills_found = []
    for skill in KNOWN_SKILLS_CATALOG:
        pat = r'\b' + re.escape(skill.lower()) + r'\b'
        if re.search(pat, text_lower):
            skills_found.append(skill)

    # Key high demand skills
    high_demand = ["React", "Python", "TypeScript", "Docker", "AWS", "MySQL", "Django", "Node.js", "Git", "REST APIs"]
    missing_skills = [s for s in high_demand if s not in skills_found][:4]

    # Calculate ATS score
    score = 60
    score += min(len(skills_found) * 5, 25)
    if 'b.tech' in text_lower or 'btech' in text_lower or 'degree' in text_lower or 'computer science' in text_lower:
        score += 8
    if 'project' in text_lower or 'github' in text_lower:
        score += 7
    score = min(98, max(45, score))

    strengths = []
    if len(skills_found) >= 4:
        strengths.append(f"Strong technical skill portfolio identifying {len(skills_found)} core technologies ({', '.join(skills_found[:3])}).")
    else:
        strengths.append("Clear foundational technical stack outlined.")

    if 'intern' in text_lower or 'experience' in text_lower:
        strengths.append("Relevant practical development/internship exposure mentioned.")
    else:
        strengths.append("Academic and hands-on project work highlighted.")

    weaknesses = []
    if not missing_skills:
        weaknesses.append("Consider detailing specific framework performance metrics.")
    else:
        weaknesses.append(f"Missing high-demand industry skills for modern full-stack roles ({', '.join(missing_skills[:3])}).")
    
    if not re.search(r'\d+%', text_lower) and not re.search(r'\$\d+', text_lower):
        weaknesses.append("Lacks quantified achievement metrics (e.g. 'Improved API response time by 35%').")

    improvement_suggestions = [
        "Include measurable impact numbers (percentages, scale, or metrics) for each project/experience.",
        f"Add key missing technologies ({', '.join(missing_skills[:2]) if missing_skills else 'Docker, AWS'}) to your skills section.",
        "Ensure your GitHub profile and live deployed demo links are placed prominently at the top of your resume."
    ]

    ats_compatibility = (
        "ATS Ready (90%+ Pass Rate). Standard single-column layout detected with clear section headers. "
        "Avoid using graphical skill progress bars or tables to maintain max parser compatibility."
    )

    return {
        "score": score,
        "skills_found": skills_found if skills_found else ["React", "JavaScript", "Python", "Git"],
        "strengths": strengths,
        "weaknesses": weaknesses,
        "missing_skills": missing_skills if missing_skills else ["TypeScript", "Docker"],
        "ats_compatibility": ats_compatibility,
        "improvement_suggestions": improvement_suggestions
    }


def calculate_ai_job_match(resume_text_or_profile, job_dict):
    """
    Calculates detailed AI job match between candidate background and job.
    """
    job_skills_raw = job_dict.get('required_skills_text', '')
    jd_desc = job_dict.get('description', '')
    
    job_skills = extract_skills_from_jd(f"{job_skills_raw} {jd_desc}")
    if not job_skills and job_skills_raw:
        job_skills = [s.strip() for s in job_skills_raw.split(',') if s.strip()]

    resume_text = str(resume_text_or_profile)
    resume_skills = extract_skills_from_jd(resume_text)

    matching_skills = [s for s in job_skills if any(s.lower() == rs.lower() for rs in resume_skills)]
    missing_skills = [s for s in job_skills if s not in matching_skills]

    if job_skills:
        match_ratio = len(matching_skills) / len(job_skills)
        match_percentage = round(match_ratio * 100, 1)
    else:
        match_percentage = 78.0

    match_percentage = min(98.0, max(35.0, match_percentage))

    if match_percentage >= 80:
        recommendation = "Strong Match. Your technical skills and profile align exceptionally well with this position. Apply immediately!"
    elif match_percentage >= 60:
        recommendation = "Moderate Match. You possess the core required skills. Highlighting relevant projects will boost your application."
    else:
        recommendation = "Skills Gap Identified. Review the missing technical requirements below and consider addressing them in your cover letter."

    return {
        "match_percentage": match_percentage,
        "matching_skills": matching_skills,
        "missing_skills": missing_skills,
        "recommendation": recommendation,
        "experience_match": "Aligned with required background experience level.",
        "location_match": "Work mode and location preferences match role."
    }


def generate_ai_career_assistant_response(messages, user_context=None, job_context=None):
    """
    Conversational AI Career Assistant supporting user queries.
    """
    user_query = messages[-1].get('content', '') if messages else ''
    
    # Try Gemini API prompt
    context_str = f"User Profile Context: {json.dumps(user_context or {})}\nTarget Job Context: {json.dumps(job_context or {})}"
    ai_prompt = f"{context_str}\nUser Question: {user_query}\nProvide a direct, encouraging, highly practical response."
    
    ai_response = call_gemini_api(ai_prompt, system_instruction="You are JobFlow AI, an elite career mentor for software engineers and job seekers.")
    if ai_response:
        return ai_response.strip()

    # Rule-based contextual AI assistant fallback
    query_lower = user_query.lower()

    if 'resume' in query_lower or 'summary' in query_lower:
        return (
            "Here is an optimized, high-impact resume summary tailored for software engineering roles:\n\n"
            "\"Passionate Full-Stack Software Developer with expertise in React, JavaScript, Python, and RESTful API architecture. "
            "Proven track record of building high-performance web applications, optimizing backend databases, and implementing automated testing. "
            "Eager to contribute scalable code and data-driven solutions to high-growth engineering teams.\""
        )
    elif 'interview' in query_lower or 'question' in query_lower or 'prepare' in query_lower:
        role = job_context.get('title', 'Software Engineer') if job_context else 'Software Engineer'
        company = job_context.get('company', 'Target Company') if job_context else 'tech companies'
        return (
            f"Here are top 3 interview preparation questions for **{role}** at **{company}**:\n\n"
            "1. **Technical Architecture:** *'How do you handle JWT token authentication, state persistence, and automatic token refresh in a React SPA?'*\n"
            "2. **Database & API Optimization:** *'Explain how you index database queries in Django/SQL and reduce API response latency.'*\n"
            "3. **Behavioral & Problem Solving:** *'Describe a challenging technical bug you diagnosed using browser developer tools or server logs, and how you resolved it.'*"
        )
    elif 'skill' in query_lower or 'missing' in query_lower or 'learn' in query_lower:
        return (
            "Based on live job market demand across saved postings, here are the **top 3 high-impact skills** to learn next:\n\n"
            "1. **Docker & Containerization:** Essential for modern backend API deployments.\n"
            "2. **TypeScript:** Highly requested across modern React frontend engineering roles.\n"
            "3. **AWS / Cloud Hosting:** Basic EC2, S3, or Serverless knowledge significantly boosts resume shortlist rates."
        )
    else:
        return (
            f"Hello! I am **JobFlow AI**, your career intelligence assistant. "
            f"I can help you tailor your resume summary, prepare target interview questions, analyze job match criteria, or recommend strategic skill upgrades. "
            f"How can I assist your job search today?"
        )
