from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Image, ChatbotConversation

# Custom admin for CustomUser
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    # Customize the fields displayed in the admin panel
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('bio', 'images')}),
    )
    list_display = ('username', 'email', 'is_staff', 'is_active', 'bio')  # Fields displayed in the list view
    search_fields = ('username', 'email', 'bio')  # Fields searchable in the admin panel
    filter_horizontal = ('images', 'groups', 'user_permissions')  # Makes ManyToManyFields easier to manage

# Custom admin for Image
@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'description', 'image')  # Fields displayed in the list view
    search_fields = ('description', 'user__username')  # Allow searching by user or description
    list_filter = ('user',)  # Filter images by user

# Custom admin for ChatbotConversation
@admin.register(ChatbotConversation)
class ChatbotConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at')  # Fields displayed in the list view
    search_fields = ('user__username',)  # Allow searching by user
    list_filter = ('created_at',)  # Filter conversations by creation date
