from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import OrderSerializer
from rest_framework.permissions import IsAuthenticated
from .renderers import UserRenderer  # Assuming this exists for custom rendering
from .models import Order
from decimal import Decimal
from django.db.models import F,Sum
from django.db import transaction
from GarmentShopAPI.models import Item, ItemSize  # Import Item and ItemSize models
from RetailSale.models import Order
from django.utils.dateparse import parse_date  # Import parse_date
from django.db.models.functions import TruncDate
import json



class CreateOrderView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    # def post(self, request):
    #     """
    #     Create a new order.
    #     """
    #     serializer = OrderSerializer(data=request.data)  # No 'many=True' here
    #     if serializer.is_valid():
    #         order = serializer.save()  # Save the order and associated items

    #         # Calculate and save the grand_total and total_price
    #         order.total_price = order.calculate_total_price()
    #         order.grand_total = order.calculate_grand_total()
    #         order.save()  # Save the updated order with total values

    #         # Re-fetch the serialized data to include the updated fields
    #         updated_serializer = OrderSerializer(order)

    #         return Response(
    #             {
    #                 "message": "Order created successfully!",
    #                 "bill_number": order.bill_number,  # Include the bill number in the response
    #                 "data": updated_serializer.data  # Use updated serializer data
    #             },
    #             status=status.HTTP_201_CREATED
    #         )
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        """
        Create a new order and deduct stock quantities by matching item_name, category, sub_category, and size.
        """
        with transaction.atomic():  # Ensure all operations are atomic
            serializer = OrderSerializer(data=request.data)
            if serializer.is_valid():
                order = serializer.save()  # Save the order

                # Deduct stock for each item in the order
                for item_data in request.data.get('items', []):
                    try:
                        # Fetch the related Item and ItemSize based on provided fields
                        item = Item.objects.get(
                            item_name=item_data['item_name'],
                            category_item=item_data['category'],
                            sub_category=item_data.get('sub_category')  # Handle optional sub_category
                        )
                        item_size = item.sizes.get(size=item_data['size'])  # Access related size

                        # Check if stock is sufficient
                        if item_size.stock_quantity >= item_data['unit']:
                            # Deduct the stock from ItemSize
                            item_size.stock_quantity = F('stock_quantity') - item_data['unit']
                            item_size.save()
                        else:
                            return Response(
                                {"error": f"Insufficient stock for {item.item_name} (Size: {item_data['size']})."},
                                status=status.HTTP_400_BAD_REQUEST
                            )
                    except (Item.DoesNotExist, ItemSize.DoesNotExist):
                        return Response(
                            {
                                "error": f"Item not found for name {item_data['item_name']}, category {item_data['category']}, "
                                         f"sub_category {item_data.get('sub_category')} and size {item_data['size']}."
                            },
                            status=status.HTTP_400_BAD_REQUEST
                        )

                # Calculate and save totals
                order.total_price = order.calculate_total_price()
                order.grand_total = order.calculate_grand_total()
                order.save()

                # Return response with updated data
                updated_serializer = OrderSerializer(order)
                return Response(
                    {
                        "message": "Order created successfully!",
                        "bill_number": order.bill_number,
                        "data": updated_serializer.data
                    },
                    status=status.HTTP_201_CREATED
                )
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
                "bill_number": order.bill_number,
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
                "saletype":order.saletype,
                "items": [
                    {
                        "barcode": item.barcode,
                        "category":item.category,
                        "sub_category":item.sub_category,
                        "size":item.size,
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
class RetrieveOrderByBillNumberView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def get(self, request, bill_number):
        """
        Retrieve order details by bill_number.
        """
        try:
            order = Order.objects.get(bill_number=bill_number)
        except Order.DoesNotExist:
            return Response({"error": "Order not found for the provided bill number."}, status=status.HTTP_404_NOT_FOUND)

        # Serialize order details
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
            "saletype":item.saletype,
            "items": [
                {
                    "barcode": item.barcode,
                    "category":item.category,
                    "sub_category":item.sub_category,
                    "item_name": item.item_name,
                    "unit": item.unit,
                    "unit_price": str(item.unit_price) if isinstance(item.unit_price, Decimal) else item.unit_price,
                    "total_item_price": str(item.total_item_price) if isinstance(item.total_item_price, Decimal) else item.total_item_price
                } for item in order.items.all()
            ]
        }

        return Response(order_data, status=status.HTTP_200_OK)
         # Queryset to generate the report

class SalesReportView(APIView):
    def get(self, request):
        """
        Retrieve date-wise sales report with sale type, category, total amount, and total units.
        """
        # Aggregate data based on Orders
        report_data = (
            Order.objects
            .filter(items__isnull=False)  # Ensure that the order has related items
            .values(
                date=TruncDate('created_at'),  # Group by date of the order
                sale_type=F('saletype'),       # Group by sale type from Order (use an alias name)
                category=F('items__category'), # Group by category from related Item
            )
            .annotate(
                total_amount=Sum(F('items__unit') * F('items__unit_price')),  # Calculate total amount based on related Item fields
                total_unit=Sum('items__unit')  # Calculate total units based on related Item quantity
            )
            .order_by('date', 'sale_type','category')  # Order results by date and sale_type
        )

        # Prepare the response data
        report_list = []
        for entry in report_data:
            report_list.append({
                "date": entry['date'],
                "sale_type": entry['sale_type'],  # Sale type (RetailSale or BulkSale)
                "category":entry['category'],
                "total_amount": str(entry['total_amount']) if isinstance(entry['total_amount'], Decimal) else entry['total_amount'],
                "total_unit": entry['total_unit']  # Total units sold
            })

        return Response(report_list, status=status.HTTP_200_OK)

    def post(self, request):
        """
        Retrieve filtered date-wise sales report with sale type, category, total amount, and total units.
        Additionally, return the total sum of all amounts for the specified date range.
        """
        # Extract filter parameters from the request body
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        sale_type = request.data.get('sale_type')

        # Validate date input
        if start_date:
            start_date = parse_date(start_date)
            if not start_date:
                return Response({"error": "Invalid start_date format. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)
        
        if end_date:
            end_date = parse_date(end_date)
            if not end_date:
                return Response({"error": "Invalid end_date format. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

        # Build the query filters dynamically
        filters = {}
        if start_date:
            filters['created_at__date__gte'] = start_date
        if end_date:
            filters['created_at__date__lte'] = end_date
        if sale_type:
            filters['saletype'] = sale_type

        # Aggregate data based on Orders
        report_data = (
            Order.objects
            .filter(items__isnull=False, **filters)  # Apply dynamic filters
            .values(
                date=TruncDate('created_at'),  # Group by date of the order
                sale_type=F('saletype'),       # Group by sale type from Order
                category=F('items__category'), # Group by category from related Item
            )
            .annotate(
                total_amount=Sum(F('items__unit') * F('items__unit_price')),  # Calculate total amount
                total_unit=Sum('items__unit')  # Calculate total units
            )
            .order_by('date', 'sale_type', 'category')  # Order results
        )

        # Calculate the total sum of all amounts in the filtered dataset
        total_sum = report_data.aggregate(total_sum=Sum('total_amount'))['total_sum']

        # Prepare the response data
        report_list = [
            {
                "date": entry['date'],
                "sale_type": entry['sale_type'],
                "category": entry['category'],
                "total_amount": str(entry['total_amount']) if isinstance(entry['total_amount'], Decimal) else entry['total_amount'],
                "total_unit": entry['total_unit']
            }
            for entry in report_data
        ]

        # Return the response, including the summary
        return Response({
            "message": "Filtered sales report retrieved successfully.",
            "report": report_list,
            "total_sum": str(total_sum) if isinstance(total_sum, Decimal) else total_sum
        }, status=status.HTTP_200_OK)