from rest_framework import serializers
from .models import RoleBasedUser, Module, SubModule

class SubModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubModule
        fields = ['id', 'name']

class ModuleSerializer(serializers.ModelSerializer):
    sub_modules = SubModuleSerializer(many=True, required=False)

    class Meta:
        model = Module
        fields = ['id', 'name', 'sub_modules']

class RoleBasedUserSerializer(serializers.ModelSerializer):
    modules = ModuleSerializer(many=True, required=False)

    class Meta:
        model = RoleBasedUser
        fields = ['id', 'role', 'username', 'modules', 'is_active']

    def create(self, validated_data):
        modules_data = validated_data.pop('modules', [])
        role_based_user = RoleBasedUser.objects.create(**validated_data)

        # Handle module and sub-module creation
        for module_data in modules_data:
            sub_modules_data = module_data.pop('sub_modules', [])
            module, _ = Module.objects.get_or_create(name=module_data['name'])

            # Create sub-modules
            for sub_module_data in sub_modules_data:
                SubModule.objects.get_or_create(name=sub_module_data['name'], module=module)

            # Associate module with the user
            role_based_user.modules.add(module)

        return role_based_user
