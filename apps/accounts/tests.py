from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status

class AuthenticationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = '/api/auth/register/'
        self.login_url = '/api/auth/login/'
        self.user_data = {
            'username': 'testuser',
            'email': 'test@jobflow.com',
            'password': 'Password123!',
            'password_confirm': 'Password123!'
        }

    def test_register_user_creates_account_and_profile(self):
        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='testuser').exists())
        user = User.objects.get(username='testuser')
        self.assertIsNotNone(user.profile)

    def test_login_user_returns_jwt_tokens(self):
        User.objects.create_user(
            username='testuser', email='test@jobflow.com', password='Password123!'
        )
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'Password123!'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_update_user_profile_success(self):
        user = User.objects.create_user(
            username='testuser', email='test@jobflow.com', password='Password123!'
        )
        self.client.force_authenticate(user=user)

        profile_data = {
            'first_name': 'Mohammed',
            'last_name': 'Zakki',
            'headline': 'Software Engineer',
            'target_role': 'Full Stack Developer',
            'experience_years': 1.0,
            'education_level': "Bachelor's Degree",
            'location': 'Bengaluru',
            'target_salary': 1200000,
            'github_url': '',
            'linkedin_url': '',
            'portfolio_url': ''
        }

        response = self.client.put('/api/auth/profile/', profile_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Mohammed')
        self.assertEqual(response.data['profile']['education_level'], 'BTech')

    def test_login_case_insensitive_username_and_email(self):
        User.objects.create_user(
            username='mr-zakki', email='zakkiadnan05@gmail.com', password='MyPassword123!'
        )
        # Case insensitive username login
        res1 = self.client.post(self.login_url, {'username': 'Mr-Zakki', 'password': 'MyPassword123!'})
        self.assertEqual(res1.status_code, status.HTTP_200_OK)
        self.assertIn('access', res1.data)

        # Email login
        res2 = self.client.post(self.login_url, {'username': 'ZakkiAdnan05@gmail.com', 'password': 'MyPassword123!'})
        self.assertEqual(res2.status_code, status.HTTP_200_OK)

    def test_login_detailed_error_messages(self):
        User.objects.create_user(
            username='mr-zakki', email='zakkiadnan05@gmail.com', password='MyPassword123!'
        )
        # Nonexistent user
        res_nonexistent = self.client.post(self.login_url, {'username': 'unknown_user', 'password': 'somepassword'})
        self.assertIn(res_nonexistent.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_401_UNAUTHORIZED])
        self.assertIn("No account found matching 'unknown_user'", str(res_nonexistent.data))

        # Wrong password
        res_wrong_pw = self.client.post(self.login_url, {'username': 'mr-zakki', 'password': 'WrongPassword!'})
        self.assertIn(res_wrong_pw.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_401_UNAUTHORIZED])
        self.assertIn("Incorrect password for 'mr-zakki'", str(res_wrong_pw.data))

    def test_password_reset_success(self):
        User.objects.create_user(
            username='mr-zakki', email='zakkiadnan05@gmail.com', password='OldPassword123!'
        )
        reset_res = self.client.post('/api/auth/reset-password/', {
            'username_or_email': 'mr-zakki',
            'new_password': 'NewPassword123!'
        })
        self.assertEqual(reset_res.status_code, status.HTTP_200_OK)

        # Verify login with new password succeeds
        login_res = self.client.post(self.login_url, {
            'username': 'mr-zakki',
            'password': 'NewPassword123!'
        })
        self.assertEqual(login_res.status_code, status.HTTP_200_OK)

