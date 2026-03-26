from django.db import migrations


def remove_duplicates(apps, schema_editor):
    from django.db import connection
    with connection.cursor() as cursor:
        # Remove duplicate suborders (order_id, driver_id)
        cursor.execute("""
            DELETE FROM orders_suborder
            WHERE id NOT IN (
                SELECT (array_agg(id ORDER BY created_at))[1]
                FROM orders_suborder
                GROUP BY order_id, driver_id
            )
        """)
        # Remove duplicate order items (order_id, product_id, type_id, unit_id)
        cursor.execute("""
            DELETE FROM orders_orderitem
            WHERE id NOT IN (
                SELECT (array_agg(id ORDER BY id::text))[1]
                FROM orders_orderitem
                GROUP BY order_id, product_id, type_id, unit_id
            )
        """)
        # Remove duplicate suborder items (sub_order_id, product_id, type_id, unit_id)
        cursor.execute("""
            DELETE FROM orders_suborderitem
            WHERE id NOT IN (
                SELECT (array_agg(id ORDER BY id::text))[1]
                FROM orders_suborderitem
                GROUP BY sub_order_id, product_id, type_id, unit_id
            )
        """)


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0017_remove_suborder_quantity'),
    ]

    operations = [
        migrations.RunPython(remove_duplicates, migrations.RunPython.noop),
    ]
