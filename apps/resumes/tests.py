from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile
from apps.resumes.models import Resume

class ResumeAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='fresheruser', password='Password123!')
        self.client.force_authenticate(user=self.user)

    def test_parse_resume_file_auto_fills_data(self):
        resume_content = b"Mohammed Zakki\nEmail: zakki@example.com\nB.Tech in Computer Science & Engineering\nSoftware Engineering Intern at Razorpay\nSkills: React, Python, Django, MySQL, Git, Tailwind CSS"
        uploaded_file = SimpleUploadedFile("Mohammed_Zakki_Resume.txt", resume_content, content_type="text/plain")

        response = self.client.post('/api/resumes/parse-file/', {'file': uploaded_file}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('React', response.data['skills_summary'])
        self.assertIn('Python', response.data['skills_summary'])
        self.assertIn('B.Tech', response.data['education_data'])
        self.assertIn('Mohammed Zakki Resume CV', response.data['title'])

    def test_create_resume_with_file(self):
        resume_content = b"Sample Resume PDF File Data"
        uploaded_file = SimpleUploadedFile("Fresher_CV.pdf", resume_content, content_type="application/pdf")

        data = {
            'title': 'Fresh Graduate SDE Resume 2026',
            'summary': 'Full-stack software engineer fresher.',
            'education_data': 'B.Tech CSE',
            'experience_data': 'SDE Intern',
            'projects_data': 'JobFlow SaaS',
            'skills_summary': 'React, Python, Django',
            'file': uploaded_file
        }

        response = self.client.post('/api/resumes/', data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Resume.objects.count(), 1)
        self.assertEqual(Resume.objects.first().file_name, 'Fresher_CV.pdf')
