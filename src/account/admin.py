from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from .models import (
    FAQ,
    Document,
    HotelTraveler,
    ManualRequests,
    Payments,
    RequestHotel,
    RequestTour,
    Traveler,
    User,
)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    save_on_top = True
    list_display = ("id", "email", "first_name", "last_name", "is_staff", "tourist_id")
    list_display_links = ("id", "email")
    search_fields = (
        "first_name",
        "last_name",
        "email",
        "phone",
        "passport_id",
        "bcard_number",
        "tourist_id",
    )
    ordering = ("-id",)

    fieldsets = (
        (None, {"fields": ("email", "password", "tourist_id", "bcard_id")}),
        (
            _("Personal info"),
            {
                "fields": (
                    "phone",
                    "whatsapp",
                    "first_name",
                    "last_name",
                    "dateofborn",
                    "gender",
                    "photo",
                    "county",
                    "passport_id",
                    "inn",
                    "date_of_issue",
                    "issued_by",
                    "validity",
                    "city",
                    "passport_front",
                    "passport_back",
                )
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
        (_("Verification"), {"fields": ("is_verified", "verification_code")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "groups",
                    "is_staff",
                    "email",
                    "phone",
                    "first_name",
                    "last_name",
                    "password1",
                    "password2",
                    "dateofborn",
                    "inn",
                    "passport_id",
                    "city",
                    "county",
                    "date_of_issue",
                    "validity",
                    "issued_by",
                ),
            },
        ),
    )

    filter_horizontal = ("user_permissions",)

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if not request.user.is_superuser:
            for fieldset in fieldsets:
                fieldset[1]["fields"] = [
                    field
                    for field in fieldset[1]["fields"]
                    if field not in ["groups", "is_staff"]
                ]
        return fieldsets


class TravelersInline(admin.StackedInline):
    model = Traveler
    extra = 0
    fields = ["first_name", "last_name", "dateofborn", "passport_id", "issued_by"]


class HotelTravelersInline(admin.StackedInline):
    model = HotelTraveler
    extra = 0
    fields = ["first_name", "last_name", "dateofborn", "passport_id", "issued_by"]


class DocumentsInline(admin.StackedInline):
    model = Document
    extra = 0


@admin.register(RequestTour)
class TourRequestAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = (
        "id",
        "first_name",
        "last_name",
        "request_number",
        "status",
        "phone",
        "created_at",
        "user",
        "tourid",
    )
    list_editable = ("status",)
    list_filter = ("status",)
    list_display_links = ("id", "first_name", "last_name", "request_number")
    search_fields = ("email", "phone", "first_name", "last_name", "inn")
    inlines = (TravelersInline, DocumentsInline)

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "pdf",
                    "manager",
                    "status",
                    "surcharge",
                    "request_number",
                    "user",
                    "first_name",
                    "last_name",
                    "phone",
                    "email",
                    "gender",
                    "dateofborn",
                    "city",
                    "country",
                    "bonuses",
                    "agreement",
                )
            },
        ),
        (
            _("Tour Info"),
            {"fields": ("operatorlink", "tourid", "price", "paid", "currency")},
        ),
        (
            _("Passport Data"),
            {
                "fields": (
                    "passport_front",
                    "passport_back",
                    "passport_id",
                    "inn",
                    "issued_by",
                    "date_of_issue",
                    "validity",
                )
            },
        ),
    )

    def get_fieldsets(self, request, obj=None):
        return self.add_fieldsets if not obj else super().get_fieldsets(request, obj)


@admin.register(RequestHotel)
class RequestHotelAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "first_name", "phone", "created_at", "status"]
    list_display_links = ["id", "user"]
    list_editable = ["status"]
    inlines = [
        HotelTravelersInline,
    ]

    def has_add_permission(self, request):
        return False


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ("id", "question")
    list_display_links = list_display


@admin.register(Payments)
class PaymentsAdmin(admin.ModelAdmin):
    list_display = ("id", "bank_name")
    list_display_links = list_display


admin.site.register(ManualRequests)
