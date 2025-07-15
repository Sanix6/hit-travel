from django.contrib import admin
from .models import DeviceToken, Notifications


@admin.register(DeviceToken)
class DeviceTokenAdmin(admin.ModelAdmin):
    list_display = ("user", "device_token", "created_at")
    search_fields = ("user__username", "device_token")
    list_filter = ("created_at",)
    ordering = ("-created_at",)


@admin.register(Notifications)
class NotificationsAdmin(admin.ModelAdmin):
    list_display = ("title", "sendtoall", "display_devices")
    search_fields = ("title", "description")
    list_filter = ("sendtoall",)
    ordering = ("-id",)

    def display_devices(self, obj):
        return ", ".join([str(device) for device in obj.devices.all()]) if obj.devices.exists() else "Все"

    display_devices.short_description = "Устройства"

