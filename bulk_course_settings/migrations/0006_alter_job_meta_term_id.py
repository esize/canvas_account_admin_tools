# Generated by Django 3.2.20 on 2024-01-12 19:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bulk_course_settings', '0005_add_meta_term_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='job',
            name='meta_term_id',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
