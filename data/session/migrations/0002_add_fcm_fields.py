from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('factory_session', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='driversession',
            name='fcm_token',
            field=models.CharField(blank=True, max_length=512, null=True),
        ),
        migrations.AddField(
            model_name='driversession',
            name='fcm_invalid',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='driversession',
            name='last_active',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='factoryusersession',
            name='fcm_token',
            field=models.CharField(blank=True, max_length=512, null=True),
        ),
        migrations.AddField(
            model_name='factoryusersession',
            name='fcm_invalid',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='factoryusersession',
            name='last_active',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
