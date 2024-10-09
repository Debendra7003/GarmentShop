from django.shortcuts import render
from .renderers import UserRenderer
from .serializers import UserRegisterSerializer,UserLoginSerializer,CompanySerializer,CatagorySerializer,CatagoryMinimalSerializer,ItemSerializer,ItemCodeSerializer,TokenRefreshSerializer
from .serializers import DesignSerializer,DesignCreateUpdateSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated 
from django.contrib.auth import authenticate
from .models import Company,Catagory,Item,Design




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


class CatagoryViewSet(APIView):
    def get(self, request, pk=None):
        if 'minimal' in request.path:  # Check if the request is for minimal data
            catagories = Catagory.objects.all()
            serializer = CatagoryMinimalSerializer(catagories, many=True)
            return Response({"data": serializer.data}, status=status.HTTP_200_OK)
        else:
            if pk is None:
                catagories = Catagory.objects.all()
                serializer = CatagorySerializer(catagories, many=True)
                return Response({"message": "List of categories retrieved successfully!", "data": serializer.data}, status=status.HTTP_200_OK)
            else:
                try:
                    catagory = Catagory.objects.get(pk=pk)
                    serializer = CatagorySerializer(catagory)
                    return Response({"message": "Category details retrieved successfully!", "data": serializer.data}, status=status.HTTP_200_OK)
                except Catagory.DoesNotExist:
                    return Response({"message": "Category not found."}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        # Check for existing catagory_name before creating a new one
        if Catagory.objects.filter(catagory_name=request.data.get('catagory_name')).exists():
            return Response({"catagory_name": ["Category with this category name already exists."]}, 
                            status=status.HTTP_400_BAD_REQUEST)
        
        serializer = CatagorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Category created successfully!", "data": serializer.data}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        try:
            catagory = Catagory.objects.get(pk=pk)

            # Check for existing catagory_name except for the current category being updated
            new_catagory_name = request.data.get('catagory_name')
            if new_catagory_name and new_catagory_name != catagory.catagory_name:
                if Catagory.objects.exclude(pk=pk).filter(catagory_name=new_catagory_name).exists():
                    return Response({"catagory_name": ["Category with this category name already exists."]}, 
                                    status=status.HTTP_400_BAD_REQUEST)

            # Check for existing catagory_code except for the current category being updated
            new_catagory_code = request.data.get('catagory_code')
            if new_catagory_code and new_catagory_code != catagory.catagory_code:
                if Catagory.objects.exclude(pk=pk).filter(catagory_code=new_catagory_code).exists():
                    return Response({"catagory_code": ["Category with this category code already exists."]}, 
                                    status=status.HTTP_400_BAD_REQUEST)

            serializer = CatagorySerializer(catagory, data=request.data, partial=True)  # Allow partial updates
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "Category updated successfully!", "data": serializer.data}, status=status.HTTP_200_OK)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Catagory.DoesNotExist:
            return Response({"message": "Category not found."}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        try:
            catagory = Catagory.objects.get(pk=pk)
            catagory.delete()
            return Response({"message": "Category deleted successfully!"}, status=status.HTTP_204_NO_CONTENT)
        except Catagory.DoesNotExist:
            return Response({"message": "Category not found."}, status=status.HTTP_404_NOT_FOUND)

class ItemViewSet(APIView):
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
        
class ItemCodeViewSet(APIView):
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
            
class DesignViewSet(APIView):
    
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