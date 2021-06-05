import pytest

from scaladecore.entities import WorkspaceEntity, AccountEntity, BusinessEntity, UserEntity

from common.utils import ModelManager


@pytest.mark.django_db
def test_accounts_models_relationships():
    users = ModelManager.handle('accounts.user', 'all')
    for user in users:
        user_ws = user.account.workspaces.all()
        assert len(user_ws) == 1

        ws = user_ws[0]
        accounts = ws.accounts.all()
        business_account = (accounts[1]
                            if accounts[0].uuid == user.account.uuid
                            else accounts[0])
        assert len(accounts) == 2
        assert ws.name == '%s-%s' % (user.account.username, 'default')
        assert business_account == user.business.master_account


class TestWorkspaceModel:
    @pytest.mark.django_db
    def test_to_entity(self):
        workspaces = ModelManager.handle('accounts.workspace', 'all')
        for ws in workspaces:
            assert isinstance(ws.to_entity, WorkspaceEntity)


class TestAccountModel:
    @pytest.mark.django_db
    def test_to_entity(self):
        accounts = ModelManager.handle('accounts.account', 'all')
        for account in accounts:
            assert isinstance(account.to_entity, AccountEntity)


class TestBusinessModel:
    @pytest.mark.django_db
    def test_to_entity(self):
        businesses = ModelManager.handle('accounts.business', 'all')
        for bs in businesses:
            assert isinstance(bs.to_entity, BusinessEntity)


class TestUserModel:
    @pytest.mark.django_db
    def test_to_entity(self):
        users = ModelManager.handle('accounts.user', 'all')
        for user in users:
            assert isinstance(user.to_entity, UserEntity)
