from django.db import migrations


def remove_duplicate_suborders(apps, schema_editor):
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("""
            DELETE FROM excavator_excavatorsuborder
            WHERE id NOT IN (
                SELECT (array_agg(id ORDER BY created_at))[1]
                FROM excavator_excavatorsuborder
                GROUP BY parent_id, driver_id
            )
        """)


class Migration(migrations.Migration):

    dependencies = [
        ('excavator', '0015_alter_excavatororder_files_and_more'),
    ]

    operations = [
        migrations.RunPython(remove_duplicate_suborders, migrations.RunPython.noop),
    ]
