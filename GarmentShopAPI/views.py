from django.shortcuts import render
from .renderers import UserRenderer
from .serializers import UserRegisterSerializer,UserLoginSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken 
from django.contrib.auth import authenticate




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
