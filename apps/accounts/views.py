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
        serializer = UserSerializer(request.user)
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
