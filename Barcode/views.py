# barcode_app/views.py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import BarcodeItem
from .serializers import BarcodeItemSerializer
import barcode
from barcode.writer import ImageWriter
from io import BytesIO
from django.core.files.base import ContentFile
import base64
import os

class BarcodeGenerateAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = BarcodeItemSerializer(data=request.data)
        if serializer.is_valid():
            item_name = serializer.validated_data['item_name']
            description = serializer.validated_data['description']
            size = serializer.validated_data['size']
            mrp = serializer.validated_data['mrp']

            # Combine fields for unique barcode content
            barcode_content = f"{item_name}-{description}-{size}-{mrp}"
            
            # Generate the barcode
            barcode_class = barcode.get_barcode_class('code128')
            barcode_image = barcode_class(barcode_content, writer=ImageWriter())

            # Save barcode image to a file
            file_path = f"Barcode\barcode\m{barcode_content}.png"
            barcode_image.save(file_path)

            # Optionally, store the generated file in a variable as binary data
            with open(file_path, "rb") as image_file:
                barcode_data = image_file.read()

            # If needed, encode the image to base64 for API response
            image_data = base64.b64encode(barcode_data).decode('utf-8')
            
            # Respond with the file path or base64 data as needed
            return Response({"file_path": file_path, "barcode_base64": image_data}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
