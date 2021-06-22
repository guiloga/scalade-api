from django.contrib.auth import authenticate, login, logout
from rest_framework.authentication import CSRFCheck
from rest_framework.exceptions import ParseError, PermissionDenied
from rest_framework.permissions import BasePermission
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_200_OK, HTTP_400_BAD_REQUEST, \
    HTTP_401_UNAUTHORIZED
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from api.serializers.auth import BusinessSignUpSerializer, UserSignUpSerializer, SignInSerializer
from api.serializers.accounts import BusinessExtentedSerializer, UserExtentedSerializer


class CSRFTokenProtection(BasePermission):
    message = 'CSRF verification failed.'

    def has_permission(self, request, view):
        self._enforce_csrf(request)
        return True

    def _enforce_csrf(self, request):
        """
        Enforce CSRF validation LIKE session based authentication

        That method has been intentionally extracted (or copied)
        from rest_framework.authentication.SessionAuthentication..
        """
        def dummy_get_response(request):  # pragma: no cover
            return None

        check = CSRFCheck(dummy_get_response)
        # populates request.META['CSRF_COOKIE'], which is used in process_view()
        check.process_request(request)
        reason = check.process_view(request, None, (), {})
        if reason:
            # CSRF failed, bail with explicit error message
            raise PermissionDenied('CSRF Failed: %s' % reason)


class SignUpView(APIView):
    """
    API View for Account registration: either a Business or a User account.
    """
    permission_classes = [CSRFTokenProtection | AllowAny]

    def post(self, request, type_):
        if type_ == 'business':
            sign_up_serializer_type = BusinessSignUpSerializer
            resource_serializer_type = BusinessExtentedSerializer
        elif type_ == 'user':
            sign_up_serializer_type = UserSignUpSerializer
            resource_serializer_type = UserExtentedSerializer
        else:
            raise ParseError("Invalid 'type' value: "
                             "valid sign up types are either 'business' or 'user'.")
        sign_up_serializer = sign_up_serializer_type(data=request.data)
        sign_up_serializer.is_valid(raise_exception=True)
        resource = sign_up_serializer.save()
        resource_serializer = resource_serializer_type(resource)
        return Response(
            resource_serializer.data,
            status=HTTP_201_CREATED)


class SignInView(APIView):
    """
    API View for Account login: either a Business or a User account.
    """
    permission_classes = [CSRFTokenProtection | AllowAny]

    def post(self, request, type_):
        serializer = SignInSerializer(
            data={**request.data, 'auth_type': type_})
        serializer.is_valid(raise_exception=True)
        auth_params = {'password': serializer.validated_data['password']}
        if type_ == 'email':
            auth_params['email'] = serializer.validated_data['identifier']
        else:
            # To avoid confusion: the username field of the UserModel is 'auth_id'.
            # So we use the authenticate() function in which username kwarg
            # corresponds to the 'auth_id' field of our UserModel that is used to authenticate
            # not the 'username' field.
            auth_params['username'] = serializer.validated_data['identifier']
        account = authenticate(request, **auth_params)
        if account:
            login(request, account)
            return Response(data={'success': True},
                            status=HTTP_200_OK)
        else:
            return Response(data={'success': False,
                                  'error': 'Invalid Password. '
                                           'Try again, or reset your password.'},
                            status=HTTP_401_UNAUTHORIZED)


class SignOutView(APIView):
    """
    API View for Account signout.
    """
    permission_classes = [CSRFTokenProtection | AllowAny]

    def post(self, request):
        if not request.user.is_authenticated:
            return Response(status=HTTP_400_BAD_REQUEST)
        logout(request)
        return Response(status=HTTP_200_OK)


class ResetPasswordView(APIView):
    """
    API view for Account password recovery.
    """

    def post(self, request):
        pass
