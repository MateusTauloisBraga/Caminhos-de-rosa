from django.contrib import admin
from django.utils import timezone

from .models import Kilometer


@admin.action(description="Marcar PIX como confirmado")
def mark_confirmed(modeladmin, request, queryset):
    queryset.update(status=Kilometer.Status.CONFIRMED, confirmed_at=timezone.now())


@admin.action(description="Reprovar e liberar KM")
def mark_available(modeladmin, request, queryset):
    queryset.update(
        status=Kilometer.Status.AVAILABLE,
        sponsor_name="",
        donor_email="",
        donor_phone="",
        amount=None,
        pix_receipt="",
        donor_message="",
        confirmed_at=None,
    )


@admin.register(Kilometer)
class KilometerAdmin(admin.ModelAdmin):
    list_display = ("number", "status", "sponsor_name", "amount", "donor_phone", "updated_at")
    list_filter = ("status",)
    search_fields = ("number", "sponsor_name", "donor_email", "donor_phone")
    ordering = ("number",)
    actions = (mark_confirmed, mark_available)
    readonly_fields = ("created_at", "updated_at", "confirmed_at")

    fieldsets = (
        ("Quilômetro", {"fields": ("number", "status", "confirmed_at")}),
        ("Apoiador", {"fields": ("sponsor_name", "donor_email", "donor_phone", "amount")}),
        ("PIX", {"fields": ("pix_receipt", "donor_message")}),
        ("Controle", {"fields": ("created_at", "updated_at")}),
    )
