from django.contrib.auth.validators import UnicodeUsernameValidator
from django.contrib.auth.password_validation import UserAttributeSimilarityValidator, \
    MinimumLengthValidator, CommonPasswordValidator, NumericPasswordValidator
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import MaxLengthValidator
from django.utils.text import slugify
from rest_framework import serializers

from api.serializers import BaseSerializer
from api.serializers.mixins import EmailValidatorMixin
from common.utils import ModelManager


class SignUpSerializer(BaseSerializer):
    email = serializers.EmailField(max_length=254)
    password = serializers.CharField(max_length=128,
                                     validators=[
                                         UserAttributeSimilarityValidator(
                                             user_attributes=('username', 'email')).validate,
                                         MinimumLengthValidator().validate,
                                         CommonPasswordValidator().validate,
                                         NumericPasswordValidator().validate, ])

    @staticmethod
    def get_account_creation_data(validated_data: dict):
        creation_data = {
            'organization_slug': validated_data['organization_slug'],
            'username': validated_data.get('username') or validated_data['organization_slug'],
            'email': validated_data['email'],
            'password': validated_data['password'],
        }
        return creation_data


class BusinessSignUpSerializer(EmailValidatorMixin, SignUpSerializer):
    organization_name = serializers.CharField(min_length=4, max_length=150)
    organization_slug = serializers.CharField(min_length=4, max_length=150,
                                              required=False)

    def create(self, validated_data):
        account_creation_data = self.get_account_creation_data(validated_data)
        account = ModelManager.handle(
            'accounts.account',
            'create_account',
            **account_creation_data,
            is_business=True, )

        business_creation_data = {
            'master_account': account,
            'organization_name': validated_data['organization_name'],
            'organization_slug': validated_data['organization_slug'],
        }
        business = ModelManager.handle(
            'accounts.business',
            'create',
            **business_creation_data, )

        return business

    def validate(self, attrs):
        organization_slug = attrs.get('organization_slug')
        if not organization_slug:
            organization_slug = slugify(attrs['organization_name'])
        validator = MaxLengthValidator(limit_value=150)
        validator(organization_slug)
        attrs['organization_slug'] = organization_slug
        try:
            ModelManager.handle(
                'accounts.business',
                'get',
                organization_slug=organization_slug, )
            raise serializers.ValidationError(
                "Invalid organization slug '%s': already exists." % organization_slug)
        except ObjectDoesNotExist:
            return attrs


class UserSignUpSerializer(EmailValidatorMixin, SignUpSerializer):
    organization_slug = serializers.CharField(min_length=4, max_length=150,
                                              required=False)
    first_name = serializers.CharField(min_length=2, max_length=150)
    last_name = serializers.CharField(min_length=2, max_length=150)
    username = serializers.CharField(max_length=150,
                                     validators=[
                                         UnicodeUsernameValidator(), ])

    def create(self, validated_data):
        account_creation_data = self.get_account_creation_data(validated_data)
        account = ModelManager.handle(
            'accounts.account',
            'create_account',
            **account_creation_data, )

        user_creation_data = {
            'account': account,
            'business': validated_data['business'],
            'first_name': validated_data['first_name'],
            'last_name': validated_data['last_name'],
        }
        user = ModelManager.handle(
            'accounts.user',
            'create',
            **user_creation_data, )

        return user

    def validate(self, attrs):
        organization_slug = attrs['organization_slug']
        try:
            business = ModelManager.handle(
                'accounts.business',
                'get',
                organization_slug=organization_slug, )
            attrs['business'] = business
        except ObjectDoesNotExist:
            raise serializers.ValidationError(
                "Invalid organization slug '%s': doesn't exist." % organization_slug)

        return attrs


class SignInSerializer(BaseSerializer):
    identifier = serializers.CharField(max_length=254)  # either an auth_id or an email address
    password = serializers.CharField(max_length=128)

    def validate(self, attrs):
        """
        It returns the corresponding UserModel instance.

        The unique validation is check that an account exists. Any additional validation logic
        for login is not performed in the serializer scope.
        """
        if self.initial_data['auth_type'] == 'email':
            id_field = 'email'
        else:
            id_field = 'auth_id'
        id_value = attrs['identifier']
        try:
            ModelManager.handle(
                'accounts.account',
                'get',
                **{id_field: id_value})
            return attrs
        except ObjectDoesNotExist:
            raise serializers.ValidationError(
                "There isn't an account with the identifier provided: '%s'" % id_value)


class ResetPasswordSerializer(BaseSerializer):
    pass
