from django.db import models


class LoanState(models.TextChoices):
    PENDING = "pending", "Pending"
    APPROVED = "approved", "Approved"


class LoanTermStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    PAID = "paid", "Paid"
