from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import RoleBasedUser, Module, SubModule
from .serializers import RoleBasedUserSerializer

class RoleBasedUserCreateView(APIView):
    def post(self, request):
        data = request.data
        modules_data = data.get('modules', [])

        # Handle creation of modules and sub-modules
        for module_data in modules_data:
            module_name = module_data.get('name')
            module, _ = Module.objects.get_or_create(name=module_name)

            # Process sub-modules if provided
            sub_modules_data = module_data.get('sub_modules', [])
            for sub_module_data in sub_modules_data:
                sub_module_name = sub_module_data.get('name')
                SubModule.objects.get_or_create(name=sub_module_name, module=module)

        # Create the RoleBasedUser instance
        serializer = RoleBasedUserSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": True, "data": serializer.data}, status=status.HTTP_201_CREATED)

        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)



class RoleBasedUserDetailView(APIView):
    def get(self, request, username):
        try:
            # Fetch the RoleBasedUser instance by username
            user = RoleBasedUser.objects.get(username=username)

            # Serialize the user data, including modules and sub-modules
            serializer = RoleBasedUserSerializer(user)
            return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)
        except RoleBasedUser.DoesNotExist:
            return Response(
                {"success": False, "error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )
