from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import PurchaseEntry
from .serializers import PurchaseEntrySerializer
from .renderers import UserRenderer  # Assuming you have a custom renderer

class PurchaseEntryViewSet(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def get(self, request, pk=None, party_name=None):
        """
        Retrieve all purchase entries or a specific one by ID or party_name.
        """
        if pk is None and party_name is None:
            purchase_entries = PurchaseEntry.objects.all()
            serializer = PurchaseEntrySerializer(purchase_entries, many=True)
            return Response({"message": "Purchase entry list retrieved successfully!", "data": serializer.data}, status=status.HTTP_200_OK)
        
        try:
            if pk is not None:
                purchase_entry = PurchaseEntry.objects.get(pk=pk)
            else:
                purchase_entry = PurchaseEntry.objects.get(party_name=party_name)
                
            serializer = PurchaseEntrySerializer(purchase_entry)
            return Response({"message": "Purchase entry details retrieved successfully!", "data": serializer.data}, status=status.HTTP_200_OK)
        except PurchaseEntry.DoesNotExist:
            return Response({"message": "Purchase entry not found."}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        """
        Create a new purchase entry.
        """
        serializer = PurchaseEntrySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Purchase entry created successfully!", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk=None, party_name=None):
        """
        Update an existing purchase entry by ID or party_name.
        """
        try:
            if pk is not None:
                purchase_entry = PurchaseEntry.objects.get(pk=pk)
            else:
                purchase_entry = PurchaseEntry.objects.get(party_name=party_name)
                
            serializer = PurchaseEntrySerializer(purchase_entry, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "Purchase entry updated successfully!", "data": serializer.data}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except PurchaseEntry.DoesNotExist:
            return Response({"message": "Purchase entry not found."}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk=None, party_name=None):
        """
        Delete a purchase entry by ID or party_name.
        """
        try:
            if pk is not None:
                purchase_entry = PurchaseEntry.objects.get(pk=pk)
            else:
                purchase_entry = PurchaseEntry.objects.get(party_name=party_name)
                
            purchase_entry.delete()
            return Response({"message": "Purchase entry deleted successfully!"}, status=status.HTTP_204_NO_CONTENT)
        except PurchaseEntry.DoesNotExist:
            return Response({"message": "Purchase entry not found."}, status=status.HTTP_404_NOT_FOUND)

