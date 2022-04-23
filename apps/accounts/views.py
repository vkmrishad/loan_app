from django.contrib.auth import get_user_model
from rest_framework import parsers
from rest_framework.authtoken.views import ObtainAuthToken

from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny

from apps.accounts.serializers import UserSerializer

User = get_user_model()


class RegisterUserView(CreateAPIView):
    """
    User registration endpoint
    """

    model = User
    permission_classes = [AllowAny]
    serializer_class = UserSerializer


class CustomObtainAuthToken(ObtainAuthToken):
    """
    Override ObtainAuthToken to fix default parser_classes
    """

    parser_classes = (parsers.JSONParser,)
