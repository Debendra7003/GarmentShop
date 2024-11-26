from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import PartyInformationSerializer
from decimal import Decimal
from django.shortcuts import get_object_or_404
from .models import PartyInformation



class PartyInformationView(APIView):
    def post(self, request):
        serializer = PartyInformationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class CalculatePaymentMethod2AmountView(APIView):
    # permission_classes = [IsAuthenticated]
    # renderer_classes=[UserRenderer]

    def post(self,request):
        """Calculate the amount for payment method2 """
        try:
            total_price=Decimal(request.data.get('total_price'))
            payment_amount1=Decimal(request.data.get('payment_amount1'))
        except (TypeError, ValueError, Decimal.InvalidOperation):
            return Response({"error": "Invalid input. Please provide valid numbers for total_price and payment_method1_amount."}, status=status.HTTP_400_BAD_REQUEST)
        
        #calculation of payment_method2_amount
        payment_amount2=total_price-payment_amount1

        #return response of calulated amount of payment_method1
        return Response({"payment_method2_amount": str(payment_amount2)}, status=status.HTTP_200_OK)
    
class InvoiceDetailView(APIView):
    def get(self, request, invoicenumber):
        party = get_object_or_404(PartyInformation, invoicenumber=invoicenumber)
        serializer = PartyInformationSerializer(party)
        return Response(serializer.data, status=status.HTTP_200_OK)