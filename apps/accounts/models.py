from uuid import uuid4

from django.db import models


class BaseModel(models.Model):
    id = models.UUIDField(default=uuid4, primary_key=True, editable=False)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    updated = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        abstract = True
