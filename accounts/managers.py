from uuid import uuid4
from django.db import models
from django.contrib.auth.models import BaseUserManager


class WorkspaceManager(models.Manager):
    def create(self, *args, **kwargs):
        workspace = super().create(*args, **kwargs)
        account = workspace.business.master_account
        account.workspaces.add(workspace)
        return workspace


class AccountManager(BaseUserManager):
    def create_account(self, username, email, password, organization_slug,
                       **kwargs):
        if not password:
            raise ValueError('Password is required, it cannot be null.')

        id_ = uuid4()
        account = self.model(
            uuid=id_,
            auth_id='%s:%s' % (organization_slug, username),
            username=username,
            email=self.normalize_email(email),
            **kwargs, )
        account.set_password(password)
        account.save(using=self._db)

        return account

    def create_superaccount(self, *args, **kwargs):
        account = self.create_account(*args, **kwargs)
        account.is_staff = True
        account.is_superuser = True
        account.save(using=self._db)

        return account


class UserManager(models.Manager):
    def create(self, *args, **kwargs):
        from .models import WorkspaceModel
        user = super().create(*args, **kwargs)
        default_workspace = '%s-%s' % (user.account.username, 'default')
        workspace = WorkspaceModel.objects.create(name=default_workspace, business=user.business)
        user.account.workspaces.add(workspace)

        return user
