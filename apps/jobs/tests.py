from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from apps.jobs.models import Job
from apps.jobs.matching_engine import calculate_job_match_score
from apps.skills.models import Skill, UserSkill

class JobAndMatchingEngineTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='Password123!')
        self.user2 = User.objects.create_user(username='user2', password='Password123!')
        
        self.client1 = APIClient()
        self.client1.force_authenticate(user=self.user1)
        
        self.client2 = APIClient()
        self.client2.force_authenticate(user=self.user2)

        self.job1 = Job.objects.create(
            user=self.user1,
            title='React Frontend Developer',
            company='Acme Inc',
            required_skills_text='React, JavaScript, CSS',
            experience_required=1.0
        )

    def test_user_can_only_see_own_jobs(self):
        response1 = self.client1.get('/api/jobs/')
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response1.data['results']), 1)

        response2 = self.client2.get('/api/jobs/')
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response2.data['results']), 0)

    def test_job_match_score_calculation(self):
        # Add React and JavaScript to user1's skills
        react_skill = Skill.objects.create(name='React', category='Frontend')
        js_skill = Skill.objects.create(name='JavaScript', category='Frontend')
        
        UserSkill.objects.create(user=self.user1, skill=react_skill, proficiency='Advanced', years_experience=2.0)
        UserSkill.objects.create(user=self.user1, skill=js_skill, proficiency='Expert', years_experience=3.0)

        job_data = {
            'description': 'React and JavaScript application development.',
            'required_skills_text': 'React, JavaScript',
            'experience_required': 1.0,
            'education': 'Bachelors',
            'work_mode': 'Remote',
            'location': 'Remote'
        }
        
        result = calculate_job_match_score(job_data, self.user1.profile, self.user1.user_skills.all())
        self.assertGreaterEqual(result['overall_match_score'], 80.0)
        self.assertEqual(result['match_level'], 'Strong Match')

    def test_suitable_jobs_feed_and_import(self):
        # 1. Fetch suitable jobs feed
        response = self.client1.get('/api/jobs/suitable-jobs/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(response.data['total_count'], 0)
        
        first_job = response.data['results'][0]
        self.assertIn('match_score', first_job)
        self.assertIn('source', first_job)

        # 2. Import job into board
        import_response = self.client1.post('/api/jobs/import-job/', {'id': first_job['id']})
        self.assertEqual(import_response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Job.objects.filter(user=self.user1, title=first_job['title']).exists())
