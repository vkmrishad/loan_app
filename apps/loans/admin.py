from django.contrib import admin

from apps.loans.models import Loan, LoanTerm

@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    search_fields = (
        "id", "user__first_name", "user__last_name", "user__username", "user__email", "term", "state"
    )
    list_display = (
        "id", "user", "amount", "term", "state", "approved_by", "approved_date"
    )
    list_filter = ("user", "term", "state", "approved_by", "approved_date")


@admin.register(LoanTerm)
class LoanAdmin(admin.ModelAdmin):
    search_fields = (
        "id", "loan__id", "loan__user__first_name", "loan__user__last_name", "loan__user__username",
        "loan__user__email", "status"
    )
    list_display = (
        "id", "loan", "amount", "due_date", "status", "paid_date"
    )
    list_filter = ("due_date", "status", "paid_date")
