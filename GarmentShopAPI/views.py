from django.shortcuts import render
from .renderers import UserRenderer
from .serializers import UserRegisterSerializer,UserLoginSerializer,CompanySerializer,CategorySerializer,CategoryMinimalSerializer,ItemSerializer,ItemCodeSerializer,TokenRefreshSerializer
from .serializers import DesignSerializer,DesignCreateUpdateSerializer,PartySerializer,TaxSerializer,FinancialYearSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated 
from django.contrib.auth import authenticate
from .models import Company,Category,Item,Design,Party,Tax,FinancialYear




# Create your views here.
# ----------------------for token generation-----------------------
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


# ---------------------------Registration view----------------------------
class UserRegisterView(APIView):
    renderer_classes=[UserRenderer]
    def post(self,request,format=None):
        serializer=UserRegisterSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user= serializer.save()
            return Response({'msg' : "Register Successfull"},status=status.HTTP_201_CREATED) 
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    

#---------------------------------Login View--------------------------------- 
class UserLoginView(APIView):
    renderer_classes=[UserRenderer]
    def post(self,request,format=None):
        serializer= UserLoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user_name=serializer.data.get('user_name')
            password=serializer.data.get('password')
            user = authenticate(user_name=user_name,password=password)
            if user is not None:
                response_data = {
                'user_name': user.user_name,
                'is_admin': user.is_admin}
                token= get_tokens_for_user(user)
                return Response({'msg' : "Login Successfull",'user':response_data,'Token':token},status=status.HTTP_200_OK)
            else:
                return Response({'Errors' : {'non_fields_errors':['user_name or Password is not valid']}},status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
#--------------------- Get Access Tokemn using Refresh Token ------------------------------

class TokenRefreshView(APIView):
    def post(self, request):
        serializer = TokenRefreshSerializer(data=request.data)
        if serializer.is_valid():
            refresh_token = serializer.validated_data["refresh_token"]
            try:
                refresh = RefreshToken(refresh_token)
                access_token = refresh.access_token
                return Response({"access_token": str(access_token)}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#Company view set
class CompanyViewSet(APIView):
    permission_classes=[IsAuthenticated]
    
    def get(self, request, pk=None):
        if pk is None:
            companies = Company.objects.all()
            serializer = CompanySerializer(companies, many=True)
            return Response({"message": "List of companies retrieved successfully!", "data": serializer.data}, status=status.HTTP_200_OK)
        else:
            try:
                company = Company.objects.get(pk=pk)
                serializer = CompanySerializer(company)
                return Response({"message": "Company details retrieved successfully!", "data": serializer.data}, status=status.HTTP_200_OK)
            except Company.DoesNotExist:
                return Response({"message": "Company not found."}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        serializer = CompanySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Company created successfully!", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        try:
            company = Company.objects.get(pk=pk)
            serializer = CompanySerializer(company, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "Company updated successfully!", "data": serializer.data}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Company.DoesNotExist:
            return Response({"message": "Company not found."}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        try:
            company = Company.objects.get(pk=pk)
            company.delete()
            return Response({"message": "Company deleted successfully!"}, status=status.HTTP_204_NO_CONTENT)
        except Company.DoesNotExist:
            return Response({"message": "Company not found."}, status=status.HTTP_404_NOT_FOUND)

#Catagory view set
class CategoryViewSet(APIView):
    permission_classes=[IsAuthenticated]
    def get(self, request, pk=None):
        if 'minimal' in request.path:  # Check if the request is for minimal data
            categories = Category.objects.all()
            serializer = CategoryMinimalSerializer(categories, many=True)
            return Response({"data": serializer.data}, status=status.HTTP_200_OK)
        else:
            if pk is None:
                categories = Category.objects.all()
                serializer = CategorySerializer(categories, many=True)
                return Response({"message": "List of categories retrieved successfully!", "data": serializer.data}, status=status.HTTP_200_OK)
            else:
                try:
                    category = Category.objects.get(pk=pk)
                    serializer = CategorySerializer(category)
                    return Response({"message": "Category details retrieved successfully!", "data": serializer.data}, status=status.HTTP_200_OK)
                except Category.DoesNotExist:
                    return Response({"message": "Category not found."}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        # Check for existing catagory_name before creating a new one
        if Category.objects.filter(category_name=request.data.get('category_name')).exists():
            return Response({"catagory_name": ["Category with this category name already exists."]}, 
                            status=status.HTTP_400_BAD_REQUEST)
        
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Category created successfully!", "data": serializer.data}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        try:
            category = Category.objects.get(pk=pk)

            # Check for existing catagory_name except for the current category being updated
            new_category_name = request.data.get('category_name')
            if new_category_name and new_category_name != category.category_name:
                if Category.objects.exclude(pk=pk).filter(category_name=new_category_name).exists():
                    return Response({"catagory_name": ["Category with this category name already exists."]}, 
                                    status=status.HTTP_400_BAD_REQUEST)

            # Check for existing catagory_code except for the current category being updated
            new_category_code = request.data.get('category_code')
            if new_category_code and new_category_code != category.category_code:
                if Category.objects.exclude(pk=pk).filter(category_code=new_category_code).exists():
                    return Response({"catagory_code": ["Category with this category code already exists."]}, 
                                    status=status.HTTP_400_BAD_REQUEST)

            serializer = CategorySerializer(category, data=request.data, partial=True)  # Allow partial updates
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "Category updated successfully!", "data": serializer.data}, status=status.HTTP_200_OK)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Category.DoesNotExist:
            return Response({"message": "Category not found."}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        try:
            category = Category.objects.get(pk=pk)
            category.delete()
            return Response({"message": "Category deleted successfully!"}, status=status.HTTP_204_NO_CONTENT)
        except Category.DoesNotExist:
            return Response({"message": "Category not found."}, status=status.HTTP_404_NOT_FOUND)
#Item view set
class ItemViewSet(APIView):
    permission_classes=[IsAuthenticated]
    """
    A ViewSet for managing item details.
    """

    def get(self, request, pk=None):
        """
        Retrieve a list of all items or a specific item by ID.
        - If 'pk' is provided, return the details of the specified item.
        - If 'pk' is not provided, return a list of all items.
        """
        if pk is None:
            items = Item.objects.all()  # Get all items
            serializer = ItemSerializer(items, many=True)  # Serialize the data
            return Response({"message": "List of items retrieved successfully!", "data": serializer.data}, status=status.HTTP_200_OK)
        else:
            try:
                item = Item.objects.get(pk=pk)  # Get the specific item
                serializer = ItemSerializer(item)  # Serialize the item data
                return Response({"message": "Item details retrieved successfully!", "data": serializer.data}, status=status.HTTP_200_OK)
            except Item.DoesNotExist:
                return Response({"message": "Item not found."}, status=status.HTTP_404_NOT_FOUND)
                

    def post(self, request):
        """
        Create a new item.
        """
        serializer = ItemSerializer(data=request.data)  # Create a serializer with request data
        if serializer.is_valid():  # Validate the serializer
            serializer.save()  # Save the new item
            return Response({"message": "Item created successfully!", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # Return validation errors

    def put(self, request, pk):
        """
        Update an existing item by ID.
        Allow updating individual fields.
        """
        try:
            item = Item.objects.get(pk=pk)  # Get the specific item
            serializer = ItemSerializer(item, data=request.data, partial=True)  # Allow partial updates
            if serializer.is_valid():  # Validate the serializer
                serializer.save()  # Save the updated item
                return Response({"message": "Item updated successfully!", "data": serializer.data}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # Return validation errors
        except Item.DoesNotExist:
            return Response({"message": "Item not found."}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        """
        Delete an item by ID.
        """
        try:
            item = Item.objects.get(pk=pk)  # Get the specific item
            item.delete()  # Delete the item
            return Response({"message": "Item deleted successfully!"}, status=status.HTTP_204_NO_CONTENT)  # Return 204 No Content
        except Item.DoesNotExist:
            return Response({"message": "Item not found."}, status=status.HTTP_404_NOT_FOUND)
#ItemCode view set
        
class ItemCodeViewSet(APIView):
    permission_classes=[IsAuthenticated]
    """
    API to retrieve only 'id', 'item_name', and 'item_code'.
    Uses ItemCodeSerializer.
    """

    def get(self, request, pk=None):
        if pk is None:
            items = Item.objects.all()  # Get all items
            serializer = ItemCodeSerializer(items, many=True)  # Serialize with limited fields
            return Response({"message": "List of items retrieved successfully!", "data": serializer.data}, status=status.HTTP_200_OK)
        else:
            try:
                item = Item.objects.get(pk=pk)
                serializer = ItemCodeSerializer(item)  # Serialize with limited fields
                return Response({"message": "Item details retrieved successfully!", "data": serializer.data}, status=status.HTTP_200_OK)
            except Item.DoesNotExist:
                return Response({"message": "Item not found."}, status=status.HTTP_404_NOT_FOUND)
#Design view set
            
class DesignViewSet(APIView):
    permission_classes=[IsAuthenticated]
    
    def get(self, request, pk=None):
        """
        Retrieve all designs or a specific design by ID.
        """
        if pk is None:
            designs = Design.objects.all()
            serializer = DesignSerializer(designs, many=True)
            return Response({"message": "Design list retrieved successfully!", "data": serializer.data}, status=status.HTTP_200_OK)
        else:
            try:
                design = Design.objects.get(pk=pk)
                serializer = DesignSerializer(design)
                return Response({"message": "Design details retrieved successfully!", "data": serializer.data}, status=status.HTTP_200_OK)
            except Design.DoesNotExist:
                return Response({"message": "Design not found."}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        """
        Create a new design.
        """
        serializer = DesignCreateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Design created successfully!", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        """
        Update an existing design.
        """
        try:
            design = Design.objects.get(pk=pk)
            serializer = DesignCreateUpdateSerializer(design, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "Design updated successfully!", "data": serializer.data}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Design.DoesNotExist:
            return Response({"message": "Design not found."}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        """
        Delete a design.
        """
        try:
            design = Design.objects.get(pk=pk)
            design.delete()
            return Response({"message": "Design deleted successfully!"}, status=status.HTTP_204_NO_CONTENT)
        except Design.DoesNotExist:
            return Response({"message": "Design not found."}, status=status.HTTP_404_NOT_FOUND)
#Party view set
class PartyViewSet(APIView):
    permission_classes=[IsAuthenticated]
    
    def get(self, request, pk=None):
        """
        Retrieve all parties or a specific party by ID.
        """
        if pk is None:
            parties = Party.objects.all()
            serializer = PartySerializer(parties, many=True)
            return Response({"message": "Party list retrieved successfully!", "data": serializer.data}, status=status.HTTP_200_OK)
        else:
            try:
                party = Party.objects.get(pk=pk)
                serializer = PartySerializer(party)
                return Response({"message": "Party details retrieved successfully!", "data": serializer.data}, status=status.HTTP_200_OK)
            except Party.DoesNotExist:
                return Response({"message": "Party not found."}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        """
        Create a new party.
        """
        serializer = PartySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Party created successfully!", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        """
        Update an existing party.
        """
        try:
            party = Party.objects.get(pk=pk)
            serializer = PartySerializer(party, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "Party updated successfully!", "data": serializer.data}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Party.DoesNotExist:
            return Response({"message": "Party not found."}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        """
        Delete a party.
        """
        try:
            party = Party.objects.get(pk=pk)
            party.delete()
            return Response({"message": "Party deleted successfully!"}, status=status.HTTP_204_NO_CONTENT)
        except Party.DoesNotExist:
            return Response({"message": "Party not found."}, status=status.HTTP_404_NOT_FOUND)
#Tax view set
class TaxViewSet(APIView):
    permission_classes=[IsAuthenticated]
    def get(self, request, pk=None):
        if pk:
            try:
                tax = Tax.objects.get(pk=pk)
                serializer = TaxSerializer(tax)
                return Response({"message": "Tax details retrieved successfully!", "data": serializer.data}, status=status.HTTP_200_OK)
            except Tax.DoesNotExist:
                return Response({"message": "Tax not found."}, status=status.HTTP_404_NOT_FOUND)
        else:
            taxes = Tax.objects.all()
            serializer = TaxSerializer(taxes, many=True)
            return Response({"message": "Tax list retrieved successfully!", "data": serializer.data}, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = TaxSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Tax created successfully!", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        try:
            tax = Tax.objects.get(pk=pk)
            serializer = TaxSerializer(tax, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "Tax updated successfully!", "data": serializer.data}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Tax.DoesNotExist:
            return Response({"message": "Tax not found."}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        try:
            tax = Tax.objects.get(pk=pk)
            tax.delete()
            return Response({"message": "Tax deleted successfully!"}, status=status.HTTP_204_NO_CONTENT)
        except Tax.DoesNotExist:
            return Response({"message": "Tax not found."}, status=status.HTTP_404_NOT_FOUND)
#Financial Year view
class FinancialYearViewSet(APIView):
    permission_classes=[IsAuthenticated]

    def get(self, request, pk=None):
        """
        Retrieve all financial years or a specific one by ID.
        """
        if pk is None:
            financial_years = FinancialYear.objects.all()
            serializer = FinancialYearSerializer(financial_years, many=True)
            return Response({"message": "Financial year list retrieved successfully!", "data": serializer.data}, status=status.HTTP_200_OK)
        else:
            try:
                financial_year = FinancialYear.objects.get(pk=pk)
                serializer = FinancialYearSerializer(financial_year)
                return Response({"message": "Financial year details retrieved successfully!", "data": serializer.data}, status=status.HTTP_200_OK)
            except FinancialYear.DoesNotExist:
                return Response({"message": "Financial year not found."}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        """
        Create a new financial year.
        """
        serializer = FinancialYearSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Financial year created successfully!", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        """
        Update an existing financial year.
        """
        try:
            financial_year = FinancialYear.objects.get(pk=pk)
            serializer = FinancialYearSerializer(financial_year, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "Financial year updated successfully!", "data": serializer.data}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except FinancialYear.DoesNotExist:
            return Response({"message": "Financial year not found."}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        """
        Delete a financial year.
        """
        try:
            financial_year = FinancialYear.objects.get(pk=pk)
            financial_year.delete()
            return Response({"message": "Financial year deleted successfully!"}, status=status.HTTP_204_NO_CONTENT)
        except FinancialYear.DoesNotExist:
            return Response({"message": "Financial year not found."}, status=status.HTTP_404_NOT_FOUND)