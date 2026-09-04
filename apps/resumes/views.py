from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Resume
from .serializers import ResumeSerializer
from .parser import extract_text_from_file, parse_resume_text

class ResumeListCreateView(generics.ListCreateAPIView):
    serializer_class = ResumeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Resume.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        if serializer.validated_data.get('is_default', False):
            Resume.objects.filter(user=self.request.user).update(is_default=False)
        
        uploaded_file = self.request.FILES.get('file')
        file_name = uploaded_file.name if uploaded_file else None
        serializer.save(user=self.request.user, file_name=file_name if file_name else serializer.validated_data.get('file_name'))

class ResumeDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ResumeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Resume.objects.filter(user=self.request.user)

    def perform_update(self, serializer):
        if serializer.validated_data.get('is_default', False):
            Resume.objects.filter(user=self.request.user).exclude(id=self.get_object().id).update(is_default=False)
        
        uploaded_file = self.request.FILES.get('file')
        file_name = uploaded_file.name if uploaded_file else None
        if file_name:
            serializer.save(file_name=file_name)
        else:
            serializer.save()

class ParseResumeFileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        uploaded_file = request.FILES.get('file')
        if not uploaded_file:
            return Response({'error': 'No resume file uploaded.'}, status=status.HTTP_400_BAD_REQUEST)

        raw_text = extract_text_from_file(uploaded_file, uploaded_file.name)
        parsed_data = parse_resume_text(raw_text, filename=uploaded_file.name)
        return Response(parsed_data, status=status.HTTP_200_OK)
