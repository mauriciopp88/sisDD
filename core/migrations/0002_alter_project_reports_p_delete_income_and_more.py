# Generated by Django 4.2.11 on 2024-07-02 23:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='reports_p',
            field=models.URLField(blank=True, null=True, verbose_name='Reports'),
        ),
        migrations.DeleteModel(
            name='Income',
        ),
        migrations.DeleteModel(
            name='IncomeType',
        ),
    ]
