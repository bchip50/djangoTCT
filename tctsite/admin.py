from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Profile, Style, Location, Message, Meeting, Course, Resource, Post
from django.contrib.auth.models import User

# Register your models here.
class UserProfileInline(admin.StackedInline):
    model = Profile

class NewUserAdmin(UserAdmin):
    inlines = [UserProfileInline]

admin.site.unregister(User)
admin.site.register(User, NewUserAdmin)
admin.site.register(Style)
admin.site.register(Location)
admin.site.register(Message)
admin.site.register(Meeting)
admin.site.register(Course)
admin.site.register(Resource)
admin.site.register(Post)
