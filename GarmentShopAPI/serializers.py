from rest_framework import serializers
from .models import User


""" ------------User registration serializers--------------"""
class UserRegisterSerializer(serializers.ModelSerializer):
    password2=serializers.CharField(style={'input_type':'password'},write_only=True)
    class Meta:
        model= User
        fields=['user_name','password','password2']

        extra_kwargs={
            'password':{'write_only':True}
        }

    #-------------------validate password & Confirm Password -----------------
    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')
        if password != password2:
            raise serializers.ValidationError("Password & Confirm password doesn't match.")
        return attrs
    
    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
    # super().create(validated_data)


""" ---------------User Login serializers-------------"""
class UserLoginSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(max_length=100)
    class Meta:
        model=User
        fields=['user_name','password']