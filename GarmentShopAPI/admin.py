from django.contrib import admin
from .models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# Register your models here.
class AdminModel(BaseUserAdmin):
    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ["id","user_name", "is_admin"]
    list_filter = ["is_admin"]
    fieldsets = [
        ('User Credential', {"fields": ["user_name", "password"]}),
        ("Permissions", {"fields": ["is_admin"]}),
    ]
    #  ("Personal info", {"fields": ["user_name"]}),
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = [
        (
            None,
            {
                "classes": ["wide"],
                "fields": ["user_name", "password1", "password2"],
            },
        ),
    ]
    search_fields = ["user_name"]
    ordering = ["user_name","id"]
    filter_horizontal = []


# Now register the new UserAdmin...
admin.site.register(User, AdminModel)
