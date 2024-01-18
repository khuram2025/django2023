# views.py

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import CompanyProfile
from .serializers import CompanyProfileSerializer

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_company_profile(request):
    serializer = CompanyProfileSerializer(data=request.data)
    if serializer.is_valid():
        company_profile = serializer.save(owner=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
