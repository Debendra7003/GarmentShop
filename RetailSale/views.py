from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import OrderSerializer
from rest_framework.permissions import IsAuthenticated
from .renderers import UserRenderer  # Assuming this exists for custom rendering
from .models import Order
from decimal import Decimal, InvalidOperation
from django.db.models import F,Sum
from django.db import transaction
from GarmentShopAPI.models import Item, ItemSize  # Import Item and ItemSize models
from RetailSale.models import Order
from django.utils.dateparse import parse_date  # Import parse_date
from django.db.models.functions import TruncDate
import json
from calendar import month_name
from django.db.models.functions import TruncDate, TruncMonth, TruncYear
from datetime import date



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
                        "bil l_number": order.bill_number,
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
            grand_total = Decimal(request.data.get('grand_total', 0))  # Default to 0 if not present
            discount = Decimal(request.data.get('discount', 0))        # Default to 0 if not present
            tax = Decimal(request.data.get('tax', 0))                  # Default to 0 if not present
        except (TypeError, ValueError,InvalidOperation):
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
            "saletype":order.saletype,
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

class CustomerSummaryView(APIView):
     def post(self, request):
        """
        Accept fullname and retrieve total sales summary for that user.
        """
        fullname = request.data.get("fullname")
        
        if not fullname:
            return Response({"error": "Fullname is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Assuming 'customer' is the field that relates to the user (adjust if necessary)
        orders = (
            Order.objects
            .filter(fullname=fullname, items__isnull=False)  # Adjust this based on your model's relationship
            .prefetch_related('items')  # Prefetch related items to optimize queries
        )

        total_amount = Decimal('0.00')
        total_quantity = 0

        # Loop through orders and calculate total sales
        for order in orders:
            # Add total_price directly from the Order table
            total_amount += order.total_price
            
            # Add the quantity of items in the order
            for item in order.items.all():
                total_quantity += item.unit  # Summing up item units

        # Calculate average amount per unit (if there are any units sold)
        average_amount = total_amount / total_quantity if total_quantity > 0 else Decimal('0.00')

        # Prepare the response data
        response_data = {
            "fullname": fullname,
            "total_amount": str(total_amount),  # Ensure the total amount is converted to string for consistency
            "total_quantity": total_quantity,
            "average_amount": str(average_amount)  # Average amount per unit
        }

        return Response(response_data, status=status.HTTP_200_OK)
    
     def get(self, request):
        """
        Retrieve sales summary for all users, including total amount, total quantity, and average amount.
        """
        # Retrieve all orders with related items (prefetch to avoid multiple queries)
        orders = (
            Order.objects
            .filter(items__isnull=False)  # Ensure that the order has related items
            .prefetch_related('items')    # Prefetch related items to optimize queries
        )

        user_sales_data = {}

        # Loop through orders and aggregate sales data by customer
        for order in orders:
            fullname = order.fullname  # Adjust field name as needed

            if fullname not in user_sales_data:
                user_sales_data[fullname] = {
                    "total_amount": Decimal('0.00'),
                    "total_quantity": 0
                }

            # Add total_price from Order model
            user_sales_data[fullname]["total_amount"] += order.total_price

            # Add quantity from related items
            for item in order.items.all():
                user_sales_data[fullname]["total_quantity"] += item.unit

        # Prepare the response data with calculated averages
        response_data = []
        for fullname, data in user_sales_data.items():
            total_amount = data["total_amount"]
            total_quantity = data["total_quantity"]

            # Calculate average amount per unit (if there are any units sold)
            average_amount = total_amount / total_quantity if total_quantity > 0 else Decimal('0.00')

            response_data.append({
                "fullname": fullname,
                "total_amount": str(total_amount),  # Ensure the total amount is converted to string
                "total_quantity": total_quantity,
                "average_amount": str(average_amount)  # Average amount per unit
            })

        return Response(response_data, status=status.HTTP_200_OK)


#Get API for dashboard section

class DailySalesView(APIView):
    def get(self, request):
        """
        Retrieve daily sales report including date, sale type, total amount, and total units.
        """
        # Get the current date
        current_date = date.today()

        # Query to calculate daily sales data
        daily_sales = (
            Order.objects
            .filter(items__isnull=False)  # Ensure that the order has related items
            .values(
                date=TruncDate('created_at'),  # Group by date
                sale_type=F('saletype')        # Annotate sale_type
            )
            .annotate(
                total_amount=Sum(F('items__unit') * F('items__unit_price')),  # Calculate total amount
                total_unit=Sum('items__unit')  # Calculate total units
            )
            .order_by('date', 'sale_type')  # Order results
        )

        # Aggregate current date sales
        current_day_sales = []
        for entry in daily_sales:
            if entry['date'] == current_date:
                current_day_sales.append({
                    "date": current_date.strftime('%Y-%m-%d'),
                    "total_amount": str(entry['total_amount']),
                    "total_units": entry['total_unit']
                })

        # Sum up total amounts for current date sales
        total_current_day_amount = sum(Decimal(e['total_amount']) for e in current_day_sales) if current_day_sales else Decimal('0')
        total_current_day_units = sum(e['total_units'] for e in current_day_sales) if current_day_sales else 0

        # Construct the response data
        response_data = {
            "message": "Daily sales report retrieved successfully.",
            "current_date": current_date.strftime('%Y-%m-%d'),
            "current_day_sales": [
                {
                    "date": current_date.strftime('%Y-%m-%d'),
                    "total_amount": str(total_current_day_amount),
                    "total_units": total_current_day_units
                }
            ],
            "all_sales": [
                {
                    "date": entry['date'].strftime('%Y-%m-%d'),
                    "sale_type": entry['sale_type'],
                    "total_amount": str(entry['total_amount']),
                    "total_units": entry['total_unit']
                }
                for entry in daily_sales
            ]
        }

        return Response(response_data, status=status.HTTP_200_OK)
class MonthlySalesView(APIView):
    def get(self, request):
        """
        Retrieve monthly sales report including month and year, sale type, total amount, and total units.
        """
        # Get the current month and year
        current_year = date.today().year
        current_month = date.today().strftime('%B')

        # Query to calculate monthly sales data
        monthly_sales = (
            Order.objects
            .filter(items__isnull=False)  # Ensure that the order has related items
            .values(
                month=TruncMonth('created_at'),  # Group by month
                year=TruncYear('created_at'),  # Group by year
                sale_type=F('saletype')         # Annotate sale_type
            )
            .annotate(
                total_amount=Sum(F('items__unit') * F('items__unit_price')),  # Calculate total amount
                total_unit=Sum('items__unit')  # Calculate total units
            )
            .order_by('year', 'month', 'sale_type')  # Order results
        )

        # Aggregate current month sales
        current_month_sales = []
        for entry in monthly_sales:
            if entry['month'].strftime('%B') == current_month and entry['year'].year == current_year:
                current_month_sales.append({
                    "month": entry['month'].strftime('%B %Y'),
                    "year": entry['year'].year,
                    "total_amount": str(entry['total_amount']),
                    "total_units": entry['total_unit']
                })

        # Sum up total amounts for current month sales
        total_current_month_amount = sum(Decimal(e['total_amount']) for e in current_month_sales) if current_month_sales else Decimal('0')
        total_current_month_units = sum(e['total_units'] for e in current_month_sales) if current_month_sales else 0

        # Construct the response data
        response_data = {
            "message": "Monthly sales report retrieved successfully.",
            "current_month": f"{current_month} {current_year}",
            "current_month_sales": [
                {
                    "month": f"{current_month} {current_year}",
                    "total_amount": str(total_current_month_amount),
                    "total_units": total_current_month_units
                }
            ],
            "all_sales": [
                {
                    "month": entry['month'].strftime('%B %Y'),
                    "year": entry['year'].year,
                    "sale_type": entry['sale_type'],
                    "total_amount": str(entry['total_amount']),
                    "total_units": entry['total_unit']
                }
                for entry in monthly_sales
            ]
        }

        return Response(response_data, status=status.HTTP_200_OK)

class YearlySalesView(APIView):
    def get(self, request):
        """
        Retrieve yearly sales report including year, total amount, and total units.
        """
        # Get the current year
        current_year = date.today().year

        # Query to calculate yearly sales data
        yearly_sales = (
            Order.objects
            .filter(items__isnull=False)  # Ensure that the order has related items
            .values(
                year=TruncYear('created_at'),  # Group by year
                sale_type=F('saletype'),       # Annotate sale_type
                category=F('items__category'),  # Annotate category
            )
            .annotate(
                total_amount=Sum(F('items__unit') * F('items__unit_price')),  # Calculate total amount
                total_unit=Sum('items__unit')  # Calculate total units
            )
            .order_by('year', 'sale_type', 'category')  # Order results
        )

        # Aggregate current year sales
        current_year_sales = []
        for entry in yearly_sales:
            if entry['year'].year == current_year:
                current_year_sales.append({
                    "year": current_year,
                    "total_amount": str(entry['total_amount']),
                    "total_units": entry['total_unit']
                })

        # Sum up total amounts for current year sales
        total_current_year_amount = sum(Decimal(e['total_amount']) for e in current_year_sales) if current_year_sales else Decimal('0')
        total_current_year_units = sum(e['total_units'] for e in current_year_sales) if current_year_sales else 0

        # Construct the response data
        response_data = {
            "message": "Yearly sales report retrieved successfully.",
            "current_year": current_year,
            "current_year_sales": [
                {
                    "year": current_year,
                    "total_amount": str(total_current_year_amount),
                    "total_units": total_current_year_units
                }
            ],
            "all_sales": [
                {
                    "year": entry['year'].year,
                    "sale_type": entry['sale_type'],
                    "category": entry['category'],
                    "total_amount": str(entry['total_amount']),
                    "total_units": entry['total_unit']
                }
                for entry in yearly_sales
            ]
        }

        return Response(response_data, status=status.HTTP_200_OK)