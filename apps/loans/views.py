from datetime import datetime, timedelta

from django.db import transaction, IntegrityError
from django.utils import timezone

from drf_spectacular.utils import extend_schema
from rest_framework import status

from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.loans.choices import LoanState
from apps.loans.models import Loan, LoanTerm
from apps.loans.serializers import (
    LoanSerializer, LoanApproveInputSerializer, LoanCreateInputSerializer, LoanListQuerySerializer
)


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

        try:
            with transaction.atomic():
                serializer = self.get_serializer(instance, data=request.data, partial=True)
                if serializer.is_valid(raise_exception=True):
                    # Partial update
                    self.perform_update(serializer)

                    if request.data.get('state') == LoanState.APPROVED:
                        # Update approved_date and approved_by
                        instance.approved_date = timezone.now()
                        instance.approved_by = request.user
                        instance.save()

                        # Create loan terms here (weekly)
                        loan_amount = instance.amount
                        loan_term = instance.term

                        # Calculate loan term amount
                        calculate_term_amount = round(loan_amount / loan_term, 2)
                        final_amount_diff = round(loan_amount - (calculate_term_amount * loan_term), 2)

                        loan_terms = list()
                        due_date = instance.approved_date
                        for term in range(loan_term):
                            # Add diff to last payment
                            if term == (loan_term - 1):
                                calculate_term_amount = calculate_term_amount + final_amount_diff

                            # Calculate due_date (weekly)
                            due_date = due_date + timedelta(days=7)

                            # For bulk create loan terms
                            loan_terms.append(
                                LoanTerm(
                                    loan=instance,
                                    amount=calculate_term_amount,
                                    due_date=due_date
                                )
                            )
                        # Bulk create loan terms
                        LoanTerm.objects.bulk_create(loan_terms, batch_size=1000)
                return Response(serializer.data)
        except IntegrityError as e:
            transaction.rollback()
            return Response(
               data={"error": str(e)},
               status=status.HTTP_400_BAD_REQUEST
           )

    @extend_schema(request=LoanApproveInputSerializer)
    @action(
        methods=['post'],
        detail=True,
        url_path='loan-repayment'
    )
    def loan_payment(self, request, *args, **kwargs):
        pass
