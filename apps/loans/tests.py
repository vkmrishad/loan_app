from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token

from apps.loans.choices import LoanState, LoanTermStatus
from apps.loans.serializers import AMOUNT_MIN, TERM_MIN, AMOUNT_MAX, TERM_MAX


class LoanTestCase(APITestCase):
    def setUp(self):
        # Init Client
        self.client = APIClient()

        # Create admin user
        self.admin = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="admin@@password"
        )

        # Create admin token
        self.admin_token = Token.objects.create(user=self.admin)

        # Create user
        self.user = User.objects.create_user(
            username="user", email="user@example.com", password="user@@password"
        )

        # Create user token
        self.user_token = Token.objects.create(user=self.user)

        # Create loan with user
        self.loan1 = self.client.post(
            "/api/loans/",
            {"amount": 10000, "term": 3},
            HTTP_AUTHORIZATION=f"Token {self.user_token.key}",
        ).json()

        # Create loan with admin
        self.loan2 = self.client.post(
            "/api/loans/",
            {"amount": 20000, "term": 4},
            HTTP_AUTHORIZATION=f"Token {self.admin_token.key}",
        ).json()

    def test_api_loan_create(self):
        """
        Test loan creation endpoint
        """
        # Without authorization
        request = self.client.post(
            "/api/loans/",
            {"amount": 0, "term": 0},
        )
        self.assertEqual(request.status_code, status.HTTP_401_UNAUTHORIZED)

        # With authorization
        request = self.client.post(
            "/api/loans/",
            {"amount": 10000, "term": 3},
            HTTP_AUTHORIZATION=f"Token {self.user_token.key}",
        )
        response = request.json()
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response["amount"], 10000)
        self.assertEqual(response["term"], 3)
        self.assertEqual(response["state"], LoanState.PENDING)

    def test_api_loan_create_validation(self):
        """
        Test loan creation amount and term validation endpoint
        """
        # Minimum amount and term
        request = self.client.post(
            "/api/loans/",
            {"amount": 0, "term": 0},
            HTTP_AUTHORIZATION=f"Token {self.user_token.key}",
        )
        response = request.json()
        self.assertEqual(request.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response["amount"],
            [f"amount($) should be greater than or equal {AMOUNT_MIN}"],
        )
        self.assertEqual(
            response["term"],
            [f"term(weekly) should be greater than or equal {TERM_MIN}"],
        )

        # Maximum amount and term
        request = self.client.post(
            "/api/loans/",
            {"amount": 10000000, "term": 60},
            HTTP_AUTHORIZATION=f"Token {self.user_token.key}",
        )
        response = request.json()
        self.assertEqual(request.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response["amount"], [f"amount($) should be less than or equal {AMOUNT_MAX}"]
        )
        self.assertEqual(
            response["term"], [f"term(weekly) should be less than or equal {TERM_MAX}"]
        )

    def test_api_approve_loan(self):
        """
        Test admin approve loan endpoint
        """
        # Without authorization
        request = self.client.patch(
            f"/api/loans/{self.loan1['id']}/approve-loan/",
            {"state": "approved"},
        )
        self.assertEqual(request.status_code, status.HTTP_401_UNAUTHORIZED)

        # With authorization (normal user)
        request = self.client.patch(
            f"/api/loans/{self.loan1['id']}/approve-loan/",
            {"state": "approved"},
            HTTP_AUTHORIZATION=f"Token {self.user_token.key}",
        )
        self.assertEqual(request.status_code, status.HTTP_403_FORBIDDEN)

        # With authorization (admin user)
        request = self.client.patch(
            f"/api/loans/{self.loan1['id']}/approve-loan/",
            {"state": "approved"},
            HTTP_AUTHORIZATION=f"Token {self.admin_token.key}",
        )
        response = request.json()
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(response["state"], LoanState.APPROVED)
        self.assertEqual(response["user"], self.user.id)
        self.assertEqual(response["approved_by"], self.admin.id)
        self.assertEqual(len(response["loan_terms"]), 3)

        # With authorization (admin user) - error for already approved
        request = self.client.patch(
            f"/api/loans/{self.loan1['id']}/approve-loan/",
            {"state": "approved"},
            HTTP_AUTHORIZATION=f"Token {self.admin_token.key}",
        )
        response = request.json()
        self.assertEqual(request.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response["error"], "Loan is already approved")

    def test_api_loan_list(self):
        """
        Test list loan user specific and all endpoint
        """
        # Without authorization
        request = self.client.get(f"/api/loans/")
        self.assertEqual(request.status_code, status.HTTP_401_UNAUTHORIZED)

        # With authorization (normal user) - user specific
        request = self.client.get(
            f"/api/loans/",
            HTTP_AUTHORIZATION=f"Token {self.user_token.key}",
        )
        response = request.json()
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(response["count"], 1)

        # With authorization (admin user) - user specific
        request = self.client.get(
            f"/api/loans/",
            HTTP_AUTHORIZATION=f"Token {self.admin_token.key}",
        )
        response = request.json()
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(response["count"], 1)

        # With authorization (normal user) - ?all=true
        request = self.client.get(
            f"/api/loans/?all=True",
            HTTP_AUTHORIZATION=f"Token {self.user_token.key}",
        )
        response = request.json()
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(response["count"], 1)

        # With authorization (admin user) - ?all=true
        request = self.client.get(
            f"/api/loans/?all=True",
            HTTP_AUTHORIZATION=f"Token {self.admin_token.key}",
        )
        response = request.json()
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(response["count"], 2)

    def test_api_loan_repayment(self):
        """
        Test loan repayment endpoint
        """
        # Without authorization
        request = self.client.post(
            f"/api/loans/{self.loan1['id']}/loan-repayment/",
            {"amount": 0},
        )
        self.assertEqual(request.status_code, status.HTTP_401_UNAUTHORIZED)

        # Approve loan - (admin user)
        request = self.client.patch(
            f"/api/loans/{self.loan1['id']}/approve-loan/",
            {"state": "approved"},
            HTTP_AUTHORIZATION=f"Token {self.admin_token.key}",
        )
        response = request.json()
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(response["state"], LoanState.APPROVED)
        self.assertEqual(response["user"], self.user.id)
        self.assertEqual(response["approved_by"], self.admin.id)
        self.assertEqual(len(response["loan_terms"]), 3)

        # Validate repayment amount
        request = self.client.post(
            f"/api/loans/{self.loan1['id']}/loan-repayment/",
            {"amount": 0},
            HTTP_AUTHORIZATION=f"Token {self.user_token.key}",
        )
        response = request.json()
        self.assertEqual(request.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response["error"], "Loan repayment amount should be equal to 3333.33"
        )

        # First term repayment
        request = self.client.post(
            f"/api/loans/{self.loan1['id']}/loan-repayment/",
            {"amount": 3333.33},
            HTTP_AUTHORIZATION=f"Token {self.user_token.key}",
        )
        response = request.json()
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(response["state"], LoanState.APPROVED)
        self.assertEqual(response["loan_terms"][0]["status"], LoanTermStatus.PAID)
        self.assertEqual(response["loan_terms"][0]["paid_amount"], 3333.33)

        # Second term repayment
        request = self.client.post(
            f"/api/loans/{self.loan1['id']}/loan-repayment/",
            {"amount": 3333.33},
            HTTP_AUTHORIZATION=f"Token {self.user_token.key}",
        )
        response = request.json()
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(response["state"], LoanState.APPROVED)
        self.assertEqual(response["loan_terms"][1]["status"], LoanTermStatus.PAID)
        self.assertEqual(response["loan_terms"][1]["paid_amount"], 3333.33)

        # Third term repayment
        request = self.client.post(
            f"/api/loans/{self.loan1['id']}/loan-repayment/",
            {"amount": 3333.34},
            HTTP_AUTHORIZATION=f"Token {self.user_token.key}",
        )
        response = request.json()
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(response["state"], LoanState.PAID)
        self.assertEqual(response["loan_terms"][2]["status"], LoanTermStatus.PAID)
        self.assertEqual(response["loan_terms"][2]["paid_amount"], 3333.34)

        # Check already fully paid loan
        request = self.client.post(
            f"/api/loans/{self.loan1['id']}/loan-repayment/",
            {"amount": 3333.34},
            HTTP_AUTHORIZATION=f"Token {self.user_token.key}",
        )
        response = request.json()
        self.assertEqual(request.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response["error"], "Loan is already fully paid")

        # Check payment of unapproved loan
        request = self.client.post(
            f"/api/loans/{self.loan2['id']}/loan-repayment/",
            {"amount": 3333.34},
            HTTP_AUTHORIZATION=f"Token {self.admin_token.key}",
        )
        response = request.json()
        self.assertEqual(request.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response["error"], "Loan is not approved or loan terms does not exists"
        )
