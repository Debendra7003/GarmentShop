from datetime import datetime
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

    def post(self, request):
        """
        Create a new purchase entry.
        """
        serializer = PurchaseEntrySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Purchase entry created successfully!", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request):
        """
        Retrieve all purchase entries.
        """
        purchase_entries = PurchaseEntry.objects.all()
        serializer = PurchaseEntrySerializer(purchase_entries, many=True)
        return Response({
            "message": "All purchase entries retrieved successfully!",
            "data": serializer.data
        }, status=status.HTTP_200_OK)


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


class PurchaseDetailsViewSet(APIView):
    # permission_classes = [IsAuthenticated]
    # renderer_classes = [UserRenderer]

    def post(self, request):
        """
        Retrieve purchase entries within a date range and optionally filter by party_name.
        """
        from_date = request.data.get('from_date')
        to_date = request.data.get('to_date')
        party_name = request.data.get('party_name', None)

        # Validate date inputs
        if not from_date or not to_date:
            return Response({"message": "Both from_date and to_date are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Parse dates
            from_date = datetime.strptime(from_date, '%Y-%m-%d').date()
            to_date = datetime.strptime(to_date, '%Y-%m-%d').date()
        except ValueError:
            return Response({"message": "Invalid date format. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

        # Use the correct field for filtering
        query = PurchaseEntry.objects.filter(voucher_date__range=[from_date, to_date])
        if party_name:
            query = query.filter(party_name=party_name)

        # Serialize and return data
        serializer = PurchaseEntrySerializer(query, many=True)
        return Response({
            "message": "Filtered purchase entries retrieved successfully!",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

