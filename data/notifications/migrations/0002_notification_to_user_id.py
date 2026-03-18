from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='to_user_id',
            field=models.UUIDField(blank=True, null=True),
        ),
    ]
