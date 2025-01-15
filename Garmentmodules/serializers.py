from rest_framework import serializers
from .models import Module, SubModule

class SubModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubModule
        fields = ['id', 'name']

class ModuleSerializer(serializers.ModelSerializer):
    sub_modules = SubModuleSerializer(many=True, required=False)

    class Meta:
        model = Module
        fields = ['id', 'name', 'sub_modules']

    def create(self, validated_data):
        sub_modules_data = validated_data.pop('sub_modules', None)
        module = Module.objects.create(**validated_data)

        # Check if sub_modules are provided
        if sub_modules_data:
            for sub_module_data in sub_modules_data:
                SubModule.objects.create(module=module, **sub_module_data)

        return module
