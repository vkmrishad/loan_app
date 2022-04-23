from django.utils import timezone

from drf_spectacular.utils import extend_schema

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.loans.choices import LoanState
from apps.loans.models import Loan
from apps.loans.serializers import LoanSerializer, LoanApproveInputSerializer, LoanCreateInputSerializer, \
    LoanListQuerySerializer


class LoanViewSet(ModelViewSet):
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer
    http_method_names = ['get', 'patch', 'post']
    permission_classes = (IsAuthenticated,)

    def get_permissions(self):
        if self.action in ['partial_update', 'approve_loan']:
            self.permission_classes = (IsAdminUser,)
        return super().get_permissions()

    @extend_schema(parameters=[LoanListQuerySerializer])
    def list(self, request, *args, **kwargs):
        """
        List loans
        """
        queryset = self.get_queryset()

        query_serializer = LoanListQuerySerializer(data=request.query_params)
        query_serializer.is_valid(raise_exception=True)
        query_params = query_serializer.data

        _all = query_params.get('all')

        if not _all:
            queryset = queryset.filter(user=request.user)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(request=LoanCreateInputSerializer)
    def create(self, request, *args, **kwargs):
        """
        Create Loan
        """
        self.serializer_class = LoanCreateInputSerializer
        return super().create(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        queryset = self.get_object()

        # Check user and staff status
        if queryset.user != request.user and not request.user.is_staff:
            raise PermissionDenied()

        serializer = self.get_serializer(queryset)
        return Response(serializer.data)

    @extend_schema(request=LoanApproveInputSerializer)
    @action(
        methods=['patch'],
        detail=True,
        url_path='approve-loan'
    )
    def approve_loan(self, request, *args, **kwargs):
        """
        Approve loan by admin
        """
        instance = self.get_object()

        if instance.state == LoanState.APPROVED:
            return Response(
                data={"error": f"Loan is already {LoanState.APPROVED}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            # Partial update
            self.perform_update(serializer)

            # Update approved_date and approved_by
            instance.approved_date = timezone.now()
            instance.approved_by = request.user
            instance.save()

        return Response(serializer.data)
