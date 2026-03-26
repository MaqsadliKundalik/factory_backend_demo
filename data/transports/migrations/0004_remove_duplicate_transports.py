from django.db import migrations


def remove_duplicates(apps, schema_editor):
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("""
            DELETE FROM transports_transport
            WHERE id NOT IN (
                SELECT (array_agg(id ORDER BY created_at))[1]
                FROM transports_transport
                GROUP BY number, whouse_id
            )
        """)


class Migration(migrations.Migration):

    dependencies = [
        ('transports', '0003_transport_car_type_alter_transport_type'),
    ]

    operations = [
        migrations.RunPython(remove_duplicates, migrations.RunPython.noop),
    ]
