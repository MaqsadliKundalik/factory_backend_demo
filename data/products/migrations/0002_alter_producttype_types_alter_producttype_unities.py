from django.db import migrations, models
import django.contrib.postgres.fields

def migrate_data(apps, schema_editor):
    ProductType = apps.get_model('products', 'ProductType')
    for obj in ProductType.objects.all():
        # types and unities are currently jsonb in DB, so obj.types/unities will be lists
        obj.types_new = obj.types if isinstance(obj.types, list) else []
        obj.unities_new = obj.unities if isinstance(obj.unities, list) else []
        obj.save()

class Migration(migrations.Migration):

    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='producttype',
            name='types_new',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=255), blank=True, default=list, size=None),
        ),
        migrations.AddField(
            model_name='producttype',
            name='unities_new',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=255), blank=True, default=list, size=None),
        ),
        migrations.RunPython(migrate_data),
        migrations.RemoveField(
            model_name='producttype',
            name='types',
        ),
        migrations.RemoveField(
            model_name='producttype',
            name='unities',
        ),
        migrations.RenameField(
            model_name='producttype',
            old_name='types_new',
            new_name='types',
        ),
        migrations.RenameField(
            model_name='producttype',
            old_name='unities_new',
            new_name='unities',
        ),
    ]
