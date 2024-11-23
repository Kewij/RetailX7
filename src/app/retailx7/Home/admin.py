from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Image, ChatbotConversation
import json

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
    list_display = ('id', 'user', 'short_description', 'image_preview')  # Display concise description and image preview
    search_fields = ('description', 'user__username')  # Allow searching by user or description
    list_filter = ('user',)  # Filter images by user
    readonly_fields = ('formatted_description',)  # Show JSON description as formatted and read-only in the admin form

    def short_description(self, obj):
        """Provide a truncated version of the description for the list display."""
        if isinstance(obj.description, dict):
            # Handle if description is stored as JSON
            description_text = json.dumps(obj.description)
        else:
            description_text = obj.description
        return (description_text[:50] + "...") if description_text else "-"
    short_description.short_description = "Description (Short)"  # Rename column

    def formatted_description(self, obj):
        """Show the description as a formatted JSON string in the admin detail view."""
        if isinstance(obj.description, dict):
            # Format JSON nicely if stored as a dictionary
            return json.dumps(obj.description, indent=4)
        return obj.description or "-"
    formatted_description.short_description = "Description (Formatted)"  # Rename in admin detail view

    def image_preview(self, obj):
        """Render a small preview of the uploaded image."""
        if obj.image:
            return f'<img src="{obj.image.url}" style="width: 75px; height: 75px;" />'
        return "-"
    image_preview.short_description = "Image Preview"  # Rename column
    image_preview.allow_tags = True  # Allow HTML rendering

# Custom admin for ChatbotConversation
@admin.register(ChatbotConversation)
class ChatbotConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at')  # Fields displayed in the list view
    search_fields = ('user__username',)  # Allow searching by user
    list_filter = ('created_at',)  # Filter conversations by creation date
