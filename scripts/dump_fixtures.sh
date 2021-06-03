#!/bin/bash

#################
# Dump Fixtures #
#################
# Dumps all models data to a .json fixtures
# Launch it from scalade-api/ root repo dir and virtualenv activated.

# Dump all data
echo "Dumping all models data .."
python manage.py dumpdata -a > fixtures/all.json
echo -e "done!\n"

# Dump accounts data
echo "Dumping all accounts models data .."
python manage.py dumpdata accounts.AccountModel > fixtures/accounts.json
python manage.py dumpdata accounts.WorkspaceModel > fixtures/workspaces.json
python manage.py dumpdata accounts.UserModel > fixtures/users.json
python manage.py dumpdata accounts.BusinessModel > fixtures/businesses.json
echo -e "done!\n"

# Dump streams data
echo "Dumping all streams models data .."
python manage.py dumpdata streams.FunctionInstanceLogMessageModel > fixtures/function_instance_log_messages.json
python manage.py dumpdata streams.FunctionTypeModel > fixtures/function_types.json
python manage.py dumpdata streams.FunctionInstanceModel > fixtures/function_instances.json
python manage.py dumpdata streams.StreamModel > fixtures/streams.json
python manage.py dumpdata streams.VariableModel > fixtures/variables.json
echo -e "done!\n"