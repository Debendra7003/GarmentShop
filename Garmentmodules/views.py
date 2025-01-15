from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Module
from .serializers import ModuleSerializer

class ModuleListView(APIView):
    def get(self, request):
        modules = Module.objects.all()
        serializer = ModuleSerializer(modules, many=True)
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)
class ModulePostView(APIView):
    def post(self, request):
        serializer = ModuleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": True, "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
class ModuleDeleteView(APIView):
    def delete(self, request, pk):
        try:
            # Find the module by its primary key (ID)
            module = Module.objects.get(pk=pk)
            module.delete()  # Delete the module
            return Response({"success": True, "message": "Module deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except Module.DoesNotExist:
            raise NotFound(detail="Module not found.")