from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import OrderSerializer,ItemPreviewSerializer
from rest_framework.permissions import IsAuthenticated
from .renderers import UserRenderer  # Assuming this exists for custom rendering
from .models import Order,ItemPreview,PreviewGrandTotal,StockDeduction
from decimal import Decimal
from django.db.models import F,Sum
from django.utils import timezone
from django.db import transaction
from GarmentShopAPI.models import Item, ItemSize,StockHistory  # Import Item and ItemSize models
from RetailSale.models import Order
from django.utils.dateparse import parse_date  # Import parse_date
from django.db.models.functions import TruncDate
import json
from calendar import month_name
from django.db.models.functions import TruncDate, TruncMonth, TruncYear
from datetime import date





# class CreateOrderView(APIView):
#     permission_classes = [IsAuthenticated]
#     renderer_classes = [UserRenderer]

#     def post(self, request):
#         """
#         Create a new order and deduct stock quantities by matching item_name, category, sub_category, and size.
#         """
#         with transaction.atomic():  # Ensure all operations are atomic
#             serializer = OrderSerializer(data=request.data)
#             if serializer.is_valid():
#                 order = serializer.save()  # Save the order

#                 # Deduct stock for each item in the order
#                 for item_data in request.data.get('items', []):
#                     try:
#                         # Fetch the related Item and ItemSize based on provided fields
#                         item = Item.objects.get(
#                             item_name=item_data['item_name'],
#                             category_item=item_data['category'],
#                             sub_category=item_data.get('sub_category')  # Handle optional sub_category
#                         )
#                         item_size = item.sizes.get(size=item_data['size'])  # Access related size

#                         # Check if stock is sufficient
#                         if item_size.stock_quantity >= item_data['unit']:
#                             # Deduct the stock from ItemSize
#                             item_size.stock_quantity = F('stock_quantity') - item_data['unit']
#                             item_size.save()
#                         else:
#                             return Response(
#                                 {"error": f"Insufficient stock for {item.item_name} (Size: {item_data['size']})."},
#                                 status=status.HTTP_400_BAD_REQUEST
#                             )
#                     except (Item.DoesNotExist, ItemSize.DoesNotExist):
#                         return Response(
#                             {
#                                 "error": f"Item not found for name {item_data['item_name']}, category {item_data['category']}, "
#                                          f"sub_category {item_data.get('sub_category')} and size {item_data['size']}."
#                             },
#                             status=status.HTTP_400_BAD_REQUEST
#                         )

#                 # Calculate and save totals
#                 order.total_price = order.calculate_total_price()
#                 order.grand_total = order.calculate_grand_total()
#                 order.save()

#                 # Return response with updated data
#                 updated_serializer = OrderSerializer(order)
#                 return Response(
#                     {
#                         "message": "Order created successfully!",
#                         "bill_number": order.bill_number,
#                         "data": updated_serializer.data
#                     },
#                     status=status.HTTP_201_CREATED
#                 )
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CreateOrderView(APIView):
    permission_classes = [IsAuthenticated]  # Adjust according to your authentication setup

    def post(self, request):
        """
        Create a new order and deduct stock quantities by matching item_name, category, sub_category, and size.
        This will also store the stock deduction before modifying the stock.
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
                            sub_category=item_data.get('sub_category', '')  # Handle optional sub_category
                        )
                        item_size = item.sizes.get(size=item_data['size'])  # Access related size

                        # Save the stock deduction before modifying the stock
                        StockDeduction.objects.create(
                            item_size=item_size,
                            change_quantity=item_data['unit'],  # Deduct the quantity based on the order
                            change_date=timezone.now()  # Record the current date and time
                        )

                        # Check if stock is sufficient
                        if item_size.stock_quantity >= item_data['unit']:
                            # Deduct the stock from ItemSize
                            item_size.stock_quantity -= item_data['unit']
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

                # Calculate and save totals for the order
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

class GetOrderDetailsView(APIView):
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
    #  def post(self, request):
    #     """
    #     Accept fullname and retrieve total sales summary for that user.
    #     """
    #     fullname = request.data.get("fullname")
        
        
    #     if not fullname:
    #         return Response({"error": "Fullname is required."}, status=status.HTTP_400_BAD_REQUEST)

    #     # Assuming 'customer' is the field that relates to the user (adjust if necessary)
    #     orders = (
    #         Order.objects
    #         .filter(fullname=fullname, items__isnull=False)  # Adjust this based on your model's relationship
    #         .prefetch_related('items')  # Prefetch related items to optimize queries
    #     )

    #     total_amount = Decimal('0.00')
    #     total_quantity = 0

    #     # Loop through orders and calculate total sales
    #     for order in orders:
        
    #         # Add total_price directly from the Order table
    #         total_amount += order.total_price
            
    #         # Add the quantity of items in the order
    #         for item in order.items.all():
    #             total_quantity += item.unit  # Summing up item units

    #     # Calculate average amount per unit (if there are any units sold)
    #     average_amount = total_amount / total_quantity if total_quantity > 0 else Decimal('0.00')

    #     # Prepare the response data
    #     response_data = {
    #         "fullname": fullname,
    #         "total_amount": str(total_amount),  # Ensure the total amount is converted to string for consistency
    #         "total_quantity": total_quantity,
    #         "average_amount": str(average_amount)  # Average amount per unit
    #     }

    #     return Response(response_data, status=status.HTTP_200_OK)

   def post(self, request):
    """
    Accept fullname and retrieve sales summary for that user, including all associated phone numbers.
    """
    fullname = request.data.get("fullname")
    
    if not fullname:
        return Response({"error": "Fullname is required."}, status=status.HTTP_400_BAD_REQUEST)

    # Fetch all orders by the given fullname
    orders = (
        Order.objects
        .filter(fullname=fullname, items__isnull=False)
        .prefetch_related('items')
    )

    if not orders.exists():
        return Response({"error": "No orders found for this user."}, status=status.HTTP_404_NOT_FOUND)

    # Group data by phone_number
    phone_number_data = {}
    for order in orders:
        phone_number = order.phone_number
        if phone_number not in phone_number_data:
            phone_number_data[phone_number] = {
                "fullname": fullname,
                "phone_number": phone_number,
                "total_amount": Decimal('0.00'),
                "total_quantity": 0,
            }

        # Add total_price from the order
        phone_number_data[phone_number]["total_amount"] += order.total_price

        # Add total quantity of items in the order
        for item in order.items.all():
            phone_number_data[phone_number]["total_quantity"] += item.unit

    # Prepare the response data
    response_data = []
    for data in phone_number_data.values():
        total_amount = data["total_amount"]
        total_quantity = data["total_quantity"]

        # Calculate average amount per unit
        average_amount = total_amount / total_quantity if total_quantity > 0 else Decimal('0.00')
        data["total_amount"] = str(total_amount)
        data["average_amount"] = str(average_amount)

        response_data.append(data)

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
            phone_number = order.phone_number  # Adjust field name as needed

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
                "phone_number":phone_number,
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

#Item Preview
class ItemPreviewAPIView(APIView):

    def post(self, request, *args, **kwargs):
        items = request.data.get('items', [])
        if not isinstance(items, list):
            return Response({"error": "Invalid data format. 'items' should be a list."}, status=status.HTTP_400_BAD_REQUEST)

        created_items = []
        errors = []

        for item_data in items:
            serializer = ItemPreviewSerializer(data=item_data)
            if serializer.is_valid():
                created_item = serializer.save()
                created_items.append(serializer.data)
            else:
                errors.append(serializer.errors)

        # Update and retrieve grand_total
        grand_total = PreviewGrandTotal.update_grand_total()

        response_data = {
            "message": "Items processed successfully.",
            "created_items": created_items,
            "errors": errors,
            "grand_total": grand_total
        }

        return Response(response_data, status=status.HTTP_201_CREATED if created_items else status.HTTP_400_BAD_REQUEST)



#StockHistory Report


# class ItemStockSummaryView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         # Get the date parameter if provided, otherwise include all dates
#         requested_date = request.query_params.get('date')
        
#         if requested_date:
#             try:
#                 date_filter = date.fromisoformat(requested_date)  # Parse the date string
#             except ValueError:
#                 return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)
#         else:
#             date_filter = None  # No date filtering if not provided

#         # Fetch data
#         item_data = []
#         items = Item.objects.all()

#         for item in items:
#             sizes = item.sizes.all()
#             for size in sizes:
#                 # Group totals by date for StockHistory
#                 stock_history_totals = StockHistory.objects.filter(
#                     item_size=size,
#                     **({"change_date__date": date_filter} if date_filter else {})
#                 ).values('change_date__date').annotate(total_added=Sum('change_quantity'))

#                 # Group totals by date for StockDeduction
#                 stock_deduction_totals = StockDeduction.objects.filter(
#                     item_size=size,
#                     **({"change_date__date": date_filter} if date_filter else {})
#                 ).values('change_date__date').annotate(total_deducted=Sum('change_quantity'))

#                 # Combine the dates and calculate totals
#                 date_totals = {}
#                 for entry in stock_history_totals:
#                     date_key = entry['change_date__date']
#                     if date_key not in date_totals:
#                         date_totals[date_key] = {'total_quantity_added': 0, 'total_deducted_quantity': 0}
#                     date_totals[date_key]['total_quantity_added'] += entry['total_added']

#                 for entry in stock_deduction_totals:
#                     date_key = entry['change_date__date']
#                     if date_key not in date_totals:
#                         date_totals[date_key] = {'total_quantity_added': 0, 'total_deducted_quantity': 0}
#                     date_totals[date_key]['total_deducted_quantity'] += entry['total_deducted']

#                 # Format date-wise totals for the response
#                 date_summary = [
#                     {
#                         "date": date_key,
#                         "total_quantity_added": totals['total_quantity_added'],
#                         "total_deducted_quantity": totals['total_deducted_quantity']
#                     }
#                     for date_key, totals in sorted(date_totals.items())
#                 ]

#                 # Add item size-specific data to the response
#                 item_data.append({
#                     "item_name": item.item_name,
#                     "item_code": item.item_code,
#                     "category": item.category_item,
#                     "sub_category": item.sub_category,
#                     "size": size.size,
#                     "stock_quantity": size.stock_quantity,
#                     "date_summary": date_summary,  # Date-wise summary of totals
#                 })

#         return Response({"data": item_data}, status=200)



class ItemStockSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get the date parameter if provided, otherwise include all dates
        requested_date = request.query_params.get('date')

        if requested_date:
            try:
                date_filter = date.fromisoformat(requested_date)  # Parse the date string
            except ValueError:
                return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)
        else:
            date_filter = None  # No date filtering if not provided

        # Fetch data
        item_data = []
        items = Item.objects.all()

        for item in items:
            sizes = item.sizes.all()
            for size in sizes:
                # Fetch stock history grouped by date
                stock_history_by_date = StockHistory.objects.filter(
                    item_size=size,
                    **({"change_date__date": date_filter} if date_filter else {})
                ).values('change_date__date').annotate(
                    total_added=Sum('change_quantity')
                )

                # Fetch stock deduction grouped by date
                stock_deduction_by_date = StockDeduction.objects.filter(
                    item_size=size,
                    **({"change_date__date": date_filter} if date_filter else {})
                ).values('change_date__date').annotate(
                    total_deducted=Sum('change_quantity')
                )

                # Combine the results by date
                date_map = {}
                for entry in stock_history_by_date:
                    date_map[entry['change_date__date']] = {
                        "total_quantity_added": entry['total_added'],
                        "total_deducted_quantity": 0
                    }
                for entry in stock_deduction_by_date:
                    if entry['change_date__date'] in date_map:
                        date_map[entry['change_date__date']]["total_deducted_quantity"] = entry['total_deducted']
                    else:
                        date_map[entry['change_date__date']] = {
                            "total_quantity_added": 0,
                            "total_deducted_quantity": entry['total_deducted']
                        }

                # Add data for each date
                for change_date, totals in date_map.items():
                    item_data.append({
                        "date": change_date,
                        "item_name": item.item_name,
                        "item_code": item.item_code,
                        "category": item.category_item,
                        "sub_category": item.sub_category,
                        "size": size.size,
                        "current_stock_quantity": size.stock_quantity,
                        "original_stock_quantity": size.stock_quantity - totals["total_quantity_added"] + totals["total_deducted_quantity"],
                        "total_quantity_added": totals["total_quantity_added"],
                        "total_deducted_quantity": totals["total_deducted_quantity"],
                    })

        return Response({"data": item_data}, status=200)