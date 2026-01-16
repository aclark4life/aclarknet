# Generated manually for generic foreign key support

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('contenttypes', '0001_initial'),
        ('db', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='note',
            name='content_type',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to='contenttypes.contenttype',
            ),
        ),
        migrations.AddField(
            model_name='note',
            name='object_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
