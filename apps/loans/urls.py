from django.urls import path, include

from rest_framework import routers

from apps.loans.views import LoanViewSet

router = routers.DefaultRouter()
router.register("", LoanViewSet)

urlpatterns = [
    path("", include(router.urls)),
]