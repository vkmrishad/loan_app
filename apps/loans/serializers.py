from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from apps.loans.models import Loan, LoanTerm

# Terms in weekly
TERM_MIN = 1  # 1 week
TERM_MAX = 52  # 52 week (1 year)

# Amount in dollar
AMOUNT_MIN = 1000
AMOUNT_MAX = 1000000


class LoanTermSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanTerm
        fields = ("id", "amount", "due_date", "status", "paid_amount", "paid_date")


class LoanSerializer(serializers.ModelSerializer):
    loan_terms = serializers.SerializerMethodField()

    class Meta:
        model = Loan
        fields = (
            "id",
            "amount",
            "term",
            "state",
            "approved_date",
            "user",
            "approved_by",
            "loan_terms",
            "closed_date",
        )
        read_only_fields = ("user", "approved_by", "loan_terms", "closed_date")

    @extend_schema_field(LoanTermSerializer)
    def get_loan_terms(self, obj):
        instance = LoanTermSerializer(obj.loan_term, many=True).data
        return instance if instance else None


class LoanCreateInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = (
            "id",
            "amount",
            "term",
            "state",
            "approved_date",
            "user",
            "approved_by",
        )
        read_only_fields = ("state", "approved_date", "user", "approved_by")

    def create(self, validated_data):
        user = self.context["request"].user

        # Update user
        validated_data["user"] = user

        loan = super().create(validated_data)
        return loan

    def validate_amount(self, amount):
        if amount < AMOUNT_MIN:
            raise serializers.ValidationError(
                {"amount": f"amount($) should be greater than {AMOUNT_MIN}"}
            )
        if amount > AMOUNT_MAX:
            raise serializers.ValidationError(
                {"amount": f"amount($) should be less than {AMOUNT_MAX}"}
            )
        return amount

    def validate_term(self, term):
        if term < TERM_MIN:
            raise serializers.ValidationError(
                {"term": f"term(weekly) should be greater than {TERM_MIN}"}
            )
        if term > TERM_MAX:
            raise serializers.ValidationError(
                {"term": f"term(weekly) should be less than {TERM_MAX}"}
            )
        return term


class LoanApproveInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = ("state",)


class LoanListQuerySerializer(serializers.Serializer):
    all = serializers.BooleanField(
        required=False, default=False, help_text="List all loans"
    )


class LoanRePaymentInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanTerm
        fields = ("amount",)
