from rest_framework import generics, permissions, status
from django.db.models import Q
from .models import Interview, InterviewQuestion
from .serializers import InterviewSerializer, InterviewQuestionSerializer

class InterviewListCreateView(generics.ListCreateAPIView):
    serializer_class = InterviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Interview.objects.filter(user=self.request.user)
        status_param = self.request.query_params.get('status', None)
        if status_param and status_param != 'ALL':
            queryset = queryset.filter(status=status_param)
        return queryset.order_by('interview_date')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class InterviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = InterviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Interview.objects.filter(user=self.request.user)

class InterviewQuestionListCreateView(generics.ListCreateAPIView):
    serializer_class = InterviewQuestionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = InterviewQuestion.objects.filter(user=self.request.user)
        
        # Search & Filter
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(company__icontains=search) |
                Q(question__icontains=search) |
                Q(role__icontains=search) |
                Q(answer__icontains=search)
            )

        difficulty = self.request.query_params.get('difficulty', None)
        if difficulty and difficulty != 'ALL':
            queryset = queryset.filter(difficulty=difficulty)

        return queryset.order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class InterviewQuestionDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = InterviewQuestionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return InterviewQuestion.objects.filter(user=self.request.user)
