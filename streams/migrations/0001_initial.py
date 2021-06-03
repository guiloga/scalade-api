# Generated by Django 3.1.4 on 2021-06-03 11:15

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='FunctionInstanceModel',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='Resource Identifier')),
                ('position', models.TextField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('initialized', models.DateTimeField(null=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('completed', models.DateTimeField(null=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('running', 'Running'), ('blocked', 'Blocked'), ('canceled', 'Canceled'), ('completed', 'Completed')], default='pending', max_length=50)),
            ],
            options={
                'verbose_name': 'Function Instance',
                'db_table': 'function_instances',
                'ordering': ['-created'],
            },
        ),
        migrations.CreateModel(
            name='VariableModel',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='Resource Identifier')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('iot', models.CharField(choices=[('input', 'INPUT'), ('output', 'OUTPUT')], default='input', max_length=50)),
                ('id_name', models.CharField(max_length=50)),
                ('type', models.CharField(max_length=50)),
                ('charset', models.CharField(default='utf-8', max_length=50)),
                ('bytes', models.BinaryField()),
                ('rank', models.IntegerField()),
                ('function_instance', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='variables', to='streams.functioninstancemodel')),
            ],
            options={
                'verbose_name': 'Variable',
                'db_table': 'variables',
                'ordering': ['-created'],
            },
        ),
        migrations.CreateModel(
            name='StreamModel',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='Resource Identifier')),
                ('name', models.CharField(max_length=50)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('pushed', models.DateTimeField(null=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('finished', models.DateTimeField(null=True)),
                ('status', models.CharField(choices=[('settled', 'Settled'), ('pushed', 'Pushed'), ('paused', 'Paused'), ('cancelled', 'Cancelled'), ('finished', 'Finished')], default='settled', max_length=50)),
                ('account', models.ForeignKey(help_text='The creator and owner of the stream.', on_delete=django.db.models.deletion.CASCADE, related_name='streams', to=settings.AUTH_USER_MODEL)),
                ('workspace', models.ForeignKey(help_text='The Workspace that stream belongs to', on_delete=django.db.models.deletion.CASCADE, related_name='streams', to='accounts.workspacemodel')),
            ],
            options={
                'verbose_name': 'Stream',
                'db_table': 'streams',
                'ordering': ['-created'],
            },
        ),
        migrations.CreateModel(
            name='FunctionTypeModel',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='Resource Identifier')),
                ('key', models.CharField(max_length=50, unique=True)),
                ('verbose_name', models.CharField(max_length=50)),
                ('description', models.TextField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('inputs', models.TextField(null=True)),
                ('outputs', models.TextField(null=True)),
                ('account', models.ForeignKey(help_text='The creator and owner of the function.', on_delete=django.db.models.deletion.CASCADE, related_name='function_types', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Function Type',
                'db_table': 'function_types',
                'ordering': ['-created'],
            },
        ),
        migrations.AddField(
            model_name='functioninstancemodel',
            name='function_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='instances', to='streams.functiontypemodel'),
        ),
        migrations.AddField(
            model_name='functioninstancemodel',
            name='stream',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='functions', to='streams.streammodel'),
        ),
        migrations.CreateModel(
            name='FunctionInstanceLogMessageModel',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='Resource Identifier')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('log_message', models.CharField(max_length=500)),
                ('log_level', models.CharField(choices=[('debug', 'Debug'), ('info', 'Info'), ('warning', 'Warning'), ('error', 'Error')], default='info', max_length=50)),
                ('function_instance', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='log_messages', to='streams.functioninstancemodel')),
            ],
            options={
                'verbose_name': 'Function Instance Log Message',
                'db_table': 'function_instance_log_messages',
                'ordering': ['-created'],
            },
        ),
    ]
