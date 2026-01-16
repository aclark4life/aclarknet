# Generated migration to add start_date and end_date to Invoice model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('db', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='start_date',
            field=models.DateField(blank=True, null=True, verbose_name='Start Date'),
        ),
        migrations.AddField(
            model_name='invoice',
            name='end_date',
            field=models.DateField(blank=True, null=True, verbose_name='End Date'),
        ),
    ]
