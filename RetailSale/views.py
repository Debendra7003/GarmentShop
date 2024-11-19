from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import OrderSerializer
from rest_framework.permissions import IsAuthenticated
from .renderers import UserRenderer  # Assuming this exists for custom rendering
from .models import Order
from decimal import Decimal
class CreateOrderView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def post(self, request):
        """
        Create a new order.
        """
        serializer = OrderSerializer(data=request.data)  # No 'many=True' here
        if serializer.is_valid():
            order = serializer.save()  # Save the order and associated items

            # You need to explicitly calculate and save the grand_total and total_price
            order.total_price = order.calculate_total_price()
            order.grand_total = order.calculate_grand_total()
            order.save()  # Save the updated order with total values

            return Response({"message": "Order created successfully!", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        """
        Retrieve all orders with detailed information.
        """
        orders = Order.objects.all()
        order_list = []
        for order in orders:
            order_data = {
                "id": order.id,
                "fullname": order.fullname,
                "phone_number": order.phone_number,
                "address": order.address,
                "tax": str(order.tax) if isinstance(order.tax, Decimal) else order.tax,
                "discount": str(order.discount) if isinstance(order.discount, Decimal) else order.discount,
                "grand_total": str(order.grand_total) if isinstance(order.grand_total, Decimal) else order.grand_total,
                "total_price": str(order.total_price) if isinstance(order.total_price, Decimal) else order.total_price,
                "payment_method1": order.payment_method1,
                "payment_method2": order.payment_method2,
                "narration": order.narration,
                "payment_method1_amount": str(order.payment_method1_amount) if isinstance(order.payment_method1_amount, Decimal) else order.payment_method1_amount,
                "payment_method2_amount": str(order.payment_method2_amount) if isinstance(order.payment_method2_amount, Decimal) else order.payment_method2_amount,
                "items": [
                    {
                        "barcode": item.barcode,
                        "item_name": item.item_name,
                        "unit": item.unit,
                        "unit_price": str(item.unit_price) if isinstance(item.unit_price, Decimal) else item.unit_price,
                        "total_item_price": str(item.total_item_price) if isinstance(item.total_item_price, Decimal) else item.total_item_price
                    } for item in order.items.all()
                ]
            }
            order_list.append(order_data)
        
        return Response(order_list, status=status.HTTP_200_OK)
class CalculateTotalPriceView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def post(self, request):
        """
        Calculate the total price based on grand_total, discount, and tax.
        """
        try:
            grand_total = Decimal(request.data.get('grand_total'))
            discount = Decimal(request.data.get('discount'))
            tax = Decimal(request.data.get('tax'))
        except (TypeError, ValueError, Decimal.InvalidOperation):
            return Response({"error": "Invalid input. Please provide valid numbers for grand_total, discount, and tax."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Calculate total_price
        total_price = grand_total + tax - discount

        # Return the calculated total_price
        return Response({"total_price": str(total_price)}, status=status.HTTP_200_OK)
class CalculatePaymentMethod2AmountView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes=[UserRenderer]

    def post(self,request):
        """
        Calculate the amount for payment method2

        """
        try:
            total_price=Decimal(request.data.get('total_price'))
            payment_method1_amount=Decimal(request.data.get('payment_method1_amount'))
        except (TypeError, ValueError, Decimal.InvalidOperation):
            return Response({"error": "Invalid input. Please provide valid numbers for total_price and payment_method1_amount."}, status=status.HTTP_400_BAD_REQUEST)
        
        #calculation of payment_method2_amount
        payment_method2_amount=total_price-payment_method1_amount

        #return response of calulated amount of payment_method1
        return Response({"payment_method2_amount": str(payment_method2_amount)}, status=status.HTTP_200_OK)