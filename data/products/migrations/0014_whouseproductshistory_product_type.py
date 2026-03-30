from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0013_remove_whouseproductshistory_wproduct_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="whouseproductshistory",
            name="product_type",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="products.producttype",
            ),
        ),
    ]
