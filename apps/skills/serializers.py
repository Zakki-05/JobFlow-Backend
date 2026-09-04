from rest_framework import serializers
from .models import Skill, UserSkill

class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'name', 'category']

class UserSkillSerializer(serializers.ModelSerializer):
    skill_details = SkillSerializer(source='skill', read_only=True)
    skill_id = serializers.PrimaryKeyRelatedField(
        queryset=Skill.objects.all(), source='skill', write_only=True
    )
    skill_name = serializers.CharField(write_only=True, required=False)
    category = serializers.CharField(write_only=True, required=False, default='Other')

    class Meta:
        model = UserSkill
        fields = [
            'id', 'skill', 'skill_id', 'skill_name', 'category',
            'skill_details', 'proficiency', 'years_experience', 'created_at'
        ]
        read_only_fields = ['skill']

    def create(self, validated_data):
        user = self.context['request'].user
        skill = validated_data.get('skill', None)
        skill_name = validated_data.pop('skill_name', None)
        category = validated_data.pop('category', 'Other')

        if not skill and skill_name:
            skill, _ = Skill.objects.get_or_create(
                name__iexact=skill_name.strip(),
                defaults={'name': skill_name.strip(), 'category': category}
            )

        user_skill, created = UserSkill.objects.update_or_create(
            user=user,
            skill=skill,
            defaults={
                'proficiency': validated_data.get('proficiency', 'Intermediate'),
                'years_experience': validated_data.get('years_experience', 1.0)
            }
        )
        return user_skill
