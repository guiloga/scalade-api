from uuid import uuid4

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import MinLengthValidator
from django.utils import timezone
from common.contracts import ModelContract
from .managers import WorkspaceManager, AccountManager, UserManager, BusinessManager
from scaladecore.entities import WorkspaceEntity, AccountEntity, BusinessEntity, UserEntity


class WorkspaceModel(ModelContract):
    uuid = models.UUIDField(primary_key=True,
                            default=uuid4,
                            editable=False,
                            verbose_name='Resource Identifier')
    created = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=50)
    business = models.ForeignKey('accounts.BusinessModel',
                                 related_name='workspaces',
                                 on_delete=models.CASCADE,
                                 help_text='The Business that this workspace belongs to.')

    objects = WorkspaceManager()

    class Meta:
        ordering = ['-created', ]
        db_table = 'workspaces'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'business'], name='unique_name'),
        ]
        verbose_name = 'Workspace'

    def __str__(self):
        return f'{self.business.organization_slug}:{self.name}'

    @property
    def to_entity(self):
        return WorkspaceEntity(
            uuid=self.uuid,
            created=self.created,
            name=self.name,
            business=self.business.to_entity, )


class AccountModel(ModelContract, PermissionsMixin, AbstractBaseUser):
    uuid = models.UUIDField(primary_key=True,
                            default=uuid4,
                            editable=False,
                            verbose_name='Resource Identifier')
    created = models.DateTimeField(auto_now_add=True)
    auth_id = models.CharField(
        error_messages={
            'unique': 'An account with that auth_id already exists.'},
        help_text='It is the authentication identifier for login, '
                  'composed by (organization_slug:username).',
        max_length=150,
        unique=True,
        verbose_name='auth id')
    username = models.CharField(
        help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.',
        max_length=150,
        validators=[UnicodeUsernameValidator()],
        verbose_name='username')
    email = models.EmailField(
        blank=False, null=False, unique=True, max_length=254, verbose_name='email address',
        help_text='Required. 254 characters or fewer.')
    password = models.CharField(max_length=128, verbose_name='password')
    is_staff = models.BooleanField(
        default=False,
        help_text='Designates whether the user can log into the admin site.',
        verbose_name='staff status')
    is_superuser = models.BooleanField(
        default=False,
        help_text='Designates that this account has all permissions '
                  'without explicitly assigning them.',
        verbose_name='superuser status')
    is_active = models.BooleanField(
        default=True,
        help_text='Designates whether this user should be treated as active. '
                  'Unselect this instead of deleting accounts.',
        verbose_name='active status')
    date_joined = models.DateTimeField(
        default=timezone.now, verbose_name='date joined')
    last_login = models.DateTimeField(
        blank=True, null=True, verbose_name='last login')
    groups = models.ManyToManyField(
        'auth.Group',
        blank=True,
        help_text='The groups this user belongs to.'
                  'A user will get all permissions granted to each of their groups.',
        related_name='account_set',
        related_query_name='account',
        verbose_name='groups')
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='account_set',
        related_query_name='account',
        verbose_name='user permissions')
    workspaces = models.ManyToManyField(WorkspaceModel,
                                        blank=True,
                                        related_name='accounts',
                                        help_text='Workspaces related to this account.',
                                        verbose_name='related workspaces')

    USERNAME_FIELD = 'auth_id'
    REQUIRED_FIELDS = ('username', 'email',)

    objects = AccountManager()

    class Meta:
        ordering = ['-created', ]
        db_table = 'accounts'
        verbose_name = 'Account'

    def __str__(self):
        return f'{self.uuid}'

    @property
    def to_entity(self) -> AccountEntity:
        return AccountEntity(
            uuid=self.uuid,
            created=self.created,
            auth_id=self.auth_id,
            username=self.username,
            email=self.email,
            date_joined=self.date_joined,
            last_login=self.last_login, )


class BusinessModel(ModelContract):
    uuid = models.UUIDField(primary_key=True,
                            default=uuid4,
                            editable=False,
                            verbose_name='Resource Identifier')
    created = models.DateTimeField(auto_now_add=True)
    master_account = models.OneToOneField(AccountModel,
                                          related_name='business',
                                          on_delete=models.CASCADE)
    organization_name = models.CharField(max_length=150,
                                         validators=[
                                             MinLengthValidator(limit_value=4), ])
    organization_slug = models.SlugField(max_length=150,
                                         unique=True,
                                         validators=[
                                             MinLengthValidator(limit_value=4), ])
    # company_acronym = models.CharField(max_length=50, unique=True)
    # company_logo = models.ImageField(null=True)

    objects = BusinessManager()

    class Meta:
        ordering = ['-created', ]
        db_table = 'business'
        verbose_name = 'Business'
        verbose_name_plural = 'Businesses'

    def __str__(self):
        return f'{self.organization_name}'

    @property
    def to_entity(self) -> BusinessEntity:
        return BusinessEntity(
            uuid=self.uuid,
            created=self.created,
            master_account=self.master_account.to_entity,
            organization_name=self.organization_name, )


class UserModel(ModelContract):
    uuid = models.UUIDField(primary_key=True,
                            default=uuid4,
                            editable=False,
                            verbose_name='Resource Identifier')
    created = models.DateTimeField(auto_now_add=True)
    account = models.OneToOneField(AccountModel,
                                   related_name='user',
                                   on_delete=models.CASCADE)
    business = models.ForeignKey(BusinessModel,
                                 related_name='users',
                                 on_delete=models.CASCADE)
    first_name = models.CharField(
        blank=False, null=False, max_length=150, verbose_name='first name',
        help_text='Required. 150 characters or fewer',
        validators=[
            MinLengthValidator(limit_value=2), ])
    last_name = models.CharField(blank=True, max_length=150, verbose_name='last name',
                                 validators=[
                                     MinLengthValidator(limit_value=2), ])

    objects = UserManager()

    class Meta:
        ordering = ['-created', ]
        db_table = 'users'
        verbose_name = 'User'

    def __str__(self):
        return f'{self.account.username}'

    @property
    def to_entity(self) -> UserEntity:
        return UserEntity(
            uuid=self.uuid,
            created=self.created,
            account=self.account.to_entity,
            business=self.business.to_entity,
            first_name=self.first_name,
            last_name=self.last_name, )
