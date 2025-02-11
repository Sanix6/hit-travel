from django.contrib import admin
from django.utils.html import format_html

from .models import (
    AirProviders,
    AviaAgreement,
    FlightCancel,
    FlightRequest,
    Passengers,
    Segments,
)


class AviaAgreementAdmin(admin.ModelAdmin):
    def has_add_permission(self, obj):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(AviaAgreement, AviaAgreementAdmin)


@admin.register(AirProviders)
class AirProvidersAdmin(admin.ModelAdmin):
    list_display = ["id", "code", "title", "get_img"]
    list_display_links = list_display
    search_fields = ("title", "code")

    def get_img(self, obj):
        if obj.img:
            return format_html(f"<img src='{obj.img.url}' height='60' width='100'>")

    def has_add_permission(self, obj):
        return False

    get_img.short_description = "Изображение"


class PassengersAdmin(admin.StackedInline):
    model = Passengers
    extra = 0


class SegmentsInline(admin.StackedInline):
    model = Segments
    extra = 0


@admin.register(FlightRequest)
class FlightRequestAdmin(admin.ModelAdmin):
    inlines = [PassengersAdmin, SegmentsInline]
    list_display = [
        "user",
        "get_from_to",
        "book_class",
        "segment_type",
        "amount",
        "paid",
        "status",
        "created_at",
    ]
    search_fields = list_display and ['billing_number']
    list_display_links = list_display
    ordering = ["-created_at"]

    def get_from_to(self, obj):
        if obj.segments.exists():
            first_segment = obj.segments.first()
            last_segment = obj.segments.last()

            if first_segment and last_segment:
                num_segments = obj.segments.count()
                if (
                    first_segment.from_iata == last_segment.to_iata
                    and num_segments == 2
                ) or (
                    first_segment.from_iata == last_segment.to_iata and num_segments > 2
                ):
                    return f"{first_segment.from_country}/{first_segment.from_name} ✈ {first_segment.to_country}/{first_segment.to_name}"
                if first_segment.from_name != last_segment.to_name:
                    return f"{first_segment.from_country}/{first_segment.from_name} ✈ {last_segment.to_country}/{last_segment.to_name}"
        return "Информация недоступна"

    get_from_to.short_description = "Откуда - Куда"

    def segment_type(self, obj):
        if obj.segments.exists():
            num_segments = obj.segments.count()

            if num_segments == 1:
                return f"Прямой рейс"

            if (
                obj.segments.first().from_iata == obj.segments.last().to_iata
                and num_segments == 2
            ):
                return f"Туда и обратно"

            if (
                obj.segments.first().from_iata == obj.segments.last().to_iata
                and num_segments > 2
            ):
                return f"Туда и обратно с пересадкой"

            if (
                obj.segments.first().from_iata != obj.segments.last().to_iata
                and num_segments > 1
            ):
                return f"С пересадкой"

    segment_type.short_description = "Тип брони"


@admin.register(FlightCancel)
class FlightCancelAdmin(admin.ModelAdmin):
    list_display = ["id", "transaction", "flight"]
