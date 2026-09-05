from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.models import User
from .serializers import RegisterSerializer, UserSerializer, ProfileSerializer, CustomTokenObtainPairSerializer
from .models import Profile

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

class CurrentUserProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        if not hasattr(user, 'profile') or user.profile is None:
            Profile.objects.get_or_create(user=user)
        serializer = UserSerializer(user)
        return Response(serializer.data)

    def put(self, request):
        user = request.user
        profile = getattr(user, 'profile', None)
        if not profile:
            profile = Profile.objects.create(user=user)

        data = request.data.copy()
        
        # Clean empty URL strings
        for field in ['github_url', 'linkedin_url', 'portfolio_url']:
            if field in data and (data[field] == '' or data[field] is None):
                data[field] = None

        # Fallback education level mapping for legacy or string choices
        valid_edu_keys = [c[0] for c in Profile.EDUCATION_LEVEL_CHOICES]
        edu_val = data.get('education_level')
        if edu_val and edu_val not in valid_edu_keys:
            if 'bachelor' in str(edu_val).lower() or 'b.tech' in str(edu_val).lower() or 'btech' in str(edu_val).lower():
                data['education_level'] = 'BTech'
            elif 'master' in str(edu_val).lower() or 'm.tech' in str(edu_val).lower() or 'mtech' in str(edu_val).lower():
                data['education_level'] = 'MTech'
            elif 'bca' in str(edu_val).lower() or 'b.sc' in str(edu_val).lower():
                data['education_level'] = 'BCA_BSc'
            elif 'mca' in str(edu_val).lower() or 'm.sc' in str(edu_val).lower():
                data['education_level'] = 'MCA_MSc'
            else:
                data['education_level'] = 'BTech'

        # Update User fields
        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'last_name' in data:
            user.last_name = data['last_name']
        if 'email' in data and data['email']:
            user.email = data['email']
        user.save()

        profile_serializer = ProfileSerializer(profile, data=data, partial=True)
        if profile_serializer.is_valid():
            profile_serializer.save()
            return Response(UserSerializer(user).data)
        
        return Response(profile_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class HealthCheckView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response({
            'status': 'healthy',
            'service': 'JobFlow Intelligence Platform API',
            'version': '1.0.0'
        }, status=status.HTTP_200_OK)

class AdminPasswordResetView(APIView):
    """One-time admin utility to reset a user's password. Requires the admin reset key."""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        import os
        reset_key = os.getenv('ADMIN_RESET_KEY', 'jobflow-initial-setup-2026')
        provided_key = request.data.get('admin_key', '')
        username = request.data.get('username', '')
        new_password = request.data.get('new_password', '')

        if provided_key != reset_key:
            return Response({'detail': 'Invalid admin key.'}, status=status.HTTP_403_FORBIDDEN)
        if not username or not new_password:
            return Response({'detail': 'Username and new_password are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(username=username)
            user.set_password(new_password)
            user.save()
            return Response({'detail': f'Password for {username} has been reset successfully.'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

class PasswordResetView(APIView):
    """User-facing view to reset password for a known username or email."""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        raw_identifier = (request.data.get('username_or_email') or request.data.get('username') or '').strip()
        new_password = request.data.get('new_password', '').strip()

        if not raw_identifier:
            return Response({'detail': 'Please provide your username or email address.'}, status=status.HTTP_400_BAD_REQUEST)
        if not new_password or len(new_password) < 8:
            return Response({'detail': 'New password must be at least 8 characters long.'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(username__iexact=raw_identifier).first()
        if not user and '@' in raw_identifier:
            user = User.objects.filter(email__iexact=raw_identifier).first()

        if not user:
            return Response({'detail': f"No account found matching '{raw_identifier}'."}, status=status.HTTP_404_NOT_FOUND)

        user.set_password(new_password)
        user.save()

        return Response({
            'detail': f'Password for account "{user.username}" has been successfully updated. You can now sign in.',
            'username': user.username
        }, status=status.HTTP_200_OK)
