# barcode_app/views.py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView,View
from .models import BarcodeItem,BarcodeGen
from .serializers import BarcodeItemSerializer,BarcodeSerializer
import barcode
from django.http import JsonResponse
from barcode.writer import ImageWriter
from io import BytesIO
from django.core.files.base import ContentFile
import base64
from barcode import Code128
from PIL import Image, ImageDraw, ImageFont
import random
import io
import json
from django.views.decorators.csrf import csrf_exempt





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



class GenerateBarcodeView(APIView):
    # @csrf_exempt
    def post(self, request, *args, **kwargs):
        # Parse JSON data
        try:    
            data = request.data
            item_name = data.get("item_name")
            item_size = data.get("item_size")
            item_price = data.get("item_price")
            shop_name = data.get("shop_name")
            quantity = data.get("quantity", 1)  # Default to 1 if not provided

            # Validate shop_name length
            if len(shop_name) > 25:
                raise ValueError("shop_name cannot exceed 25 characters.")

            response_data = []

            for _ in range(quantity):
                # Generate a unique serial number based on shop name, item size, and a random number
                serial_number = f"{shop_name[:2].upper()}{item_size}{random.randint(1000, 9999)}"

                # Generate the barcode image
                barcode = Code128(serial_number, writer=ImageWriter())
                barcode_image = barcode.render(writer_options={"font_size": 1,
                                                            "text_distance": 1,
                                                            "module_width": 0.2,
                                                            "module_height": 5,
                                                            "write_text": False})

                # Create a blank image for adding additional text (like item details and shop name)
                width, height = barcode_image.size
                new_image = Image.new("RGB", (width + 40, height + 100), "white")
                new_image.paste(barcode_image, (20, 80))

                # Add text (item details, shop name) to the image
                draw = ImageDraw.Draw(new_image)
                try:
                    font = ImageFont.truetype("arial.ttf", 15)
                    font_bold = ImageFont.truetype("arialbd.ttf", 15)
                except IOError:
                    font = ImageFont.load_default()
                    font_bold = font

                # # Calculate the width of the shop name text and center it
                # shop_name_width = draw.textsize(shop_name, font=font_bold)[0]
                # shop_name_position = (width // 2 - shop_name_width // 2, 10)

                # # Draw the shop name centered at the top
                # draw.text(shop_name_position, shop_name, font=font_bold, fill="black")
                # Get the width of the shop_name text for positioning
                shop_name_width, _ = draw.textbbox((0, 0), shop_name, font=font_bold)[2:]

                draw.text((20, 35), item_name.upper(), font=font, fill="black")
                draw.text((20, 50), f"Size : {item_size}", font=font, fill="black")
                draw.text((20, 65), f"Price: {item_price}/-", font=font, fill="black")
                draw.text((width  - shop_name_width, 10), shop_name.upper(), font=font_bold, fill="black")
                draw.text((width // 2 - 15, height + 70), serial_number.upper(), font=font, fill="black")

                # Save barcode to in-memory file
                buffer = io.BytesIO()
                new_image.save(buffer, "PNG")
                buffer.seek(0)

                # Save barcode image and details to the database
                barcode_instance = BarcodeGen(
                    shop_name=shop_name,
                    item_name=item_name,
                    item_size=item_size,
                    item_price=item_price,
                    serial_number=serial_number
                )
                barcode_instance.barcode_image.save(f"{serial_number}.png", ContentFile(buffer.read()))
                barcode_instance.save()

                # Serialize barcode instance
                serializer = BarcodeSerializer(barcode_instance)
                response_data.append(serializer.data)

            return JsonResponse({"barcodes": response_data})
        except ValueError as e:
            # Catch specific errors and return them in the response
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # Catch any other unexpected errors
            return Response({"error": "An unexpected error occurred", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)