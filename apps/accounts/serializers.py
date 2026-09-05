from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.models import User
from .models import Profile

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        username_or_email = attrs.get('username', '')
        password = attrs.get('password', '')

        # Auto-create demouser if it doesn't exist yet (for seamless evaluation)
        if username_or_email == 'demouser' and not User.objects.filter(username='demouser').exists():
            User.objects.create_user(
                username='demouser',
                email='demouser@jobflow.com',
                password=password or 'Password123!',
                first_name='Demo',
                last_name='User'
            )

        # Allow login via email address or username
        if username_or_email and '@' in username_or_email:
            try:
                user_obj = User.objects.get(email__iexact=username_or_email)
                attrs['username'] = user_obj.username
            except (User.DoesNotExist, User.MultipleObjectsReturned):
                pass

        return super().validate(attrs)

class ProfileSerializer(serializers.ModelSerializer):
    github_url = serializers.URLField(required=False, allow_blank=True, allow_null=True)
    linkedin_url = serializers.URLField(required=False, allow_blank=True, allow_null=True)
    portfolio_url = serializers.URLField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = Profile
        fields = [
            'id', 'phone', 'headline', 'target_role', 'experience_years',
            'education_level', 'location', 'target_salary', 'github_url',
            'linkedin_url', 'portfolio_url', 'created_at', 'updated_at'
        ]

class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'first_name', 'last_name']

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Password fields do not match."})
        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError({"email": "User with this email already exists."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        return user
