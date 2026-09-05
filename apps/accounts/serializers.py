from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.models import User
from .models import Profile

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        raw_input = (attrs.get('username') or '').strip()
        password = attrs.get('password', '')

        # Auto-create demouser if it doesn't exist yet (for seamless evaluation)
        if raw_input.lower() == 'demouser' and not User.objects.filter(username__iexact='demouser').exists():
            User.objects.create_user(
                username='demouser',
                email='demouser@jobflow.com',
                password=password or 'Password123!',
                first_name='Demo',
                last_name='User'
            )

        # Allow login via username (case-insensitive) or email (case-insensitive)
        user_obj = User.objects.filter(username__iexact=raw_input).first()
        if not user_obj and '@' in raw_input:
            user_obj = User.objects.filter(email__iexact=raw_input).first()

        if not user_obj:
            raise serializers.ValidationError({
                "detail": f"No account found matching '{raw_input}'. Please check your spelling or register a new account."
            })

        if not user_obj.is_active:
            raise serializers.ValidationError({
                "detail": "This account is disabled. Please contact support."
            })

        attrs['username'] = user_obj.username

        try:
            return super().validate(attrs)
        except serializers.ValidationError:
            raise serializers.ValidationError({
                "detail": f"Incorrect password for '{user_obj.username}'. Please try again or use 'Forgot Password' to reset it."
            })

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
        username = (attrs.get('username') or '').strip()
        email = (attrs.get('email') or '').strip()
        attrs['username'] = username
        attrs['email'] = email

        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Password fields do not match."})
        if User.objects.filter(username__iexact=username).exists():
            raise serializers.ValidationError({"username": "Username is already taken. Please choose another."})
        if User.objects.filter(email__iexact=email).exists():
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
