# Generated by Django 4.2.11 on 2024-07-22 00:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_alter_project_reports_p_delete_income_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='total_amount',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10, null=True, verbose_name='Total Amount'),
        ),
        migrations.AlterUniqueTogether(
            name='workrecord',
            unique_together={('employee', 'project', 'date', 'hours')},
        ),
    ]
