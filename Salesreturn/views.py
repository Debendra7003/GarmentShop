from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated 
from .serializers import ReturnSerializer

class ReturnCreateView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        serializer = ReturnSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Return created successfully!", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response({"message": "Failed to create return.", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
