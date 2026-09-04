from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from django.utils import timezone
from datetime import timedelta, date
from django.contrib.auth.models import User
from apps.skills.models import Skill, UserSkill
from apps.jobs.models import Job, JobSkill
from apps.resumes.models import Resume
from apps.applications.models import Application, ApplicationStatusHistory, FollowUp
from apps.interviews.models import Interview, InterviewQuestion

SEED_SKILLS = [
    ("React", "Frontend"),
    ("JavaScript", "Frontend"),
    ("TypeScript", "Frontend"),
    ("HTML5", "Frontend"),
    ("Tailwind CSS", "Frontend"),
    ("Python", "Backend"),
    ("Django", "Backend"),
    ("Django REST Framework", "Backend"),
    ("Node.js", "Backend"),
    ("MySQL", "Database"),
    ("PostgreSQL", "Database"),
    ("Redis", "Database"),
    ("Docker", "DevOps"),
    ("AWS", "DevOps"),
    ("Git", "Tools"),
    ("Jest", "Tools"),
    ("REST APIs", "Backend"),
    ("Agile Development", "SoftSkills"),
]

SEED_JOBS = [
    {
        "title": "SDE-1 (React & Python / Django)",
        "company": "Razorpay",
        "location": "Bengaluru (Hybrid)",
        "job_type": "Full-time",
        "work_mode": "Hybrid",
        "salary": "₹16 LPA - ₹22 LPA",
        "job_url": "https://razorpay.com/jobs/sde1",
        "description": "Building payment gateway infrastructure and merchant dashboards using React, Python, Django, MySQL, and Redis. High concurrency microservices development.",
        "required_skills_text": "React, JavaScript, Python, Django, REST APIs, MySQL, Git",
        "experience_required": 1.0,
        "education": "B.Tech / B.E.",
        "source": "Naukri.com",
        "status": "INTERVIEW",
        "match_score": 88.5
    },
    {
        "title": "Frontend Engineer (React / TypeScript)",
        "company": "Swiggy",
        "location": "Bengaluru (Remote)",
        "job_type": "Full-time",
        "work_mode": "Remote",
        "salary": "₹14 LPA - ₹18 LPA",
        "job_url": "https://swiggy.com/careers",
        "description": "Looking for frontend engineers to build consumer tech web applications. High proficiency in React, TypeScript, Redux, and Web Performance optimization.",
        "required_skills_text": "React, JavaScript, TypeScript, Tailwind CSS, HTML5, Jest",
        "experience_required": 1.0,
        "education": "B.Tech / B.E.",
        "source": "Instahyre",
        "status": "OFFER",
        "match_score": 84.0
    },
    {
        "title": "Backend Engineer - SDE II (Django / MySQL)",
        "company": "Flipkart",
        "location": "Bengaluru (Hybrid)",
        "job_type": "Full-time",
        "work_mode": "Hybrid",
        "salary": "₹20 LPA - ₹26 LPA",
        "job_url": "https://flipkartcareers.com/backend",
        "description": "Join Flipkart Core Supply Chain engineering. Design Django REST services, optimize relational database queries, and manage distributed Caching.",
        "required_skills_text": "Python, Django, Django REST Framework, MySQL, Docker, Redis",
        "experience_required": 2.0,
        "education": "B.Tech / B.E.",
        "source": "LinkedIn India",
        "status": "ASSESSMENT",
        "match_score": 79.0
    },
    {
        "title": "SDE Intern (Full Stack)",
        "company": "CRED",
        "location": "Bengaluru (On-site)",
        "job_type": "Internship",
        "work_mode": "On-site",
        "salary": "₹40,000/month Stipend",
        "job_url": "https://cred.club/careers",
        "description": "6-month internship for fresh graduates passionate about slick UI animations, React, and backend API integration. Pre-Placement Offer (PPO) opportunities.",
        "required_skills_text": "React, JavaScript, HTML5, Git, Tailwind CSS",
        "experience_required": 0.5,
        "education": "B.Tech / B.E.",
        "source": "Unstop",
        "status": "APPLIED",
        "match_score": 92.0
    },
    {
        "title": "Software Development Engineer (Python / React)",
        "company": "Zomato",
        "location": "Gurgaon / NCR (Hybrid)",
        "job_type": "Full-time",
        "work_mode": "Hybrid",
        "salary": "₹15 LPA - ₹20 LPA",
        "job_url": "https://zomato.com/careers",
        "description": "Develop high-throughput REST APIs and scalable React web modules for restaurant merchant ecosystem.",
        "required_skills_text": "React, TypeScript, Python, REST APIs, Docker, Git",
        "experience_required": 1.5,
        "education": "B.Tech / B.E.",
        "source": "Naukri.com",
        "status": "APPLIED",
        "match_score": 81.5
    },
    {
        "title": "Full Stack Developer",
        "company": "Zoho Corporation",
        "location": "Chennai (On-site)",
        "job_type": "Full-time",
        "work_mode": "On-site",
        "salary": "₹8 LPA - ₹12 LPA",
        "job_url": "https://zoho.com/careers",
        "description": "Build cloud business software products. Strong foundational knowledge in Data Structures, JavaScript, and backend REST web services required.",
        "required_skills_text": "React, JavaScript, Tailwind CSS, Jest, Git",
        "experience_required": 1.0,
        "education": "B.Tech / MCA",
        "source": "Company Portal",
        "status": "REJECTED",
        "match_score": 77.0
    },
    {
        "title": "Python Backend Trainee",
        "company": "TCS Digital",
        "location": "Hyderabad / Pune",
        "job_type": "Full-time",
        "work_mode": "Hybrid",
        "salary": "₹7 LPA - ₹9 LPA",
        "job_url": "https://tcs.com/careers",
        "description": "TCS Digital role for entry level software engineers. Python Django framework, REST APIs, and SQL database management.",
        "required_skills_text": "Python, Django REST Framework, AWS, PostgreSQL, Redis",
        "experience_required": 0.5,
        "education": "B.Tech / B.E.",
        "source": "Naukri.com",
        "status": "SAVED",
        "match_score": 72.0
    },
    {
        "title": "Junior Web Engineer (SDE 1)",
        "company": "Microsoft India",
        "location": "Hyderabad / Bengaluru",
        "job_type": "Full-time",
        "work_mode": "Hybrid",
        "salary": "₹22 LPA - ₹28 LPA",
        "job_url": "https://careers.microsoft.com/india",
        "description": "Build cloud web productivity services with React, TypeScript, and modern backend APIs.",
        "required_skills_text": "React, JavaScript, HTML5, CSS, Git",
        "experience_required": 1.0,
        "education": "B.Tech / B.E.",
        "source": "LinkedIn India",
        "status": "APPLIED",
        "match_score": 90.0
    }
]

SEED_QUESTIONS = [
    {
        "company": "Razorpay",
        "role": "SDE-1",
        "round": "Technical",
        "question": "What is the difference between useState and useEffect hooks in React, and how do you handle race conditions in API requests?",
        "answer": "useState manages local component state, while useEffect runs side-effects. Race conditions in API calls are resolved using AbortController or cleanup flags.",
        "difficulty": "Medium"
    },
    {
        "company": "Swiggy",
        "role": "Frontend Engineer",
        "round": "Coding",
        "question": "How do you optimize initial page load performance in a large React SPA deployed in India with varying network speeds?",
        "answer": "Utilize Route-based Code Splitting (React.lazy + Suspense), image optimization (WebP), asset caching, and Gzip/Brotli compression.",
        "difficulty": "Hard"
    },
    {
        "company": "Flipkart",
        "role": "Backend Engineer",
        "round": "Technical",
        "question": "Explain the difference between select_related and prefetch_related in Django ORM with code examples.",
        "answer": "select_related performs SQL JOINs for ForeignKeys/OneToOne. prefetch_related executes separate queries and performs in-memory Python joining for ManyToMany or Reverse ForeignKeys.",
        "difficulty": "Medium"
    }
]

class SeedDataView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        
        # 1. Master Skills Catalog
        skill_objects = {}
        for sname, scat in SEED_SKILLS:
            sk, _ = Skill.objects.get_or_create(name=sname, defaults={'category': scat})
            skill_objects[sname] = sk

        # 2. User Skills
        user_skills_to_add = [
            ("React", "Advanced", 2.0),
            ("JavaScript", "Expert", 3.0),
            ("Python", "Advanced", 2.5),
            ("Django", "Intermediate", 1.5),
            ("Django REST Framework", "Intermediate", 1.5),
            ("MySQL", "Intermediate", 1.5),
            ("Git", "Advanced", 3.0),
            ("Tailwind CSS", "Expert", 2.0),
            ("HTML5", "Expert", 3.0),
        ]
        for sk_name, prof, yrs in user_skills_to_add:
            if sk_name in skill_objects:
                UserSkill.objects.get_or_create(
                    user=user,
                    skill=skill_objects[sk_name],
                    defaults={'proficiency': prof, 'years_experience': yrs}
                )

        # 3. Default Resume
        resume, _ = Resume.objects.get_or_create(
            user=user,
            title="Software Engineering Full-Stack Resume 2026",
            defaults={
                'summary': "Full-Stack Software Engineer proficient in React, JavaScript, Python, Django REST Framework, and MySQL.",
                'education_data': "B.S. in Computer Science & Engineering (2022 - 2026)",
                'experience_data': "Software Engineering Intern | Developed RESTful services and interactive SaaS dashboards.",
                'projects_data': "JobFlow Job Application Platform, Campus Management App",
                'skills_summary': "React, JavaScript, Python, Django, MySQL, Tailwind CSS, Git, REST APIs",
                'is_default': True
            }
        )

        # 4. Jobs & Applications
        today = date.today()
        created_jobs = 0
        created_apps = 0

        for idx, item in enumerate(SEED_JOBS):
            job, job_created = Job.objects.get_or_create(
                user=user,
                company=item['company'],
                title=item['title'],
                defaults={
                    'location': item['location'],
                    'job_type': item['job_type'],
                    'work_mode': item['work_mode'],
                    'salary': item['salary'],
                    'job_url': item['job_url'],
                    'description': item['description'],
                    'required_skills_text': item['required_skills_text'],
                    'experience_required': item['experience_required'],
                    'education': item['education'],
                    'source': item['source'],
                    'is_applied': item['status'] != 'SAVED'
                }
            )

            # Link job skills
            for sk_name in item['required_skills_text'].split(','):
                sk_clean = sk_name.strip()
                if sk_clean in skill_objects:
                    JobSkill.objects.get_or_create(job=job, skill=skill_objects[sk_clean], defaults={'is_required': True})

            if job_created:
                created_jobs += 1

            if item['status'] != 'SAVED':
                app, app_created = Application.objects.get_or_create(
                    user=user,
                    job=job,
                    defaults={
                        'status': item['status'],
                        'match_score': item['match_score'],
                        'resume': resume,
                        'notes': f"Applied via {item['source']} portal."
                    }
                )
                if app_created:
                    created_apps += 1
                    ApplicationStatusHistory.objects.create(
                        application=app,
                        status='APPLIED',
                        notes=f"Initial application submitted via {item['source']}."
                    )
                    if item['status'] in ['INTERVIEW', 'OFFER']:
                        ApplicationStatusHistory.objects.create(
                            application=app,
                            status=item['status'],
                            notes=f"Advanced to {item['status']} round."
                        )
                        # Schedule Interview if status is INTERVIEW
                        if item['status'] == 'INTERVIEW':
                            interview, _ = Interview.objects.get_or_create(
                                user=user,
                                application=app,
                                round='Technical',
                                defaults={
                                    'interview_date': timezone.now() + timedelta(days=3),
                                    'interviewer': 'Lead Engineering Manager',
                                    'status': 'SCHEDULED',
                                    'notes': 'Prepare live system design & React component coding demonstration.'
                                }
                            )

                    # Follow-up for applied apps
                    FollowUp.objects.get_or_create(
                        application=app,
                        status='NEEDS_FOLLOWUP' if idx % 2 == 0 else 'COMPLETED',
                        defaults={
                            'followup_date': today + timedelta(days=5),
                            'notes': f"Send email follow-up to recruiter at {item['company']}."
                        }
                    )

        # 5. Seed Interview Questions
        for q in SEED_QUESTIONS:
            InterviewQuestion.objects.get_or_create(
                user=user,
                company=q['company'],
                question=q['question'],
                defaults={
                    'role': q['role'],
                    'round': q['round'],
                    'answer': q['answer'],
                    'difficulty': q['difficulty']
                }
            )

        return Response({
            'message': 'Demo seed data generated successfully!',
            'details': {
                'jobs_processed': len(SEED_JOBS),
                'new_jobs_created': created_jobs,
                'applications_created': created_apps,
                'user_skills': len(user_skills_to_add),
                'questions_seeded': len(SEED_QUESTIONS)
            }
        }, status=status.HTTP_201_CREATED)
