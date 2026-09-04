from rest_framework import generics, permissions, status, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q
from .models import Job, JobSkill
from .serializers import JobSerializer
from .matching_engine import extract_skills_from_jd, calculate_job_match_score
from apps.skills.models import Skill, UserSkill

class JobListCreateView(generics.ListCreateAPIView):
    serializer_class = JobSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Job.objects.filter(user=self.request.user)
        
        # Search filter
        search_query = self.request.query_params.get('search', None)
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(company__icontains=search_query) |
                Q(location__icontains=search_query) |
                Q(required_skills_text__icontains=search_query)
            )

        # Filter by work mode
        work_mode = self.request.query_params.get('work_mode', None)
        if work_mode and work_mode != 'All':
            queryset = queryset.filter(work_mode=work_mode)

        # Filter by job type
        job_type = self.request.query_params.get('job_type', None)
        if job_type and job_type != 'All':
            queryset = queryset.filter(job_type=job_type)

        # Filter by applied status
        is_applied = self.request.query_params.get('is_applied', None)
        if is_applied is not None:
            if is_applied.lower() in ('true', '1'):
                queryset = queryset.filter(is_applied=True)
            elif is_applied.lower() in ('false', '0'):
                queryset = queryset.filter(is_applied=False)

        # Ordering
        ordering = self.request.query_params.get('ordering', '-date_saved')
        return queryset.order_by(ordering)

    def perform_create(self, serializer):
        job = serializer.save(user=self.request.user)
        # Link skills if required_skills_text provided
        if job.required_skills_text:
            for sk_name in job.required_skills_text.split(','):
                sk_clean = sk_name.strip()
                if sk_clean:
                    skill_obj, _ = Skill.objects.get_or_create(
                        name__iexact=sk_clean,
                        defaults={'name': sk_clean, 'category': 'Other'}
                    )
                    JobSkill.objects.get_or_create(job=job, skill=skill_obj, defaults={'is_required': True})

class JobDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = JobSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Job.objects.filter(user=self.request.user)

    def perform_update(self, serializer):
        job = serializer.save()
        if job.required_skills_text:
            for sk_name in job.required_skills_text.split(','):
                sk_clean = sk_name.strip()
                if sk_clean:
                    skill_obj, _ = Skill.objects.get_or_create(
                        name__iexact=sk_clean,
                        defaults={'name': sk_clean, 'category': 'Other'}
                    )
                    JobSkill.objects.get_or_create(job=job, skill=skill_obj, defaults={'is_required': True})

class JobAnalyzerExtractView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        description = request.data.get('description', '')
        if not description:
            return Response({'error': 'Job description text is required.'}, status=status.HTTP_400_BAD_REQUEST)

        extracted_skills = extract_skills_from_jd(description)
        
        # Estimate job title / experience from text
        exp_match = 1.0
        if 'year' in description.lower():
            import re
            m = re.search(r'(\d+)\+?\s*years?', description.lower())
            if m:
                exp_match = float(m.group(1))

        return Response({
            'extracted_skills': extracted_skills,
            'extracted_skills_text': ", ".join(extracted_skills),
            'estimated_experience': exp_match,
            'description_preview': description[:250] + '...' if len(description) > 250 else description
        })

class JobMatchCalculateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        job_id = request.data.get('job_id', None)
        
        if job_id:
            try:
                job = Job.objects.get(id=job_id, user=user)
                job_data = {
                    'description': job.description,
                    'required_skills_text': job.required_skills_text,
                    'experience_required': job.experience_required,
                    'education': job.education,
                    'work_mode': job.work_mode,
                    'location': job.location
                }
            except Job.DoesNotExist:
                return Response({'error': 'Job not found.'}, status=status.HTTP_404_NOT_FOUND)
        else:
            job_data = request.data

        user_profile = getattr(user, 'profile', None)
        user_skills = UserSkill.objects.filter(user=user).select_related('skill')

        match_results = calculate_job_match_score(job_data, user_profile, user_skills)
        return Response(match_results)

SUITABLE_JOBS_CATALOG = [
    {
        "id": "sj_naukri_01",
        "title": "SDE-1 (React & Python / Django)",
        "company": "Razorpay",
        "location": "Bengaluru (Hybrid)",
        "job_type": "Full-time",
        "work_mode": "Hybrid",
        "salary": "₹16 LPA - ₹22 LPA",
        "source": "Naukri.com",
        "job_url": "https://naukri.com/job/razorpay-sde1",
        "description": "Building payment gateway infrastructure and merchant dashboards using React, Python, Django, MySQL, and Redis. High concurrency microservices development.",
        "required_skills_text": "React, JavaScript, Python, Django, REST APIs, MySQL, Git",
        "experience_required": 1.0,
        "education": "B.Tech / B.E."
    },
    {
        "id": "sj_instahyre_02",
        "title": "Frontend Engineer (React / TypeScript)",
        "company": "Swiggy",
        "location": "Bengaluru (Remote)",
        "job_type": "Full-time",
        "work_mode": "Remote",
        "salary": "₹14 LPA - ₹18 LPA",
        "source": "Instahyre",
        "job_url": "https://instahyre.com/job/swiggy-frontend",
        "description": "Looking for frontend engineers to build consumer tech web applications. High proficiency in React, TypeScript, Redux, and Web Performance optimization.",
        "required_skills_text": "React, JavaScript, TypeScript, Tailwind CSS, HTML5, Jest",
        "experience_required": 1.0,
        "education": "B.Tech / B.E."
    },
    {
        "id": "sj_linkedin_03",
        "title": "Backend SDE - Core Engineering",
        "company": "Flipkart",
        "location": "Bengaluru (Hybrid)",
        "job_type": "Full-time",
        "work_mode": "Hybrid",
        "salary": "₹20 LPA - ₹26 LPA",
        "source": "LinkedIn India",
        "job_url": "https://linkedin.com/jobs/flipkart-backend",
        "description": "Join Flipkart Core Supply Chain engineering. Design Django REST services, optimize relational database queries, and manage distributed caching.",
        "required_skills_text": "Python, Django, Django REST Framework, MySQL, Docker, Redis",
        "experience_required": 1.5,
        "education": "B.Tech / B.E."
    },
    {
        "id": "sj_unstop_04",
        "title": "Full Stack SDE Intern (PPO Offered)",
        "company": "CRED",
        "location": "Bengaluru (On-site)",
        "job_type": "Internship",
        "work_mode": "On-site",
        "salary": "₹40,000/month Stipend",
        "source": "Unstop",
        "job_url": "https://unstop.com/jobs/cred-sde-intern",
        "description": "6-month internship for fresh graduates passionate about slick UI animations, React, and backend API integration. Pre-Placement Offer (PPO) opportunities.",
        "required_skills_text": "React, JavaScript, HTML5, Git, Tailwind CSS",
        "experience_required": 0.5,
        "education": "B.Tech / B.E."
    },
    {
        "id": "sj_company_05",
        "title": "Software Development Engineer (Python / React)",
        "company": "Zomato",
        "location": "Gurgaon / NCR (Hybrid)",
        "job_type": "Full-time",
        "work_mode": "Hybrid",
        "salary": "₹15 LPA - ₹20 LPA",
        "source": "Company Portal",
        "job_url": "https://zomato.com/careers/sde",
        "description": "Develop high-throughput REST APIs and scalable React web modules for restaurant merchant ecosystem.",
        "required_skills_text": "React, TypeScript, Python, REST APIs, Docker, Git",
        "experience_required": 1.0,
        "education": "B.Tech / B.E."
    },
    {
        "id": "sj_glassdoor_06",
        "title": "Junior Web Engineer (SDE 1)",
        "company": "Microsoft India",
        "location": "Hyderabad / Bengaluru",
        "job_type": "Full-time",
        "work_mode": "Hybrid",
        "salary": "₹22 LPA - ₹28 LPA",
        "source": "Glassdoor India",
        "job_url": "https://glassdoor.co.in/job/microsoft-sde1",
        "description": "Build cloud web productivity services with React, TypeScript, and modern backend APIs.",
        "required_skills_text": "React, JavaScript, HTML5, CSS, Git",
        "experience_required": 1.0,
        "education": "B.Tech / B.E."
    },
    {
        "id": "sj_naukri_07",
        "title": "Graduate Engineer Trainee (GET)",
        "company": "TCS Digital",
        "location": "Hyderabad / Pune",
        "job_type": "Full-time",
        "work_mode": "Hybrid",
        "salary": "₹7 LPA - ₹9 LPA",
        "source": "Naukri.com",
        "job_url": "https://naukri.com/job/tcs-digital-get",
        "description": "TCS Digital role for entry level software engineers. Python Django framework, REST APIs, and SQL database management.",
        "required_skills_text": "Python, Django REST Framework, AWS, PostgreSQL, Redis",
        "experience_required": 0.5,
        "education": "B.Tech / B.E."
    },
    {
        "id": "sj_indeed_08",
        "title": "Full Stack Developer Trainee",
        "company": "Zoho Corporation",
        "location": "Chennai (On-site)",
        "job_type": "Full-time",
        "work_mode": "On-site",
        "salary": "₹8 LPA - ₹12 LPA",
        "source": "Indeed India",
        "job_url": "https://indeed.co.in/job/zoho-fullstack",
        "description": "Build cloud business software products. Strong foundational knowledge in Data Structures, JavaScript, and backend REST web services required.",
        "required_skills_text": "React, JavaScript, Tailwind CSS, Jest, Git",
        "experience_required": 0.5,
        "education": "B.Tech / MCA"
    }
]

class SuitableJobsListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        user_profile = getattr(user, 'profile', None)
        user_skills = UserSkill.objects.filter(user=user).select_related('skill')

        # Existing saved titles/companies for current user to flag is_imported
        saved_titles = set(Job.objects.filter(user=user).values_list('title', flat=True))

        source_filter = request.query_params.get('source', 'All')
        work_mode_filter = request.query_params.get('work_mode', 'All')
        search_query = request.query_params.get('search', '').lower()

        results = []
        for item in SUITABLE_JOBS_CATALOG:
            if source_filter != 'All' and item['source'] != source_filter:
                continue
            if work_mode_filter != 'All' and item['work_mode'] != work_mode_filter:
                continue
            if search_query:
                combined_text = f"{item['title']} {item['company']} {item['location']} {item['required_skills_text']}".lower()
                if search_query not in combined_text:
                    continue

            # Calculate JobMatch Score
            score_data = calculate_job_match_score(item, user_profile, user_skills)
            
            job_obj = dict(item)
            job_obj['match_score'] = score_data['overall_match_score']
            job_obj['match_breakdown'] = score_data
            job_obj['is_imported'] = item['title'] in saved_titles

            results.append(job_obj)

        # Sort by match score descending
        results.sort(key=lambda x: x['match_score'], reverse=True)

        return Response({
            'total_count': len(results),
            'results': results
        }, status=status.HTTP_200_OK)

class ImportSuitableJobView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        job_id = request.data.get('id')

        # Find in catalog or build from data
        item = next((j for j in SUITABLE_JOBS_CATALOG if j['id'] == job_id), None)
        if not item:
            item = request.data

        if not item or 'title' not in item:
            return Response({'error': 'Invalid job data.'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if already imported
        existing = Job.objects.filter(user=user, title=item['title'], company=item['company']).first()
        if existing:
            return Response({'message': 'Job is already in your board!', 'job_id': existing.id}, status=status.HTTP_200_OK)

        job = Job.objects.create(
            user=user,
            title=item['title'],
            company=item['company'],
            location=item.get('location', 'Bengaluru'),
            job_type=item.get('job_type', 'Full-time'),
            work_mode=item.get('work_mode', 'Remote'),
            salary=item.get('salary', '₹12 LPA - ₹18 LPA'),
            job_url=item.get('job_url', ''),
            description=item.get('description', ''),
            required_skills_text=item.get('required_skills_text', ''),
            experience_required=item.get('experience_required', 1.0),
            education=item.get('education', 'B.Tech / B.E.'),
            source=item.get('source', 'Naukri.com'),
            is_applied=False
        )

        # Link skills
        if job.required_skills_text:
            for sk_name in job.required_skills_text.split(','):
                sk_clean = sk_name.strip()
                if sk_clean:
                    skill_obj, _ = Skill.objects.get_or_create(
                        name__iexact=sk_clean,
                        defaults={'name': sk_clean, 'category': 'Other'}
                    )
                    JobSkill.objects.get_or_create(job=job, skill=skill_obj, defaults={'is_required': True})

        return Response({
            'message': f"'{job.title}' at {job.company} imported to your Job Board!",
            'job_id': job.id
        }, status=status.HTTP_201_CREATED)
