from django.db import models

class Module(models.Model):
    name = models.CharField(max_length=100)  # Name of the module (e.g., "Configurations")

    def __str__(self):
        return self.name

class SubModule(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name="sub_modules")  # Link to the parent module
    name = models.CharField(max_length=100)  # Name of the sub-module (e.g., "General Settings")

    def __str__(self):
        return self.name

class RoleBasedUser(models.Model):
    role = models.CharField(max_length=50)  # Role of the user (e.g., "Admin")
    username = models.CharField(max_length=100, unique=True)  # Unique username
    modules = models.ManyToManyField(Module)  # Many-to-many relationship to modules (which contain sub-modules)
    is_active = models.BooleanField(default=True)  # Whether the user is active

    def __str__(self):
        return self.username
