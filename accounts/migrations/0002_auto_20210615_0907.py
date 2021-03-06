# Generated by Django 3.1.4 on 2021-06-15 09:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accountmodel',
            name='auth_id',
            field=models.CharField(error_messages={'unique': 'An account with that auth_id already exists.'}, help_text='It is the authentication identifier for login, composed by (organization_slug:username).', max_length=150, unique=True, verbose_name='auth id'),
        ),
    ]
