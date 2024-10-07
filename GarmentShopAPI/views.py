# views.py

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Company, Category
from rest_framework.permissions import IsAuthenticated
from .serializers import CompanySerializer, CategorySerializer

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

class CategoryViewSet(APIView):
    def get(self, request, pk=None):
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
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Category created successfully!", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        try:
            category = Category.objects.get(pk=pk)
            serializer = CategorySerializer(category, data=request.data)
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
