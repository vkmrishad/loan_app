from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import CASCADE
from django.utils.translation import ugettext_lazy as _

from apps.accounts.models import BaseModel
from apps.loans.choices import LoanState, LoanTermStatus

User = get_user_model()


class Loan(BaseModel):
    user = models.ForeignKey(User, on_delete=CASCADE, verbose_name=_("user"), related_name="user")
    amount = models.FloatField(_("amount"))
    term = models.IntegerField(_("term"))
    state = models.CharField(_("state"), choices=LoanState.choices, max_length=30, default=LoanState.PENDING)
    approved_by = models.ForeignKey(
        User, on_delete=CASCADE, verbose_name=_("approved_by"), null=True, blank=True, related_name="approved_by"
    )
    approved_date = models.DateTimeField(_("approved_date"), null=True, blank=True)

    def __str__(self):
        return f"{self.user}, amount: {self.amount}, terms: {self.term}"

    class Meta:
        verbose_name = _("Loan")
        verbose_name_plural = _("Loans")


class LoanTerm(BaseModel):
    loan = models.ForeignKey(Loan, on_delete=CASCADE, verbose_name=_("loan"), related_name="loan")
    amount = models.FloatField(_("amount"))
    due_date = models.DateTimeField(_("due_date"), null=True, blank=True)
    status = models.CharField(
        _("status"), choices=LoanTermStatus.choices, max_length=30, default=LoanTermStatus.PENDING
    )
    payment_date = models.DateTimeField(_("payment_date"), null=True, blank=True)

    def __str__(self):
        return f"{self.loan} -> amount: {self.amount}, due_date: {self.due_date}"

    class Meta:
        verbose_name = _("Loan Term")
        verbose_name_plural = _("Loan Terms")
