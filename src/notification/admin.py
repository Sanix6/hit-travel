from django.contrib import admin

from src.notification.models import CustomNotification, TokenFCM, UserToken


@admin.register(CustomNotification)
class CustomNotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'text')

    # class Media:
    #     js = (
    #         # '//ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js',
    #         'admin/js/jquery-3.5.1.min.js',
    #         'admin/js/notification_model.js',
    #         )
        

@admin.register(TokenFCM)
class TokenFCMAdmin(admin.ModelAdmin):
    list_display = ('id', 'token', 'created_at')


@admin.register(UserToken)
class UserTokenAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'token', 'is_active', 'updated_at', 'created_at')
    search_fields = ('user__username', 'user__id', 'id', 'token__id')
    list_filter = ('is_active',)