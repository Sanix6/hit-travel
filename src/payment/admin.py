from django.contrib import admin
from src.payment.models import Transaction

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['status', 'name', 'user', 'amount', 'rid']
    ordering = ["-created_at"]
